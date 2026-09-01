// 风险读侧 API（S4 M3a 契约，只消费不改后端）
// - GET /api/risk/dashboard        全局督办看板聚合
// - GET /api/risk/reporting/draft  监管报送初稿（红色预警，query 参数）
// 响应统一信封 { outcome, data, error }；vite 代理剥离 /api 前缀 → 后端 /risk/...。
import type { ZhWarnLevel } from './warnLevel';

// ---------------------------------------------------------------------------
// /risk/dashboard
// ---------------------------------------------------------------------------
export interface DashboardCapital {
  group_consolidated_capital_yi: number;
  bank_net_capital_yi: number;
  bank_tier1_capital_yi: number;
  bank_internal_limit_yi: number;
  concern_line: number;
  warn_line: number;
  internal_limit_ratio: number;
}

export interface ConcentrationRank {
  rank: number;
  group_customer_no: string;
  group_customer_name: string;
  consolidated_balance_yi: number;
  concentration_ratio: number;
  latest_warn_level: string | null;
  latest_signal_status: string | null;
  signal_count: number;
}

export interface Overdue {
  pending_confirm_overdue: number;
  in_disposal_overdue: number;
  cutoff_date: string;
}

export interface SubsidiaryResponse {
  org_name: string;
  open_signal_count: number;
  avg_open_age_days: number;
  completed_disposal_count: number;
  avg_disposal_days: number;
}

export interface RiskDashboard {
  as_of_date: string;
  capital: DashboardCapital;
  overdue_days_threshold: number;
  group_concentration_ranking: ConcentrationRank[];
  signal_status_distribution: Record<string, number>;
  overdue: Overdue;
  subsidiary_response: SubsidiaryResponse[];
}

// ---------------------------------------------------------------------------
// /risk/reporting/draft
// ---------------------------------------------------------------------------
export interface DraftBreakdownItem {
  org_name: string;
  balance_yi: number;
  reference_denom_yi?: number;
  org_reference_ratio?: number;
}

export interface HiddenRelatedParty {
  customer_name: string;
  balance_yi: number;
  relation_clues: string[];
}

export interface ReportingDraft {
  report_title: string;
  generated_at: string;
  warning: {
    warning_id: string;
    signal_id: string;
    warn_level: string;
    signal_status: string;
    warn_reason: string;
  };
  group_customer: { group_customer_no: string; group_customer_name: string };
  consolidated_exposure: {
    own_balance_yi: number;
    hidden_related_party_balance_yi: number;
    total_balance_yi: number;
    group_consolidated_capital_yi: number;
    concentration_ratio: number;
    ratio_display: string;
  };
  breakdown: DraftBreakdownItem[];
  hidden_related_parties: HiddenRelatedParty[];
  trigger_rules: { rule: string; name: string; basis: string; lines?: string; desc?: string }[];
  regulatory_basis: { article: string; text: string }[];
}

interface Envelope<T> {
  outcome: 'ok' | 'error';
  data?: T;
  error?: { code: string; message: string };
}

async function getEnvelope<T>(url: string): Promise<Envelope<T>> {
  const res = await fetch(url, { headers: { 'Content-Type': 'application/json' } });
  let body: Envelope<T>;
  try {
    body = (await res.json()) as Envelope<T>;
  } catch {
    throw new Error('HTTP ' + res.status + ': 响应不是合法 JSON');
  }
  if (!res.ok || body.outcome !== 'ok' || body.data === undefined) {
    throw new Error(body.error?.message ?? 'HTTP ' + res.status);
  }
  return body;
}

export async function fetchRiskDashboard(overdueDays = 30): Promise<RiskDashboard> {
  const env = await getEnvelope<RiskDashboard>('/api/risk/dashboard?overdue_days=' + overdueDays);
  return env.data as RiskDashboard;
}

export async function fetchReportingDraft(groupCustomerNo: string): Promise<ReportingDraft> {
  const env = await getEnvelope<ReportingDraft>(
    '/api/risk/reporting/draft?group_customer_no=' + encodeURIComponent(groupCustomerNo),
  );
  return env.data as ReportingDraft;
}

// 工具：把后端预警级别字符串归一到中文枚举（后端已是中文；兜底映射）
export function toZhWarnLevel(v: string | null | undefined): ZhWarnLevel | null {
  if (v === '黄' || v === '橙' || v === '红') return v;
  if (v === 'YELLOW') return '黄';
  if (v === 'ORANGE') return '橙';
  if (v === 'RED') return '红';
  return null;
}

// 工具：百分比数字 → "10.8%"（避免浮点尾巴）
export function pctOf(ratio: number): string {
  return (ratio * 100).toFixed(1) + '%';
}
