// 对话引擎 —— 本地 state + 固定剧本流式模拟（无后端；docs/chat-ux-spec-v1.md §7.2/§8）
import { useCallback, useEffect, useRef, useState } from 'react';
import { SESSIONS } from '../proto/fakeData';
import { FULL_SEED_QUESTION, SCRIPTS, TOOL_STEPS_VIEW, matchScript, matchScriptInContext, type AiScript } from './scriptData';

// —— 时序常量（spec §5.4/§5.5/§8.1/§8.2）——
const THINK_SKELETON_MS = 800; // >800ms 出骨架（§8.2）
const THINK_HINT_MS = 8000; // >8s 追加「正在核对口径与阈值…」（§8.2）
const BLOCK_GAP_MS = 160;
const REPORT_SKELETON_MS = 800; // 报告生成中骨架（§5.4）
const TOOL_SKELETON_MS = 400; // tools 骨架先行（§5.5）
const TOOL_STEP_MS = [600, 700, 500]; // 三步合计 1.8s，与 TOOLS_SUMMARY 口径一致
const ERROR_EXTRA_MS = 500;

export type BlockPhase = 'skeleton' | 'running' | 'done';

export interface AiBlockState {
  key: string;
  type: 'tools' | 'text' | 'table' | 'chart' | 'report' | 'confirm';
  /** text 块已流式输出部分 / 全量 */
  md?: string;
  mdFull?: string;
  toolsPhase?: BlockPhase;
  stepStatus?: ('process' | 'finish')[];
  reportPhase?: 'skeleton' | 'done';
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'ai';
  text?: string;
  time: string;
  status: 'thinking' | 'streaming' | 'done' | 'error';
  blocks: AiBlockState[];
  /** 原问题（复制/重试/重新生成用） */
  question?: string;
  attempt: number;
  errorReason?: string;
  scriptId?: string;
  /** §8.2 >8s 提示行 */
  thinkingHint?: boolean;
}

export interface ChatSession {
  key: string;
  label: string;
  messages: ChatMessage[];
}

let seq = 0;
const nextId = () => `m${++seq}`;
let blkSeq = 0;
const nextBlk = () => `b${++blkSeq}`;
const hhmm = () => {
  const d = new Date();
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
};

function staticBlock(b: AiScript['blocks'][number]): AiBlockState {
  if (b.type === 'text') return { key: nextBlk(), type: 'text', md: b.md, mdFull: b.md };
  if (b.type === 'tools')
    return { key: nextBlk(), type: 'tools', toolsPhase: 'done', stepStatus: TOOL_STEPS_VIEW.map(() => 'finish') };
  if (b.type === 'report') return { key: nextBlk(), type: 'report', reportPhase: 'done' };
  return { key: nextBlk(), type: b.type };
}

function initialSessions(): ChatSession[] {
  return [
    {
      key: 's1',
      label: SESSIONS[0].label,
      messages: [
        { id: nextId(), role: 'user', text: FULL_SEED_QUESTION, time: hhmm(), status: 'done', blocks: [], attempt: 1 },
        {
          id: nextId(),
          role: 'ai',
          time: hhmm(),
          status: 'done',
          blocks: SCRIPTS.full.blocks.map(staticBlock),
          attempt: 1,
          scriptId: 'full',
        },
      ],
    },
    { key: 's2', label: SESSIONS[1].label, messages: [] },
    { key: 's3', label: SESSIONS[2].label, messages: [] },
  ];
}

