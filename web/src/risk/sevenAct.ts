// 七幕剧本演示数据源（口径包 v0.3 §五/§七）—— 演示「道具」常量与监管条款文案的单一事实来源。
// 数字 = Jack 拍板种子常量（§八）：并表资本 800 亿；天晟 48/22/16.4 → 86.4 亿 → 10.8% 橙；
// +恒昌 16 亿 → 102.4 亿 → 12.8% 红。恒昌三线索文本 = ap_customer_relation_tree.clear_remark_*
// 再生库实测值（customer.db，RT-2026-900001/2/3），与后端 /risk/reporting/draft 同源。
// 监管条款：2023 金控关联交易办法第二十三条（gov.cn 原文）；2018 办法 37/34（与后端 ARTICLE_* 同源）。

import type { ZhWarnLevel } from './warnLevel';

// ---------------------------------------------------------------------------
// 第 1 幕 · 揭示（天晟集团逐家 → 合计 10.8% 橙）
// ---------------------------------------------------------------------------
export interface InstitutionExposure {
  org: string;
  balanceYi: number;
  ratioPct: number;
  denominatorYi: number;
  refLine: string; // 参考线/限额文案（「单看都安全」的依据）
}

export const TIANSHENG: {
  name: string;
  groupNo: string;
  capitalYi: number;
  institutions: InstitutionExposure[];
  consolidatedYi: number;
  ratioPct: number;
  level: ZhWarnLevel;
  ruleBasis: string;
} = {
  name: '天晟集团有限公司',
  groupNo: 'GRP-2026-900001',
  capitalYi: 800,
  institutions: [
    { org: '安平银行', balanceYi: 48, ratioPct: 8.0, denominatorYi: 600, refLine: '行内内部限额 60 亿' },
    { org: '安平证券', balanceYi: 22, ratioPct: 5.5, denominatorYi: 400, refLine: '参考线 5.5%' },
    { org: '安平资产管理', balanceYi: 16.4, ratioPct: 8.2, denominatorYi: 200, refLine: '参考线 8.2%' },
  ],
  consolidatedYi: 86.4,
  ratioPct: 10.8,
  level: '橙',
  ruleBasis: 'R1a 集团层归集集中度 ≥ 预警线 10%（金控办法第三十二/三十三条 · 安平内部口径）',
};

// ---------------------------------------------------------------------------
// 第 2 幕 · 升级识别（恒昌贸易三线索 → 12.8% 红）
// ---------------------------------------------------------------------------
export interface RelationClue {
  key: string;
  title: string;
  source: string; // 数据来源（真表字段）
  text: string; // 再生库实测值（ap_customer_relation_tree.clear_remark_*）
}

export const HENGCHANG_CLUES: RelationClue[] = [
  {
    key: 'equity',
    title: '股权代持线索',
    source: '工商信息 · clear_remark_1',
    text: '恒昌贸易大股东张伟与天晟实业存在股权代持关系（登记股东名义持股 35%，实控人系天晟方一致行动人）',
  },
  {
    key: 'guarantee',
    title: '交叉担保链',
    source: '征信系统 · clear_remark_2',
    text: '恒昌贸易与天晟系企业互为担保人，交叉担保余额合计约 12 亿元，担保圈可闭环追溯',
  },
  {
    key: 'capital',
    title: '资金往来异动',
    source: '行内监测 · clear_remark_3',
    text: '近 6 个月恒昌贸易与天晟系资金往来净额显著上升至约 8.6 亿元，超出历史均值 3 倍',
  },
];

export const HENGCHANG_TRADE: {
  name: string;
  balanceYi: number;
  relationTreeIds: string[];
  relationTreeTable: string;
} = {
  name: '恒昌贸易有限公司',
  balanceYi: 16,
  relationTreeIds: ['RT-2026-900001', 'RT-2026-900002', 'RT-2026-900003'],
  relationTreeTable: 'ap_customer_relation_tree',
};

export const TIANSHENG_ESCALATED: {
  consolidatedYi: number;
  ratioPct: number;
  level: ZhWarnLevel;
  ruleBasis: string;
  note: string;
} = {
  consolidatedYi: 102.4,
  ratioPct: 12.8,
  level: '红',
  ruleBasis: 'R2 关联客户组归集（股权链+担保链+资金往来三线索交叉）→ 按 R1a 重算 > 内部限额 12%',
  note: '这条线传统关联交易表里查不出来——只有把三张底层证据链交叉起来才能认定。',
};

