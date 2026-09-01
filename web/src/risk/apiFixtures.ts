// 测试用 API 响应夹具（/risk/dashboard 与 /risk/reporting/draft），
// 结构对齐后端 src/api/risk_reporting.py 真实返回（口径：天晟 10.8% / 12.8%、瑞华 9.4%）。
import type { RiskDashboard, ReportingDraft } from './riskApi';

export const dashboardFixture: RiskDashboard = {
  as_of_date: '2026-12-31',
  capital: {
    group_consolidated_capital_yi: 800,
    bank_net_capital_yi: 600,
    bank_tier1_capital_yi: 480,
    bank_internal_limit_yi: 60,
    concern_line: 0.09,
    warn_line: 0.1,
    internal_limit_ratio: 0.12,
  },
  overdue_days_threshold: 30,
  group_concentration_ranking: [
    { rank: 1, group_customer_no: 'GRP-2026-900001', group_customer_name: '天晟集团有限公司', consolidated_balance_yi: 86.4, concentration_ratio: 0.108, latest_warn_level: '橙', latest_signal_status: '处置中', signal_count: 3 },
    { rank: 2, group_customer_no: 'GRP-2026-900002', group_customer_name: '瑞华能源集团有限公司', consolidated_balance_yi: 75.2, concentration_ratio: 0.094, latest_warn_level: '黄', latest_signal_status: '已关闭', signal_count: 2 },
    { rank: 3, group_customer_no: 'GRP-2026-900003', group_customer_name: '中科智造产业发展集团', consolidated_balance_yi: 40.8, concentration_ratio: 0.051, latest_warn_level: '黄', latest_signal_status: '已确认', signal_count: 1 },
  ],
  signal_status_distribution: {
    待确认: 5934,
    确认中: 4023,
    已确认: 4006,
    处置中: 3093,
    已关闭: 1977,
    已撤销: 560,
    已排除: 410,
  },
  overdue: { pending_confirm_overdue: 128, in_disposal_overdue: 45, cutoff_date: '2026-12-01' },
  subsidiary_response: [
    { org_name: '安平银行', open_signal_count: 132, avg_open_age_days: 18.6, completed_disposal_count: 88, avg_disposal_days: 21.4 },
    { org_name: '安平证券', open_signal_count: 97, avg_open_age_days: 12.3, completed_disposal_count: 61, avg_disposal_days: 16.2 },
    { org_name: '安平资产管理', open_signal_count: 55, avg_open_age_days: 9.8, completed_disposal_count: 40, avg_disposal_days: 13.5 },
  ],
};

export const reportingDraftFixture: ReportingDraft = {
  report_title: '大额风险暴露口径监管报送初稿',
  generated_at: '2026-12-31T08:00:00Z',
  data_as_of: '2026-12-31',
  warning: {
    warning_id: 'WS-2026-90000002',
    signal_id: 'SIG-2026-90000002',
    warn_level: '红',
    signal_status: '处置中',
    warn_reason: '纳入隐性关联方后归集集中度 12.8% 突破内部限额',
  },
  group_customer: { group_customer_no: 'GRP-2026-900001', group_customer_name: '天晟集团有限公司' },
  consolidated_exposure: {
    own_balance_yi: 86.4,
    hidden_related_party_balance_yi: 16.0,
    total_balance_yi: 102.4,
    group_consolidated_capital_yi: 800,
    concentration_ratio: 0.128,
    ratio_display: '12.8%',
  },
  breakdown: [
    { org_name: '安平银行', balance_yi: 48, reference_denom_yi: 600, org_reference_ratio: 0.08 },
    { org_name: '安平证券', balance_yi: 22, reference_denom_yi: 400, org_reference_ratio: 0.055 },
    { org_name: '安平资产管理', balance_yi: 16.4, reference_denom_yi: 200, org_reference_ratio: 0.082 },
  ],
  hidden_related_parties: [
    {
      customer_name: '恒昌贸易有限公司',
      balance_yi: 16,
      relation_clues: [
        '股权代持线索：恒昌贸易大股东张伟与天晟实业存在股权代持关系（登记股东名义持股 35%，实控人系天晟方一致行动人）',
        '交叉担保链：恒昌贸易与天晟系企业互为担保人，交叉担保余额合计约 12 亿元，担保圈可闭环追溯',
        '资金往来异动：近 6 个月恒昌贸易与天晟系资金往来净额显著上升至约 8.6 亿元，超出历史均值 3 倍',
      ],
    },
  ],
  trigger_rules: [
    { rule: 'R1a', name: '集团层归集集中度', basis: '金控办法第三十二/三十三条（安平内部口径）', lines: '关注 9% / 预警 10% / 内部限额 12%' },
    { rule: 'R2', name: '关联客户组归集', basis: '2018 办法附件 1 + 金控办法第三十三条', desc: '经联合授信识别隐性关联/一致行动人后纳入归集，按 R1a 重算' },
  ],
  regulatory_basis: [
    { article: '2018 办法第三十七条', text: '第三十七条 商业银行突破大额风险暴露监管要求的，应立即报告银行业监督管理机构。' },
    { article: '2018 办法第三十四条', text: '第三十四条 银行业监督管理机构定期评估商业银行大额风险暴露管理状况及效果，包括制度执行、系统建设、限额遵守、风险管控等，将评估意见反馈商业银行董事会和高级管理层，并将评估结果作为监管评级的重要参考。' },
  ],
};

export const okJson = (body: unknown) => Promise.resolve({ ok: true, json: () => Promise.resolve(body) });
