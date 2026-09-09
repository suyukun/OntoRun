import { useCallback, useEffect, useRef, useState } from 'react';
import { loadProfile, type ProfileBundle } from './api';
import { ChatInput } from './components/ChatInput';
import { MessageCard } from './components/MessageCard';
import { SessionBar } from './components/SessionBar';
import { useChatStream, type StreamCallbacks } from './hooks/useChatStream';
import type { ChatMessage, SessionItem } from './types';

function userMessage(id: number, text: string): ChatMessage {
  return { id, role: 'user', text, steps: [], streamedText: '', result: null, error: null, phase: 'streaming' };
}

function aiMessage(id: number, question: string): ChatMessage {
  return { id, role: 'ai', text: question, steps: [], streamedText: '', result: null, error: null, phase: 'streaming' };
}

export default function App() {
  const [bundle, setBundle] = useState<ProfileBundle | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessions, setSessions] = useState<SessionItem[]>([{ id: 1, title: '新对话', pinned: false, starred: false }]);
  const [activeSession, setActiveSession] = useState(1);
  const idSeq = useRef(2); // 1 已被初始会话占用
  const activeMsgId = useRef<number | null>(null);
  const msgsRef = useRef<HTMLDivElement | null>(null);

  // profile 装配：后端未起 → loadProfile 内部降级 mock 模式
  useEffect(() => {
    void loadProfile().then(setBundle);
  }, []);

  // 新消息自动滚底
  useEffect(() => {
    const el = msgsRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages]);

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
    (q: string) => {
      const base = idSeq.current;
      idSeq.current += 2;
      activeMsgId.current = base + 1;
      setMessages((ms) => [...ms, userMessage(base, q), aiMessage(base + 1, q)]);
      // 首问命名会话（占位；正式命名策略随 T4）
      setSessions((ss) => ss.map((s) => (s.id === activeSession && s.title === '新对话' ? { ...s, title: q.slice(0, 18) } : s)));
      send(q);
    },
    [activeSession, send],
  );

  const renameSession = (id: number) => {
    const cur = sessions.find((s) => s.id === id);
    const t = window.prompt('重命名会话', cur?.title ?? '');
    if (t && t.trim()) setSessions((ss) => ss.map((s) => (s.id === id ? { ...s, title: t.trim() } : s)));
  };

  const togglePin = (id: number) => setSessions((ss) => ss.map((s) => (s.id === id ? { ...s, pinned: !s.pinned } : s)));
  const toggleStar = (id: number) => setSessions((ss) => ss.map((s) => (s.id === id ? { ...s, starred: !s.starred } : s)));

  const newSession = () => {
    const s: SessionItem = { id: idSeq.current++, title: '新对话', pinned: false, starred: false };
    setSessions((ss) => [...ss, s]);
    setActiveSession(s.id);
    setMessages([]);
  };

  const selectSession = (id: number) => {
    if (id === activeSession) return;
    setActiveSession(id);
    setMessages([]); // T2 骨架：会话内容暂不持久（服务端持久化/历史回放在 T4）
  };

  const deleteSession = (id: number) => {
    if (!window.confirm('删除该会话？删除后对您隐藏（审计数据物理保留——删除隐藏语义在 T4 接入）。')) return;
    const rest = sessions.filter((s) => s.id !== id);
    const next: SessionItem[] = rest.length > 0 ? rest : [{ id: idSeq.current++, title: '新对话', pinned: false, starred: false }];
    setSessions(next);
    if (id === activeSession) {
      setActiveSession(next[0].id);
      setMessages([]);
    }
  };

  const profile = bundle?.profile;
  const ready = bundle != null;

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
          activeId={activeSession}
          onSelect={selectSession}
          onNew={newSession}
          onRename={renameSession}
          onTogglePin={togglePin}
          onToggleStar={toggleStar}
          onDelete={deleteSession}
        />
        <main className="main">
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
                <MessageCard key={m.id} msg={m} pathLabels={profile?.path_labels ?? {}} onRetry={handleSend} onFollowUp={handleSend} />
              ),
            )}
          </div>
          <ChatInput busy={busy} ready={ready} onSend={handleSend} onStop={stop} />
        </main>
      </div>
    </>
  );
}
