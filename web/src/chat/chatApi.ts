// 真实问数链路客户端（批 3，chat-ux-spec v1.2）：/agent/risk/chat 契约 + 数据源模式解析
// 后端一次性响应；流式/骨架 UX 由前端本地播放（spec §8，时序语义不变，内容全真）。

export interface EvidenceRulesHit {
  rule?: string;
  name?: string;
  clause?: string;
  lines?: string;
  computed?: Record<string, unknown>;
  [k: string]: unknown;
}

export interface EvidenceBlock {
  intent?: string;
  conclusion?: string;
  basis_tables?: string[];
  rules_hits?: EvidenceRulesHit[];
  denominator?: { name?: string; value_yi?: number; source?: string } | null;
  detail_rows?: Record<string, unknown>[];
  [k: string]: unknown;
}

export interface NeedConfirm {
  id: string;
  name: string;
  arguments: Record<string, unknown>;
}

export interface ChatApiResponse {
  session_id: string;
  reply: string;
  need_confirm: NeedConfirm | null;
  outcome: string | null;
  evidence: EvidenceBlock[] | null;
}

export type ChatMode = 'fake' | 'live';

let modeOverride: ChatMode | null = null;
/** 测试专用：强制数据源模式（优先级最高） */
export function setChatModeOverride(m: ChatMode | null) {
  modeOverride = m;
}

/** 模式解析：测试覆盖 > URL ?src= > VITE_CHAT_DATA_SOURCE > fake（默认安全） */
export function resolveChatMode(): ChatMode {
  if (modeOverride) return modeOverride;
  const p = new URLSearchParams(window.location.search).get('src');
  if (p === 'live' || p === 'fake') return p;
  const env = String(import.meta.env.VITE_CHAT_DATA_SOURCE ?? '').toLowerCase();
  return env === 'live' ? 'live' : 'fake';
}

export type StreamEvent =
  | { type: 'token'; text: string }
  | { type: 'tool_start'; name: string }
  | { type: 'tool_result'; name: string; outcome: string }
  | ({ type: 'final' } & ChatApiResponse)
  | { type: 'error'; message: string };

/** SSE 流式对话（批 4-②）：逐帧回调，final 帧兑现完整响应。HTTP 非 200 或断流抛错。 */
export async function streamRiskChat(
  message: string,
  sessionId: string | undefined,
  onEvent: (ev: StreamEvent) => void,
  signal?: AbortSignal,
): Promise<ChatApiResponse> {
  const res = await fetch('/api/agent/risk/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Actor': 'human' },
    body: JSON.stringify(sessionId ? { message, session_id: sessionId } : { message }),
    signal,
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  if (!res.body) throw new Error('empty-stream');
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = '';
  let final: ChatApiResponse | null = null;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    let idx: number;
    while ((idx = buf.indexOf('\n\n')) !== -1) {
      const frame = buf.slice(0, idx);
      buf = buf.slice(idx + 2);
      for (const line of frame.split('\n')) {
        if (!line.startsWith('data:')) continue;
        const ev = JSON.parse(line.slice(5)) as StreamEvent;
        if (ev.type === 'final') {
          final = { session_id: ev.session_id, reply: ev.reply, need_confirm: ev.need_confirm, outcome: ev.outcome, evidence: ev.evidence };
          onEvent(ev);
        } else {
          onEvent(ev);
        }
      }
    }
  }
  if (!final) throw new Error('stream-incomplete');
  return final;
}

// —— 图表派生（c4 chip）：从揭示载荷 detail_rows / rules_hits.computed 派生柱状系列，不手写数字 ——
export interface ChartSeriesItem {
  org: string;
  /** 百分数值（如 10.8 表示 10.8%） */
  ratio: number;
  /** 机构自身参考线（百分数）；无参考线为 null */
  refRatio: number | null;
  /** 集团归集行（对照 R1a 三线） */
  isGroup: boolean;
}

export function chartSeriesFromEvidence(evs: EvidenceBlock[]): ChartSeriesItem[] | null {
  const items: ChartSeriesItem[] = [];
  for (const e of evs) {
    for (const r of e.detail_rows ?? []) {
      if (typeof r.org_name !== 'string' || typeof r.ratio_display !== 'string') continue;
      const ratio = Number.parseFloat(r.ratio_display);
      if (!Number.isFinite(ratio)) continue;
      const ref =
        typeof r.org_reference_ratio === 'number' && Number.isFinite(r.org_reference_ratio)
          ? r.org_reference_ratio * 100
          : null;
      items.push({ org: r.org_name, ratio, refRatio: ref, isGroup: false });
    }
    for (const h of e.rules_hits ?? []) {
      const c = h.computed;
      if (c && typeof c.ratio === 'number' && h.rule === 'R1a') {
        items.push({ org: '集团归集', ratio: c.ratio * 100, refRatio: null, isGroup: true });
      }
    }
  }
  return items.length > 0 ? items : null;
}

/** tools 块步骤文案：intent → 可读步骤（内容来自真实载荷，映射仅做展示转写） */
export function intentLabel(intent: string): string {
  if (intent.startsWith('risk_query:')) return `实查 ${intent.slice('risk_query:'.length)}`;
  const known: Record<string, string> = {
    act1_group_reveal: '第 1 幕 · 逐家归集揭示',
    act2_related_reveal: '第 2 幕 · 关联升级识别',
    act4_approval_chain: '第 4 幕 · 处置审批链',
    verify_reason: '实查标红/橙原因维度',
  };
  return known[intent] ?? intent;
}