// Backend API client + types mirroring src/fortune_admin payloads.

export type RuleStatus = "unverified" | "confirmed";

// T501 数字目录：数字卡版本行（口径锚规则 + 最新确认状态摘要；取不到如实 null）。
export interface MeasureCaliber {
  rule_id: string;
  status: RuleStatus;
  code: string | null;
  confirmer: string | null;
  time: string | null;
  commit: string | null;
  /** 最新记录可能是驳回（confirmed | rejected）；无记录为 null，不冒充确认。 */
  verdict: string | null;
}

export interface Measure {
  id: string;
  description: string;
  expression: string;
  source_table: string;
  source_alias: string;
  time_field: string;
  filters: string[];
  /** T501 增量可选字段：后端现值恒带；可选以保持既有夹具向后兼容。 */
  domain?: string | null;
  domain_name?: string | null;
  caliber?: MeasureCaliber | null;
}

export interface JoinSpec {
  table: string;
  alias: string;
  on: string;
  select_columns: string[];
  snapshot_policy: string;
  snapshot_column: string;
}

export interface Dimension {
  id: string;
  description: string;
  expression: string;
  join: JoinSpec | null;
  grains: Record<string, string> | null;
}

export interface ConfirmRecord {
  rule_id: string;
  verdict: string;
  confirmer: string;
  code: string;
  time: string;
  commit: string | null;
  mode: string;
}

export interface DivergenceOption {
  key: string;
  label: string;
  value_evidence: string;
  applies_to: string;
}

export interface Decision {
  option_key: string;
  decided_by: string;
  time: string;
  commit: string;
}

export interface CaliberRule {
  id: string;
  description: string;
  source_script: string;
  status: RuleStatus;
  related_tables: string[];
  last_record: ConfirmRecord | null;
  divergence?: DivergenceOption[] | null;
  decision?: Decision | null;
}

export interface Ontology {
  measures: Measure[];
  dimensions: Dimension[];
  rules: CaliberRule[];
  summary: {
    measures: number;
    dimensions: number;
    rules: number;
    pending: number;
    confirmed: number;
  };
}

export interface LineageNode {
  id: string;
  label: string;
  layer: string;
  unconfirmed: boolean;
}

export interface LineageEdge {
  source: string;
  target: string;
  via_script: string;
  unconfirmed: boolean;
}

export interface Lineage {
  nodes: LineageNode[];
  edges: LineageEdge[];
  layers: Record<string, { color: string; label: string }>;
  stats: { nodes: number; edges: number; unconfirmed_edges: number };
}

export type ObjectKind = "measure" | "dimension" | "table";

export interface ObjectDetail {
  kind: ObjectKind;
  id: string;
  description: string;
  layer: string | null;
  unconfirmed: boolean;
  definition: {
    expression?: string;
    source_table?: string;
    source_alias?: string;
    time_field?: string;
    filters?: string[];
    join?: JoinSpec | null;
    grains?: Record<string, string> | null;
    bound_measures?: { id: string; description: string }[];
    bound_dimensions?: { id: string; description: string }[];
  };
  rules: CaliberRule[];
  upstream: LineageEdge[];
  downstream: LineageEdge[];
}

export interface HistoryCommit {
  short: string;
  author: string;
  time: string;
  human: string;
  subject: string;
}

export interface HistoryPayload {
  commits: HistoryCommit[];
  count: number;
}

export type DecisionOptionKey = "account" | "user" | "both" | "escalate";

export interface TrialResult {
  rule_id: string;
  month: string;
  value: number;
  unit: string;
  generated_at: string;
  source: "semantic_query" | "cache";
}

export interface ConfirmBody {
  verdict: string;
  confirmeer: string;
  decision?: { option_key: DecisionOptionKey };
}

async function getJson<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url} -> HTTP ${res.status}`);
  return res.json();
}

export const api = {
  ontology: () => getJson<Ontology>("/api/ontology"),
  lineage: () => getJson<Lineage>("/api/lineage"),
  objectDetail: (kind: ObjectKind, id: string) =>
    getJson<ObjectDetail>(`/api/objects/${kind}/${encodeURIComponent(id)}`),
  history: (limit: number) => getJson<HistoryPayload>(`/api/history?limit=${limit}`),
  // decision 可选（T203 R8 裁决）：带 decision:{option_key} 时后端按裁决处理
  // （account/user/both=三选一落 confirmed；escalate=只留痕不翻转，A4-7）。
  confirmRule: async (
    ruleId: string,
    verdict: string,
    confirmeer: string,
    decision?: { option_key: DecisionOptionKey }
  ) => {
    const res = await fetch(`/api/rules/${ruleId}/confirm`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        verdict,
        confirmeer,
        ...(decision ? { decision } : {}),
      }),
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`HTTP ${res.status}: ${text}`);
    }
    return res.json() as Promise<{ record: ConfirmRecord; message: string }>;
  },
};
