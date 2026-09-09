import { useCallback, useEffect, useRef, useState, type CSSProperties } from 'react';
import { loadProfile, type ProfileBundle } from './api';
import { ChatInput } from './components/ChatInput';
import { MessageCard } from './components/MessageCard';
import { SessionBar } from './components/SessionBar';
import { TraceNotFoundError, useHistory, fetchTrace } from './hooks/useHistory';
import { fetchMessages, NEW_TITLE, useSessions } from './hooks/useSessions';
import { useChatStream, type StreamCallbacks } from './hooks/useChatStream';
import type { ChatMessage, FinalResult, HistoryEntry } from './types';

function userMessage(id: number, text: string): ChatMessage {
  return { id, role: 'user', text, steps: [], streamedText: '', result: null, error: null, phase: 'done' };
}

function aiMessage(id: number, question: string): ChatMessage {
  return { id, role: 'ai', text: question, steps: [], streamedText: '', result: null, error: null, phase: 'streaming' };
}

/** client_request_id：uuid 优先，无 crypto 环境降级随机串（幂等键只要求同次重试一致） */
function newCrid(): string {
  return typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function'
    ? crypto.randomUUID()
    : 'crid-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 10);
}

type ReplayView =
  | { phase: 'loading' }
  | { phase: 'missing' }
  | { phase: 'failed' }
  | { phase: 'ready'; startedAt: string; msg: ChatMessage };

const TAB_STYLE: CSSProperties = { border: 'none', background: 'transparent', padding: '4px 2px', cursor: 'pointer', fontSize: 13 };
const TAB_ACTIVE: CSSProperties = { ...TAB_STYLE, fontWeight: 600, boxShadow: 'inset 0 -2px 0 #333' };

