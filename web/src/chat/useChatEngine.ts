// 对话引擎 —— fake=本地剧本流式模拟；live=真实问数（/agent/risk/chat，批 3）
// 流式/骨架 UX 两模式一致：后端一次性响应由前端本地播放（docs/chat-ux-spec-v1.md §7.2/§8）
import { useCallback, useEffect, useRef, useState } from 'react';
import { SESSIONS } from '../proto/fakeData';
import {
  chartSeriesFromEvidence,
  intentLabel,
  resolveChatMode,
  sendRiskChat,
  type ChartSeriesItem,
  type ChatMode,
  type EvidenceBlock,
  type NeedConfirm,
} from './chatApi';
import { FULL_SEED_QUESTION, SCRIPTS, TOOL_STEPS_VIEW, matchScript, matchScriptInContext, type AiScript } from './scriptData';

// —— 时序常量（spec §5.4/§5.5/§8.1/§8.2）——
const THINK_SKELETON_MS = 800; // >800ms 出骨架（§8.2）
const THINK_HINT_MS = 8000; // >8s 追加「正在核对口径与阈值…」（§8.2）
const BLOCK_GAP_MS = 160;
const REPORT_SKELETON_MS = 800; // 报告生成中骨架（§5.4）
const TOOL_SKELETON_MS = 400; // tools 骨架先行（§5.5）
const TOOL_STEP_MS = [600, 700, 500]; // 三步合计 1.8s，与 TOOLS_SUMMARY 口径一致
const ERROR_EXTRA_MS = 500;
// live 模式时序：真实等待即思考态；载荷到位后快速回放过程与文本
const LIVE_MIN_THINK_MS = 800; // 骨架最短停留（§8.2）
const LIVE_TOOL_STEP_MS = 180; // 证据 intent 步骤回放间隔
const LIVE_TEXT_WAIT_CAP_MS = 6000; // 长回答不阻塞后续块（文本打字机继续）

export type BlockPhase = 'skeleton' | 'running' | 'done';

export interface AiBlockState {
  key: string;
  type: 'tools' | 'text' | 'table' | 'chart' | 'report' | 'confirm';
  /** text 块已流式输出部分 / 全量 */
  md?: string;
  mdFull?: string;
  toolsPhase?: BlockPhase;
  stepStatus?: ('process' | 'finish')[];
  /** live：tools 步骤文案（来自真实证据 intent） */
  stepLabels?: string[];
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
  /** live：思考阶段（1 理解问题 / 2 检索数据 / 3 核对口径），驱动阶段化提示文案 */
  thinkingStage?: 1 | 2 | 3;
  /** live：本条回答的数据源模式与真实载荷（证据抽屉/图表/confirm 消费） */
  mode?: ChatMode;
  evidence?: EvidenceBlock[];
  needConfirm?: NeedConfirm;
  chartSeries?: ChartSeriesItem[] | null;
}

export interface ChatSession {
  key: string;
  label: string;
  messages: ChatMessage[];
  /** live：后端会话 id（多轮上下文由后端 RiskAgent 会话承载） */
  remoteId?: string;
  /** 批 4：置顶（展示时排前，插入序内稳定） */
  pinned?: boolean;
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
  // live（批 3.1）：会话列表真实化——只出一个空会话，提问后自动命名；不预置 fake 剧本条目
  if (resolveChatMode() === 'live') {
    return [{ key: 's1', label: '新对话', messages: [] }];
  }
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
  const genTokens = useRef(new Map<string, { cancelled: boolean; ac?: AbortController }>());

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