// ---------------------------------------------------------------------------
// 第 4 幕 · 双签驳回（AI 提议 → 审批人按 2023 办法第二十三条驳回）
// ---------------------------------------------------------------------------
export const AI_SPLIT_PROPOSAL: {
  action: string;
  title: string;
  summary: string;
  args: { label: string; value: string }[];
  issue: string;
} = {
  action: 'dispose_split_channel',
  title: 'AI 提议：将天晟部分授信拆分至非关联第三方通道主体',
  summary: '将天晟 24 亿元授信拆分为 4 笔、经两家非关联通道主体发放，使名义归集集中度降至 9.8%，不再超预警线。',
  args: [
    { label: '拆分金额', value: '24 亿元（4 笔 × 6 亿）' },
    { label: '通道主体', value: '2 家非关联第三方' },
    { label: '目标名义集中度', value: '9.8%（< 预警线 10%）' },
  ],
  issue: '表面上压降了名义集中度——实为规避归集监测的合规腾挪。',
};

// 2023 金控关联交易办法第二十三条（中国人民银行令〔2023〕第 1 号，gov.cn 原文）
export const REG_2023_ARTICLE_23_3 = {
  ref: '2023 金融控股公司关联交易办法 第二十三条（三）',
  text:
    '通过隐匿关联关系、拆分交易、设计复杂交易结构等各种隐蔽方式规避内部审查、外部监管以及报告披露义务，' +
    '为关联方违规提供融资、隐藏风险等。',
  note: '审批人驳回：AI 提议不得执行，退回重新起草。',
};

// ---------------------------------------------------------------------------
// 第 5 幕 · 监管动作（报送初稿 + 银团压降计划）
// ---------------------------------------------------------------------------
export const REPORTING_RED_WARNING_ID = 'WS-2026-90000002'; // 天晟红色预警（口径包§七 第 2/5 幕）

// 2018 办法（银保监会令 2018 年第 1 号）依据条款（与后端 src/api/risk_reporting.py 同源）
export const REG_2018_ARTICLE_37 =
  '第三十七条 商业银行突破大额风险暴露监管要求的，应立即报告银行业监督管理机构。';
export const REG_2018_ARTICLE_34 =
  '第三十四条 银行业监督管理机构定期评估商业银行大额风险暴露管理状况及效果，包括制度执行、系统建设、限额遵守、风险管控等，将评估意见反馈商业银行董事会和高级管理层，并将评估结果作为监管评级的重要参考。';

export const SYNDICATED_REDUCTION_PLAN: {
  title: string;
  steps: string[];
  note: string;
} = {
  title: '银团 / 联合贷款压降计划（2018 办法第三十七条 · 2003 指引第十二条）',
  steps: [
    '立即报告监管：红色预警触发即报告银行业监督管理机构',
    '组建银团：将单一银行敞口置换为银团贷款，分散单家机构风险暴露',
    '联合贷款：引入联合授信成员行分担，逐步压降至内部限额 12% 以内',
    '按月催办：处置期间不解除月度督办汇报，压降进度逐月跟踪',
  ],
  note: '现实压降周期通常数月——系统按月催办、全程留痕。',
};

// ---------------------------------------------------------------------------
// 第 6 幕 · 闭环 + 全局（瑞华黄档案例常量 + 看板说明）
// ---------------------------------------------------------------------------
export const RUIHUA_YELLOW_CASE: {
  name: string;
  ratioPct: number;
  level: ZhWarnLevel;
  chain: string[];
  closing: string;
} = {
  name: '瑞华能源集团有限公司',
  ratioPct: 9.4,
  level: '黄',
  chain: ['黄色预警生成', '确认 + 定级', '处置方案（追加担保 · 压降敞口）', '双签审批', '解除 + 解除报告'],
  closing: '完整解除关闭闭环：close_warning + 解除报告，全链路可回放。',
};

export const BOARD_CLOSING_LINE =
  '检查组来了一键调档——每一步谁批的、依据什么，说得清；全程 audit 可回放。';

// ---------------------------------------------------------------------------
// 第 0 幕 · 现状对照（静态文案）
// ---------------------------------------------------------------------------
export const MANUAL_WORKFLOW_STEPS: string[] = [
  '等 3 家附属机构报送台账',
  'Excel 手工对账、跨行核对',
  '翻股权图谱人工查关联',
  '汇总算归集集中度',
  '人工比对限额、起草报告',
];
export const MANUAL_RESULT = '一轮下来，一周。';
export const NOW_RESULT = '现在，一句话。';

// ---------------------------------------------------------------------------
// 七幕剧本目录（演示 stepper 使用；数据源同一处，避免分散）
// ---------------------------------------------------------------------------
export interface ActMeta {
  no: string;
  name: string;
  short: string;
}
export const ACTS: ActMeta[] = [
  { no: '0', name: '现状对照', short: '一周 → 一句话' },
  { no: '1', name: '揭示', short: '逐家 → 10.8% 橙' },
  { no: '2', name: '升级识别', short: '三线索 → 12.8% 红' },
  { no: '3', name: '后果链', short: '处置 · 督办 · 立项' },
  { no: '4', name: '双签驳回', short: '人拦 AI' },
  { no: '5', name: '监管动作', short: '报送初稿 + 压降' },
  { no: '6', name: '闭环 + 看板', short: '全局督办' },
];
