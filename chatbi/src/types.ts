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
}

/** 会话栏条目（T2 = 本地态占位；服务端持久化/删除隐藏语义在 T4 接入） */
export interface SessionItem {
  id: number;
  title: string;
  pinned: boolean;
  starred: boolean;
}
