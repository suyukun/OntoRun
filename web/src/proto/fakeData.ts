// 共享假数据 —— 两个原型页同源，保证对决公平
export const SESSIONS = [
  { key: 's1', label: '天晟集团风险归集' },
  { key: 's2', label: '瑞华能源黄档解除' },
  { key: 's3', label: '000098 勾稽质询' },
];

export const REVEAL_TEXT =
  '逐家单看都安全：银行 8.0%（行内限额内）、证券 5.5%（触达参考线）、资管 8.2%（触达参考线）。' +
  '归集 86.4 亿 ÷ 并表资本 800 亿 = **10.8% ≥ 预警线 10%** → 橙色预警（R1a）。';

export const TABLE_ROWS = [
  { org: '安平银行', exposure: '48.0 亿', ratio: '8.0%', ref: '行内限额', level: '安全' },
  { org: '安平证券', exposure: '22.0 亿', ratio: '5.5%', ref: '参考线 5.5%', level: '触达' },
  { org: '安平资管', exposure: '16.4 亿', ratio: '8.2%', ref: '参考线 8.2%', level: '触达' },
  { org: '归集（R1a）', exposure: '86.4 亿', ratio: '10.8%', ref: '预警线 10%', level: '橙色预警' },
];

export const ECHOPT = {
  tooltip: { trigger: 'axis' as const },
  grid: { left: 40, right: 16, top: 30, bottom: 28 },
  xAxis: {
    type: 'category' as const,
    data: ['安平银行', '安平证券', '安平资管', '归集'],
    axisLabel: { interval: 0, fontSize: 11, hideOverlap: false },
  },
  yAxis: { type: 'value' as const, axisLabel: { formatter: '{value}%' } },
  series: [
    {
      type: 'bar' as const,
      name: '占比',
      data: [
        { value: 8.0, itemStyle: { color: '#52c41a' } },
        { value: 5.5, itemStyle: { color: '#52c41a' } },
        { value: 8.2, itemStyle: { color: '#52c41a' } },
        { value: 10.8, itemStyle: { color: '#fa8c16' } },
      ],
      barWidth: 28,
    },
  ],
};

export const TOOL_STEPS = [
  { title: 'risk_group_reveal', description: 'GRP-2026-900001 · ap_group_customer × ap_concentration_limit', status: 'finish' as const },
  { title: '勾稽对账', description: '明细外部 86.4 + 内部抵销 0.0 = 台账归集 86.4 ✓', status: 'finish' as const },
  { title: 'R1a 定级', description: '阈值 base.ap_sys_param.CAP_WARN_LINE=10%（金控办法 32/33 自设，安平风管部 2025-06-30 批）', status: 'process' as const },
];

export const CONFIRM = {
  title: 'AI 提议 · 冻结天晟集团新增授信',
  reason: 'R1a 归集 10.8% ≥ 预警线 10%（处置依据：2023 关联交易办法第二十三条）',
  appliedReply: '已执行 · 源库写回 ✓ · 审计 #A-1024',
};

export const EVIDENCE = {
  tables: ['ap_group_customer', 'ap_concentration_limit', 'base.ap_sys_param'],
  rules: ['R1a 归集集中度', 'R1b 机构参考线'],
  denominator: '集团并表资本 800 亿（CAP_GROUP_CONSOLIDATED）',
  audit: '#A-1024',
};