export default function App() {
  const [bundle, setBundle] = useState<ProfileBundle | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [tab, setTab] = useState<'chat' | 'history'>('chat');
  const [replay, setReplay] = useState<ReplayView | null>(null);
  const idSeq = useRef(1);
  const loadSeq = useRef(0); // 会话切换竞态守卫：仅最后一次加载生效
  const activeMsgId = useRef<number | null>(null);
  const msgsRef = useRef<HTMLDivElement | null>(null);

  const {
    sessions, activeId, serverMode, select, create, rename, togglePin, toggleStar, remove,
  } = useSessions();
  const { entries: histEntries, loading: histLoading, error: histError, reload: histReload, remove: histRemove } = useHistory();

  // profile 装配：后端未起 → loadProfile 内部降级 mock 模式
  useEffect(() => {
    void loadProfile().then(setBundle);
  }, []);

  // 新消息自动滚底
  useEffect(() => {
    const el = msgsRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages]);

  // 切会话/刷新恢复：从服务端拉消息流（assistant 用 result 快照渲染，非重新执行）
  useEffect(() => {
    if (!serverMode || !activeId) return;
    const seq = ++loadSeq.current;
    activeMsgId.current = null;
    fetchMessages(activeId)
      .then((restored) => {
        if (seq !== loadSeq.current) return;
        idSeq.current = Math.max(idSeq.current, restored.length + 1);
        setMessages(restored);
      })
      .catch(() => {
        if (seq === loadSeq.current) setMessages([]);
      });
  }, [activeId, serverMode]);

  // 查询历史 tab 打开时刷新列表（§3.1 历史入口在对话区顶部 tab）
  useEffect(() => {
    if (tab === 'history') void histReload();
  }, [tab, histReload]);

  const patchAi = useCallback((fn: (m: ChatMessage) => ChatMessage) => {
    const id = activeMsgId.current;
    if (id == null) return;
    setMessages((ms) => ms.map((m) => (m.id === id ? fn(m) : m)));
  }, []);

  const callbacks: StreamCallbacks = {
    onStep: (s) => patchAi((m) => ({ ...m, steps: [...m.steps, s] })),
    onToken: (t) => patchAi((m) => ({ ...m, streamedText: m.streamedText + t })),
    onFinal: (r) => patchAi((m) => ({ ...m, result: r })),
    onEnded: (why, err) => patchAi((m) => ({ ...m, phase: 'done', endedBy: why, error: err ?? null })),
  };

  const { send, stop, busy } = useChatStream({
    endpoint: bundle?.profile.endpoint ?? '/api/chat',
    mock: bundle?.mockMode ?? true,
    callbacks,
  });

  const handleSend = useCallback(
    (q: string, opts?: { crid?: string }) => {
      if (serverMode && !activeId) return; // 会话未就绪（服务端模式必须归属到会话）
      const crid = opts?.crid ?? newCrid();
      const base = idSeq.current;
      idSeq.current += 2;
      activeMsgId.current = base + 1;
      setMessages((ms) => [...ms, { ...userMessage(base, q), crid }, { ...aiMessage(base + 1, q), crid }]);
      // 首问命名会话（服务端 PATCH + 本地即时反馈由 refresh 收敛）
      const cur = sessions.find((s) => s.id === activeId);
      if (cur && cur.title === NEW_TITLE) rename(cur.id, q.slice(0, 18)).catch(console.error);
      send(q, {
        conversationId: serverMode && activeId ? activeId : undefined,
        clientRequestId: crid,
      });
    },
    [serverMode, activeId, sessions, rename, send],
  );

  // 历史回放：点击历史条目 → GET /api/trace/{rid} → 快照渲染为消息卡（标注数据截至时间）
  const openReplay = useCallback(async (entry: HistoryEntry) => {
    setReplay({ phase: 'loading' });
    try {
      const trace: FinalResult = await fetchTrace(entry.request_id);
      setReplay({
        phase: 'ready',
        startedAt: trace.started_at || entry.started_at,
        msg: {
          id: 0, role: 'ai', text: trace.question,
          steps: trace.steps ?? [], streamedText: '', result: trace,
          error: null, phase: 'done', endedBy: 'final',
        },
      });
    } catch (err) {
      setReplay(err instanceof TraceNotFoundError ? { phase: 'missing' } : { phase: 'failed' });
    }
  }, []);

  const deleteSession = (id: string) => {
    if (!window.confirm('删除该会话？删除后会话与对应查询历史均不再显示（审计数据物理保留）。')) return;
    remove(id).catch(console.error);
  };

  const renameSession = (id: string) => {
    const cur = sessions.find((s) => s.id === id);
    const t = window.prompt('重命名会话', cur?.title ?? '');
    if (t && t.trim()) rename(id, t.trim()).catch(console.error);
  };

  const togglePinSession = (id: string) => togglePin(id).catch(console.error);
  const toggleStarSession = (id: string) => toggleStar(id).catch(console.error);
  const newSession = () => create().catch(console.error);

  const profile = bundle?.profile;
  const ready = bundle != null;

  const historyPanel = (
    <div style={{ flex: 1, overflowY: 'auto', padding: '8px 16px' }}>
      {(replay == null || replay.phase !== 'ready') && (
        <button style={{ ...TAB_STYLE, color: '#555' }} onClick={() => setReplay(null)}>← 返回历史列表</button>
      )}
      {replay?.phase === 'loading' && <div className="empty">回放加载中…</div>}
      {replay?.phase === 'missing' && <div className="empty">该条记录已删除或不存在，无法回放。</div>}
      {replay?.phase === 'failed' && <div className="empty">回放加载失败，请稍后重试。</div>}
      {replay?.phase === 'ready' && (
        <>
          <div style={{ margin: '8px 0', padding: '6px 10px', background: '#f5f5f5', borderRadius: 6, fontSize: 13, color: '#555' }}>
            历史回放 · 数据截至 {replay.startedAt.replace('T', ' ')}（快照渲染，不随数据变更）
          </div>
          <MessageCard
            msg={replay.msg}
            pathLabels={profile?.path_labels ?? {}}
            onRetry={(q) => { setTab('chat'); handleSend(q); }}
            onFollowUp={(q) => { setTab('chat'); handleSend(q); }}
          />
        </>
      )}
      {(replay == null || replay.phase === 'loading') && (
        <>
          {histLoading && <div className="empty">加载中…</div>}
          {histError && <div className="empty">{histError}</div>}
          {!histLoading && !histError && histEntries.length === 0 && <div className="empty">暂无查询历史。</div>}
          {histEntries.map((e) => (
            <div
              key={e.request_id}
              style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 4px', borderBottom: '1px solid #eee', cursor: 'pointer' }}
              onClick={() => void openReplay(e)}
            >
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 13, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{e.question}</div>
                <div style={{ fontSize: 12, color: '#888' }}>
                  {(e.started_at || '').replace('T', ' ')} · {e.request_id}
                </div>
              </div>
              <button
                className="opbtn"
                title="删除该条历史"
                onClick={(ev) => {
                  ev.stopPropagation();
                  if (window.confirm('删除该条查询历史？删除后不可再回放（审计数据物理保留）。')) histRemove(e.request_id).catch(console.error);
                }}
              >
                🗑
              </button>
            </div>
          ))}
        </>
      )}
    </div>
  );

  return (
    <>
      <header>
        <h1>{profile?.display ?? 'ChatBI'}</h1>
        <span>· 每个回答都给出决策过程、依据与数据</span>
        {bundle?.mockMode && <span className="mockflag">mock 数据</span>}
      </header>
      <div className="layout">
        <SessionBar
          sessions={sessions}
          activeId={activeId}
          onSelect={select}
          onNew={newSession}
          onRename={renameSession}
          onTogglePin={togglePinSession}
          onToggleStar={toggleStarSession}
          onDelete={deleteSession}
        />
        <main className="main">
          <div style={{ display: 'flex', gap: 12, padding: '6px 16px', borderBottom: '1px solid #eee' }}>
            <button style={tab === 'chat' ? TAB_ACTIVE : TAB_STYLE} onClick={() => setTab('chat')}>对话</button>
            <button style={tab === 'history' ? TAB_ACTIVE : TAB_STYLE} onClick={() => setTab('history')}>查询历史</button>
          </div>
          {tab === 'chat' ? (
            <>
              <div className="msgs" ref={msgsRef}>
                {messages.length === 0 && (
                  <div className="emptywrap">
                    <div className="empty">
                      {ready ? (bundle.mockMode ? 'mock 数据模式：试试示例问题（八状态关键字见 README）' : '试试示例问题，或直接输入') : '业务档案装配中…'}
                    </div>
                    <div className="chips">
                      {(profile?.examples ?? []).map((ex) => (
                        <button key={ex} disabled={!ready || busy} onClick={() => handleSend(ex)}>
                          {ex}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
                {messages.map((m) =>
                  m.role === 'user' ? (
                    <div key={m.id} className="m user">
                      <div className="bub">{m.text}</div>
                    </div>
                  ) : (
                    <MessageCard
                      key={m.id}
                      msg={m}
                      pathLabels={profile?.path_labels ?? {}}
                      onRetry={(q) => handleSend(q, m.crid ? { crid: m.crid } : undefined)}
                      onFollowUp={handleSend}
                    />
                  ),
                )}
              </div>
              <ChatInput busy={busy} ready={ready} onSend={handleSend} onStop={stop} />
            </>
          ) : (
            historyPanel
          )}
        </main>
      </div>
    </>
  );
}