  // —— live（批 3）：真实问数 —— 等待即思考态，载荷到位后回放过程块 + 文本（内容全真）
  const runLive = useCallback(
    (sessionKey: string, question: string, attempt: number) => {
      const msgId = nextId();
      const ac = new AbortController();
      const token = { cancelled: false, ac };
      genTokens.current.set(sessionKey, token);
      setGen(sessionKey, true);
      const alive = () => !token.cancelled;
      const sleep = (ms: number) => new Promise<void>((r) => setTimeout(r, ms));

      patchSession(sessionKey, (s) => ({
        ...s,
        messages: [
          ...s.messages,
          { id: msgId, role: 'ai', time: hhmm(), status: 'thinking', blocks: [], question, attempt, mode: 'live' },
        ],
      }));

      const pushBlock = (b: AiBlockState) =>
        patchMessage(sessionKey, msgId, (m) => ({ ...m, blocks: [...m.blocks, b] }));
      const patchLast = (fn: (b: AiBlockState) => AiBlockState) =>
        patchMessage(sessionKey, msgId, (m) => ({
          ...m,
          blocks: m.blocks.map((b, i) => (i === m.blocks.length - 1 ? fn(b) : b)),
        }));
      // 阶段化思考提示（批 3.1）：只轮换进行时措辞，绝不虚构中间结果
      const stageTimers = [
        setTimeout(() => {
          if (alive()) patchMessage(sessionKey, msgId, (m) => ({ ...m, thinkingStage: 2 }));
        }, 2500),
        setTimeout(() => {
          if (alive()) patchMessage(sessionKey, msgId, (m) => ({ ...m, thinkingStage: 3, thinkingHint: true }));
        }, THINK_HINT_MS),
      ];
      const clearStageTimers = () => stageTimers.forEach(clearTimeout);

      void (async () => {
        const remoteId = sessionsRef.current.find((x) => x.key === sessionKey)?.remoteId;
        try {
          const t0 = sleep(LIVE_MIN_THINK_MS);
          const res = await sendRiskChat(question, remoteId, ac.signal);
          await t0;
          clearStageTimers();
          if (!alive()) return;
          // 首答自动命名（批 3.1）：'新对话' → 问题前 12 字（真实会话列表）
          patchSession(sessionKey, (s) => ({
            ...s,
            remoteId: res.session_id,
            label: s.label === '新对话' ? question.slice(0, 12) : s.label,
          }));

          const evidence = res.evidence ?? [];
          patchSession(sessionKey, (s) => ({
            ...s,
            messages: s.messages.map((m) =>
              m.id === msgId
                ? { ...m, status: 'streaming', evidence, needConfirm: res.need_confirm ?? undefined }
                : m,
            ),
          }));

          // 过程透明（§5.5）：步骤 = 真实证据 intent，快速回放
          if (evidence.length > 0) {
            const labels = evidence.slice(0, 6).map((e) => intentLabel(String(e.intent ?? '实查')));
            pushBlock({ key: nextBlk(), type: 'tools', toolsPhase: 'running', stepStatus: ['process'], stepLabels: labels });
            for (let i = 0; i < labels.length; i++) {
              await sleep(LIVE_TOOL_STEP_MS);
              if (!alive()) return;
              patchLast((bl) => {
                const st = [...(bl.stepStatus ?? [])];
                st[i] = 'finish';
                if (i + 1 < labels.length) st[i + 1] = 'process';
                return { ...bl, stepStatus: st };
              });
            }
            patchLast((bl) => ({ ...bl, toolsPhase: 'done' }));
            await sleep(BLOCK_GAP_MS);
            if (!alive()) return;
          }

          // 回答正文（Markdown 全量下发，TypingContent 打字机；等待仅排后续块，长文封顶）
          patchMessage(sessionKey, msgId, (m) => ({
            ...m,
            blocks: [...m.blocks, { key: nextBlk(), type: 'text', md: res.reply, mdFull: res.reply }],
          }));
          await sleep(Math.min(res.reply.length * 12, LIVE_TEXT_WAIT_CAP_MS) + 250);
          if (!alive()) return;

          // 画图类提问且载荷含占比行 → 从真实证据派生图（不手写数字）；触发词放宽（批 4-①）
          const wantChart = /画一张|画个|画图|柱状图|饼图|对比图|可视化|图表/.test(question);
          const series = chartSeriesFromEvidence(evidence);
          if (wantChart && series) {
            patchMessage(sessionKey, msgId, (m) => ({ ...m, chartSeries: series }));
            pushBlock({ key: nextBlk(), type: 'chart' });
            await sleep(BLOCK_GAP_MS);
            if (!alive()) return;
          }

          // 写提议（§5.6）：need_confirm 随答返回 → confirm 卡；批 3 拍板不接写回
          if (res.need_confirm) {
            pushBlock({ key: nextBlk(), type: 'confirm' });
            await sleep(BLOCK_GAP_MS);
            if (!alive()) return;
          }

          patchMessage(sessionKey, msgId, (m) => ({ ...m, status: 'done' }));
          finishGen(sessionKey);
        } catch (err) {
          clearStageTimers();
          if (!alive() || (err instanceof DOMException && err.name === 'AbortError')) {
            // §7.2 停止：打断等待，保留已输出内容
            patchMessage(sessionKey, msgId, (m) => (m.status === 'thinking' ? { ...m, status: 'done' } : m));
            finishGen(sessionKey);
            return;
          }
          patchMessage(sessionKey, msgId, (m) => ({
            ...m,
            status: 'error',
            errorReason:
              err instanceof Error && err.message.startsWith('HTTP')
                ? '风险问答服务异常，请稍后重试'
                : '网络异常，无法连接风险问答服务',
          }));
          finishGen(sessionKey);
        }
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
      if (resolveChatMode() === 'live') {
        runLive(sessionKey, text, attempt);
        return;
      }
      // 多轮上下文（批 2）：按本会话最近一条 AI 剧本解析追问（如触达 → 分母），否则走基础路由
      const lastAiScriptId = sessionsRef.current
        .find((x) => x.key === sessionKey)
        ?.messages.filter((m) => m.role === 'ai')
        .at(-1)?.scriptId;
      const script = matchScriptInContext(text, lastAiScriptId);
      const errorMode = script.id === 'fallback' && attempt === 1;
      runScript(sessionKey, text, script, attempt, errorMode);
    },
    [patchSession, runLive, runScript],
  );

  /** §8.3 重试：移除错误卡并重发原问题（重试后成功） */
  const retry = useCallback(
    (sessionKey: string, messageId: string) => {
      if (generatingRef.current[sessionKey]) return;
      const s = sessionsRef.current.find((x) => x.key === sessionKey);
      const target = s?.messages.find((m) => m.id === messageId);
      if (!target) return;
      patchSession(sessionKey, (cur) => ({ ...cur, messages: cur.messages.filter((m) => m.id !== messageId) }));
      if (target.mode === 'live') {
        runLive(sessionKey, target.question ?? '', target.attempt + 1);
        return;
      }
      const script = SCRIPTS[target.scriptId ?? ''] ?? matchScript(target.question ?? '');
      runScript(sessionKey, target.question ?? '', script, target.attempt + 1, false);
    },
    [patchSession, runLive, runScript],
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
      token.ac?.abort();
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

  // —— 会话管理（批 4）：删除 / 重命名 / 置顶 ——
  const deleteSession = useCallback(
    (key: string) => {
      if (generatingRef.current[key]) return; // 生成中不可删
      const prev = sessionsRef.current;
      const idx = prev.findIndex((s) => s.key === key);
      if (idx === -1) return;
      const rest = prev.filter((s) => s.key !== key);
      const next = rest.length ? rest : [{ key: `n${Date.now()}`, label: '新对话', messages: [] }];
      setSessions(next);
      if (currentKey === key) setCurrentKey(next[Math.max(0, Math.min(idx - 1, next.length - 1))].key);
      bump();
    },
    [currentKey],
  );

  const renameSession = useCallback(
    (key: string, raw: string) => {
      const label = raw.trim().slice(0, 20);
      if (!label) return;
      patchSession(key, (s) => ({ ...s, label }));
    },
    [patchSession],
  );

  const togglePin = useCallback(
    (key: string) => {
      patchSession(key, (s) => ({ ...s, pinned: !s.pinned }));
    },
    [patchSession],
  );

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
    deleteSession,
    renameSession,
    togglePin,
  };
}