export function useChatEngine() {
  const [sessions, setSessions] = useState<ChatSession[]>(initialSessions);
  const [currentKey, setCurrentKey] = useState('s1');
  const [version, setVersion] = useState(0);
  const [generating, setGenerating] = useState<Record<string, boolean>>({});
  const sessionsRef = useRef(sessions);
  useEffect(() => {
    sessionsRef.current = sessions;
  }, [sessions]);
  const generatingRef = useRef<Record<string, boolean>>({});
  const genTokens = useRef(new Map<string, { cancelled: boolean }>());

  const bump = () => setVersion((v) => v + 1);

  const patchSession = useCallback((key: string, fn: (s: ChatSession) => ChatSession) => {
    setSessions((prev) => prev.map((s) => (s.key === key ? fn(s) : s)));
    bump();
  }, []);

  const patchMessage = useCallback(
    (sessionKey: string, msgId: string, fn: (m: ChatMessage) => ChatMessage) => {
      patchSession(sessionKey, (s) => ({
        ...s,
        messages: s.messages.map((m) => (m.id === msgId ? fn(m) : m)),
      }));
    },
    [patchSession],
  );

  const setGen = (key: string, on: boolean) => {
    generatingRef.current = { ...generatingRef.current, [key]: on };
    setGenerating(generatingRef.current);
  };

  const finishGen = useCallback(
    (sessionKey: string) => {
      genTokens.current.delete(sessionKey);
      setGen(sessionKey, false);
    },
    [],
  );

  const runScript = useCallback(
    (sessionKey: string, question: string, script: AiScript, attempt: number, errorMode: boolean) => {
      const msgId = nextId();
      const token = { cancelled: false };
      genTokens.current.set(sessionKey, token);
      setGen(sessionKey, true);
      const alive = () => !token.cancelled;
      const sleep = (ms: number) => new Promise<void>((r) => setTimeout(r, ms));

      patchSession(sessionKey, (s) => ({
        ...s,
        messages: [
          ...s.messages,
          { id: msgId, role: 'ai', time: hhmm(), status: 'thinking', blocks: [], question, attempt, scriptId: script.id },
        ],
      }));

      const pushBlock = (b: AiBlockState) =>
        patchMessage(sessionKey, msgId, (m) => ({ ...m, blocks: [...m.blocks, b] }));
      const patchLast = (fn: (b: AiBlockState) => AiBlockState) =>
        patchMessage(sessionKey, msgId, (m) => ({
          ...m,
          blocks: m.blocks.map((b, i) => (i === m.blocks.length - 1 ? fn(b) : b)),
        }));

      void (async () => {
        // §8.2：>800ms 出骨架（thinking 态 UI 由 MessageItem 渲染骨架）
        await sleep(THINK_SKELETON_MS);
        if (!alive()) return;
        const hintTimer = setTimeout(() => {
          if (alive()) patchMessage(sessionKey, msgId, (m) => ({ ...m, thinkingHint: true }));
        }, Math.max(THINK_HINT_MS - THINK_SKELETON_MS, 0));
        await sleep(Math.max(script.thinkMs - THINK_SKELETON_MS, 50));
        clearTimeout(hintTimer);
        if (!alive()) return;

        // 错误态（§8.3）：仅 fallback 剧本首次触发；重试后成功
        if (errorMode) {
          await sleep(ERROR_EXTRA_MS);
          if (!alive()) return;
          patchMessage(sessionKey, msgId, (m) => ({ ...m, status: 'error', errorReason: '网络超时，请稍后重试（模拟场景）' }));
          finishGen(sessionKey);
          return;
        }

        patchMessage(sessionKey, msgId, (m) => ({ ...m, status: 'streaming' }));

        for (const b of script.blocks) {
          if (!alive()) return;
          if (b.type === 'tools') {
            pushBlock({ key: nextBlk(), type: 'tools', toolsPhase: 'skeleton', stepStatus: [] });
            await sleep(TOOL_SKELETON_MS);
            if (!alive()) return;
            patchLast((bl) => ({ ...bl, toolsPhase: 'running', stepStatus: ['process'] }));
            for (let s = 0; s < TOOL_STEPS_VIEW.length; s++) {
              await sleep(TOOL_STEP_MS[s]);
              if (!alive()) return;
              patchLast((bl) => {
                const st = [...(bl.stepStatus ?? [])];
                st[s] = 'finish';
                if (s + 1 < TOOL_STEPS_VIEW.length) st[s + 1] = 'process';
                return { ...bl, stepStatus: st };
              });
            }
            patchLast((bl) => ({ ...bl, toolsPhase: 'done' }));
            await sleep(BLOCK_GAP_MS);
          } else if (b.type === 'text') {
            // 打字机由 @ant-design/x TypingContent 驱动（§8.1 内置能力），文本块一次性全量下发；
            // 引擎仅按同速率（step 2 / interval 24ms ≈ 12ms/字符）等待，保证下一块在文本打完后再出现
            pushBlock({ key: nextBlk(), type: 'text', md: b.md, mdFull: b.md });
            await sleep(b.md.length * 12 + 250);
            if (!alive()) return;
          } else if (b.type === 'report') {
            pushBlock({ key: nextBlk(), type: 'report', reportPhase: 'skeleton' });
            await sleep(REPORT_SKELETON_MS);
            if (!alive()) return;
            patchLast((bl) => ({ ...bl, reportPhase: 'done' }));
            await sleep(BLOCK_GAP_MS);
          } else {
            pushBlock({ key: nextBlk(), type: b.type });
            await sleep(BLOCK_GAP_MS);
          }
        }
        if (!alive()) return;
        patchMessage(sessionKey, msgId, (m) => ({ ...m, status: 'done' }));
        finishGen(sessionKey);
      })();
    },
    [finishGen, patchMessage, patchSession],
  );

  const sendMessage = useCallback(
    (sessionKey: string, raw: string, attempt = 1) => {
      const text = raw.trim().slice(0, 500);
      if (!text || generatingRef.current[sessionKey]) return; // 生成中 Enter 不发送（§7.2）
      const userMsg: ChatMessage = { id: nextId(), role: 'user', text, time: hhmm(), status: 'done', blocks: [], attempt };
      patchSession(sessionKey, (s) => ({ ...s, messages: [...s.messages, userMsg] }));
      // 多轮上下文（批 2）：按本会话最近一条 AI 剧本解析追问（如触达 → 分母），否则走基础路由
      const lastAiScriptId = sessionsRef.current
        .find((x) => x.key === sessionKey)
        ?.messages.filter((m) => m.role === 'ai')
        .at(-1)?.scriptId;
      const script = matchScriptInContext(text, lastAiScriptId);
      const errorMode = script.id === 'fallback' && attempt === 1;
      runScript(sessionKey, text, script, attempt, errorMode);
    },
    [patchSession, runScript],
  );

  /** §8.3 重试：移除错误卡并重发原问题（重试后成功） */
  const retry = useCallback(
    (sessionKey: string, messageId: string) => {
      if (generatingRef.current[sessionKey]) return;
      const s = sessionsRef.current.find((x) => x.key === sessionKey);
      const target = s?.messages.find((m) => m.id === messageId);
      if (!target) return;
      patchSession(sessionKey, (cur) => ({ ...cur, messages: cur.messages.filter((m) => m.id !== messageId) }));
      const script = SCRIPTS[target.scriptId ?? ''] ?? matchScript(target.question ?? '');
      runScript(sessionKey, target.question ?? '', script, target.attempt + 1, false);
    },
    [patchSession, runScript],
  );

  /** §4.4 重新生成：重发原问题 */
  const regenerate = useCallback(
    (sessionKey: string, messageId: string) => {
      if (generatingRef.current[sessionKey]) return;
      const s = sessionsRef.current.find((x) => x.key === sessionKey);
      const target = s?.messages.find((m) => m.id === messageId && m.role === 'ai');
      if (!target?.question) return;
      sendMessage(sessionKey, target.question, target.attempt + 1);
    },
    [sendMessage],
  );

  /** §7.2 停止：打断流式，保留已输出内容 */
  const stopGenerate = useCallback(
    (sessionKey: string) => {
      const token = genTokens.current.get(sessionKey);
      if (!token) return;
      token.cancelled = true;
      finishGen(sessionKey);
      const s = sessionsRef.current.find((x) => x.key === sessionKey);
      const live = s?.messages.find((m) => m.role === 'ai' && (m.status === 'thinking' || m.status === 'streaming'));
      if (live) patchMessage(sessionKey, live.id, (m) => ({ ...m, status: 'done' }));
    },
    [finishGen, patchMessage],
  );

  const newSession = useCallback(() => {
    const key = `n${Date.now()}`;
    setSessions((prev) => [...prev, { key, label: '新对话', messages: [] }]);
    setCurrentKey(key);
  }, []);

  return {
    sessions,
    currentKey,
    version,
    generating,
    selectSession: setCurrentKey,
    newSession,
    sendMessage,
    stopGenerate,
    retry,
    regenerate,
  };
}