/** 契约类型 —— 事件/result 结构对齐产品设计 v0.2 附录 A 与 demo semantic_layer.iter_query。 */

export interface StepInfo {
  n: number;
  title: string;
  status: 'ok' | 'fail' | 'blocked';
  detail: string;
  sql?: string;
  ms?: number;
}

export interface TableRef {
  name: string;
  layer: string;
}

/** D7：规则注册的 viz 字段（产品文档 §5-D7，与 rules.py 单一来源对齐） */
export type VizKind = 'bar' | 'line' | 'pie' | 'table' | 'kpi';

export interface FinalResult {
  request_id: string;
  started_at: string;
  question: string;
  rule: string | null;
  path: string;
  answer: string;
  sql: string | null;
  rows: Record<string, unknown>[];
  tables: TableRef[];
  steps: StepInfo[];
  /** §4.2：blocked_param 拆分为参数追问/范围超限两态，按结构化字段区分（非 answer 文案猜） */
  block_reason?: 'missing_param' | 'out_of_range';
  /** D7 viz 契约：图表类型由语义层规则注册声明（与数据形态绑定）；缺省/未支持类型一律表格渲染 */
  viz?: VizKind;
  /** §4.2 2b：LLM 路由降级为关键词匹配时的降级标记 */
  degraded?: boolean;
}

export interface StreamError {
  code: string;
  message: string;
}

export type ChatEvent =
  | { kind: 'step'; step: StepInfo }
  | { kind: 'token'; text: string }
  | { kind: 'final'; result: FinalResult }
  | { kind: 'error'; code: string; message: string };

/** 附录 C profile schema（壳所需字段子集） */
export interface Profile {
  name: string;
  display: string;
  endpoint: string;
  panels: string[];
  examples: string[];
  path_labels: Record<string, string>;
}

/** 流终局原因：final 正常 / error 帧 / 用户取消 / 断流中断 */
export type EndReason = 'final' | 'error' | 'canceled' | 'interrupted';

export interface ChatMessage {
  id: number;
  role: 'user' | 'ai';
  /** user 消息 = 用户输入；ai 消息 = 本次回答对应的问题 */
  text: string;
  steps: StepInfo[];
  streamedText: string;
  result: FinalResult | null;
  error: StreamError | null;
  phase: 'streaming' | 'done';
  endedBy?: EndReason;
  /** client_request_id：重试复用同 id，后端幂等回放不产生重复 trace（附录 A） */
  crid?: string;
}

export interface HistoryEntry {
  request_id: string;
  started_at: string;
  question: string;
  path: string | null;
  state: string | null;
  answer: string;
}

/** 服务端会话条目（GET /api/sessions 原始契约；pinned/starred 为 0/1） */
export interface ServerSession {
  id: string;
  title: string;
  pinned: number | boolean;
  starred: number | boolean;
  created_at: string;
  updated_at: string;
}

/** 服务端消息（GET /api/sessions/{id} 契约；assistant 消息带完整 result 快照，恢复=快照渲染非重新执行） */
export interface ServerMessage {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  question: string | null;
  request_id: string | null;
  state: string | null;
  answer: string | null;
  result: FinalResult | null;
  created_at: string;
}

/** 会话栏条目（T4：服务端 /api/sessions 为唯一事实源；后端未起时本地降级，仍走同结构） */
export interface SessionItem {
  id: string;
  title: string;
  pinned: boolean;
  starred: boolean;
}
