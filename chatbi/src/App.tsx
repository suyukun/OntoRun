import { useCallback, useEffect, useRef, useState } from 'react';
import { loadProfile, type ProfileBundle } from './api';
import { DEMO_PACING_ENABLED } from './config';
import { ChatInput } from './components/ChatInput';
import { InsightCard, loadInsights } from './components/InsightCard';
import { MessageCard } from './components/MessageCard';
import { SessionBar } from './components/SessionBar';
import { fetchMessages, NEW_TITLE, useSessions } from './hooks/useSessions';
import { useChatStream, type StreamCallbacks } from './hooks/useChatStream';
import type { ChatMessage, InsightItem } from './types';

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

/** 滚动条距底阈值（px）：仅当用户停在底部附近时才自动跟随（UX：不劫持上翻回看） */
const NEAR_BOTTOM_PX = 80;

export default function App() {
  const [bundle, setBundle] = useState<ProfileBundle | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [insights, setInsights] = useState<InsightItem[]>([]);
  const idSeq = useRef(1);
  const loadSeq = useRef(0); // 会话切换竞态守卫：仅最后一次加载生效
  const activeMsgId = useRef<number | null>(null);
  const msgsRef = useRef<HTMLDivElement | null>(null);
  const nearBottom = useRef(true);

  const {
    sessions, archivedSessions, activeId, serverMode,
    select, create, rename, togglePin, toggleStar, archive, restore, remove,
  } = useSessions();

  // profile 装配：后端未起 → loadProfile 内部降级 mock 模式
  useEffect(() => {
    void loadProfile().then(setBundle);
  }, []);

  // T-U2 主动洞察：打开页拉一次；无命中/失败 → 空数组（常用查询兜底，不出卡）
  useEffect(() => {
    void loadInsights().then(setInsights);
  }, []);

  // 跟随滚动：仅当用户停在消息区底部附近时新消息才自动滚底（上翻回看不被打断）
  useEffect(() => {
    const el = msgsRef.current;
    if (!el) return;
    const onScroll = () => {
      nearBottom.current = el.scrollHeight - el.scrollTop - el.clientHeight < NEAR_BOTTOM_PX;
    };
    el.addEventListener('scroll', onScroll, { passive: true });
    return () => el.removeEventListener('scroll', onScroll);
  }, []);

  useEffect(() => {
    const el = msgsRef.current;
    if (el && nearBottom.current) el.scrollTop = el.scrollHeight;
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
    pacing: DEMO_PACING_ENABLED, // US3/NC-U4：演示节奏开关（config.ts，演示默认开）
    callbacks,
  });

  const handleSend = useCallback(
    (q: string, opts?: { crid?: string }) => {
      if (serverMode && !activeId) return; // 会话未就绪（服务端模式必须归属到会话）
      const crid = opts?.crid ?? newCrid();
      const base = idSeq.current;
      idSeq.current += 2;
      activeMsgId.current = base + 1;
      nearBottom.current = true; // 用户主动发问 → 视角切回底部
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

  const deleteSession = (id: string) => {
    if (!window.confirm('删除该会话？删除后不可恢复（审计数据物理保留）。')) return;
    remove(id).catch(console.error);
  };

  const renameSession = (id: string) => {
    const cur = sessions.find((s) => s.id === id) ?? archivedSessions.find((s) => s.id === id);
    const t = window.prompt('重命名会话', cur?.title ?? '');
    if (t && t.trim()) rename(id, t.trim()).catch(console.error);
  };

  const togglePinSession = (id: string) => togglePin(id).catch(console.error);
  const toggleStarSession = (id: string) => toggleStar(id).catch(console.error);
  const archiveSession = (id: string) => archive(id).catch(console.error);
  const restoreSession = (id: string) => restore(id).catch(console.error);
  const newSession = () => create().catch(console.error);

  const profile = bundle?.profile;
  const ready = bundle != null;

  return (
    <>
      <header>
        <h1>{profile?.display ?? '财富ThoughtSpot'}</h1>
        <span>有过程 · 有依据 · 可溯源</span>
        {bundle?.mockMode && <span className="mockflag">mock 数据</span>}
      </header>
      <div className="layout">
        <SessionBar
          sessions={sessions}
          archivedSessions={archivedSessions}
          activeId={activeId}
          onSelect={select}
          onNew={newSession}
          onRename={renameSession}
          onTogglePin={togglePinSession}
          onToggleStar={toggleStarSession}
          onArchive={archiveSession}
          onRestore={restoreSession}
          onDelete={deleteSession}
        />
        <main className="main">
          <div className="msgs" ref={msgsRef}>
            {messages.length === 0 && insights.length > 0 && (
              <InsightCard insights={insights} onAsk={handleSend} />
            )}
            {messages.length === 0 && (
              <div className="emptywrap">
                <div className="empty">
                  {ready ? (bundle.mockMode ? '内置演示数据：试试示例问题，或直接输入' : '试试示例问题，或直接输入') : '业务档案装配中…'}
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
                  examples={profile?.examples ?? []}
                  onRetry={(q) => handleSend(q, m.crid ? { crid: m.crid } : undefined)}
                  onFollowUp={handleSend}
                />
              ),
            )}
          </div>
          <ChatInput busy={busy} ready={ready} onSend={handleSend} onStop={stop} />
        </main>
      </div>
    </>
  );
}
