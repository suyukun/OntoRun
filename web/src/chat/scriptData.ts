// 天晟 R1a 剧本 —— chat 演示假数据
// 内容口径全部来自 web/src/proto/fakeData.ts（天晟 R1a）与 docs/chat-ux-spec-v1.md；
// 报告正文 / 抽屉明细 / 工具步骤拆解为规格要求的扩展内容（spec §5.4/§5.5/§6.2 自拟授权），
// 所有数字与剧本同源：86.4 亿 / 800 亿 / 10.8% / 10% / 8.0% / 5.5% / 8.2% / 1,284 行 / #A-1024。
import { REVEAL_TEXT } from '../proto/fakeData';

export type AiBlockSpec =
  | { type: 'tools' }
  | { type: 'text'; md: string }
  | { type: 'table' }
  | { type: 'chart' }
  | { type: 'report' }
  | { type: 'confirm' };

export interface AiScript {
  id: string;
  /** 思考总时长，>800ms 才出骨架（§8.2） */
  thinkMs: number;
  blocks: AiBlockSpec[];
}

/** tools 展开态步骤（§5.5：API 名 + 中文动作 + 描述 + 耗时；desc 内反引号片段按行内 code 渲染） */
export interface ToolStepView {
  api: string;
  action: string;
  desc: string;
  duration: string;
}

export const TOOL_STEPS_VIEW: ToolStepView[] = [
  {
    api: 'risk_group_reveal',
    action: '查分组归集明细',
    desc: 'GRP-2026-900001 · `ap_group_customer` × `ap_concentration_limit`',
    duration: '0.6s',
  },
  {
    api: 'reconcile_check',
    action: '勾稽对账',
    desc: '明细外部 86.4 + 内部抵销 0.0 = 台账归集 86.4 ✓',
    duration: '0.7s',
  },
  {
    api: 'rule_grade_r1a',
    action: 'R1a 定级',
    desc: '阈值 `CAP_WARN_LINE=10%`（金控办法 32/33 自设，安平风管部 2025-06-30 批）',
    duration: '0.5s',
  },
];

/** 折叠行摘要（§5.5；1.8s = 三步耗时合计） */
export const TOOLS_SUMMARY = '已核查 3 张表 · 执行 2 条规则 · 勾稽通过 · 1.8s';

// —— 各剧本 text 块文案（数字全部来自剧本口径）——
const TEXT_REACHED =
  '三家机构中，**证券 5.5%** 与**资管 8.2%** 已触达各自参考线（触达 = 关注级）；银行 **8.0%** 在行内限额内。归集维度 **10.8%** ≥ 预警线 **10%**，为 **R1a 橙色预警**，风险集中在归集。明细如下：';
const TEXT_OVERVIEW =
  '**天晟集团当前存在 1 项橙色预警（R1a · 归集集中度）。** 归集集中度 **10.8%** ≥ 预警线 **10%**；三家机构单家占比均在参考线之内，风险集中在归集维度。明细如下：';
const TEXT_FORMULA =
  '归集集中度 = 归集敞口 ÷ 并表资本 = **86.4 亿** ÷ **800 亿** = **10.8%**，达到 `CAP_WARN_LINE` = **10%** → 触发 R1a 橙色预警。\n\n分母为集团并表资本 **800 亿**（`CAP_GROUP_CONSOLIDATED`），统计周期 T-1 日终；计算依据可在「证据链」逐步核对。';
const TEXT_CHART =
  '各机构占比与预警线对比如下：**归集 10.8%** 超过预警线 **10%**（橙色柱）；银行 **8.0%** 在行内限额内，证券、资管触达参考线，以黄色标出。';
const TEXT_REPORT =
  '报告已生成：围绕 **R1a** 橙色预警的处置建议，含风险现状、计算过程与依据索引。可预览全文或下载 Markdown。';
const TEXT_CONFIRM =
  '已按 R1a 处置依据起草提议：**冻结天晟集团新增授信**。该动作会写回源系统，需要你审批拍板后执行。';
const TEXT_FULL =
  '**天晟集团归集集中度 10.8% ≥ 预警线 10%，触发 R1a 橙色预警。** ' +
  REVEAL_TEXT +
  '\n\n明细与对比如下，处置建议见报告与审批提议：';
export const FALLBACK_TEXT =
  '本轮演示剧本覆盖天晟集团 **R1a** 归集集中度场景。按 `CAP_WARN_LINE` = **10%** 口径：归集 **86.4 亿** ÷ 并表资本 **800 亿** = **10.8%**，橙色预警成立；可继续询问预警明细、计算过程、对比图、处置报告或审批提议。';

/** s1 预置会话的种子问题（命中 full 全六块剧本，§11-4「一屏六块齐全」） */
export const FULL_SEED_QUESTION = '天晟集团现在有什么风险预警？给出完整处置建议。';

export const SCRIPTS: Record<string, AiScript> = {
  overview: { id: 'overview', thinkMs: 1200, blocks: [{ type: 'tools' }, { type: 'text', md: TEXT_OVERVIEW }, { type: 'table' }] },
  reached: { id: 'reached', thinkMs: 1200, blocks: [{ type: 'tools' }, { type: 'text', md: TEXT_REACHED }, { type: 'table' }] },
  reveal: { id: 'reveal', thinkMs: 1400, blocks: [{ type: 'tools' }, { type: 'text', md: REVEAL_TEXT }] },
  formula: { id: 'formula', thinkMs: 1400, blocks: [{ type: 'tools' }, { type: 'text', md: TEXT_FORMULA }] },
  chart: { id: 'chart', thinkMs: 1200, blocks: [{ type: 'tools' }, { type: 'text', md: TEXT_CHART }, { type: 'chart' }] },
  report: { id: 'report', thinkMs: 1200, blocks: [{ type: 'tools' }, { type: 'text', md: TEXT_REPORT }, { type: 'report' }] },
  confirm: { id: 'confirm', thinkMs: 1200, blocks: [{ type: 'tools' }, { type: 'text', md: TEXT_CONFIRM }, { type: 'confirm' }] },
  full: {
    id: 'full',
    thinkMs: 1600,
    blocks: [
      { type: 'tools' },
      { type: 'text', md: TEXT_FULL },
      { type: 'table' },
      { type: 'chart' },
      { type: 'report' },
      { type: 'confirm' },
    ],
  },
  fallback: { id: 'fallback', thinkMs: 1200, blocks: [{ type: 'tools' }, { type: 'text', md: FALLBACK_TEXT }] },
};

/** 关键词 → 剧本路由（演示用；未命中走 fallback = 错误态演示路径，见 useChatEngine） */
export function matchScript(question: string): AiScript {
  const q = question.trim();
  if (/完整/.test(q)) return SCRIPTS.full;
  if (/为什么|反而/.test(q)) return SCRIPTS.reveal;
  if (/怎么算|分母|公式|如何计算/.test(q)) return SCRIPTS.formula;
  if (/图|对比|占比/.test(q)) return SCRIPTS.chart;
  if (/报告/.test(q)) return SCRIPTS.report;
  if (/冻结|提议|审批/.test(q)) return SCRIPTS.confirm;
  if (/触达/.test(q)) return SCRIPTS.reached;
  if (/预警|风险|天晟|归集|R1a/.test(q)) return SCRIPTS.overview;
  return SCRIPTS.fallback;
}

// —— 报告卡（§5.4；meta 文案为 spec 定值）——
export const REPORT = {
  title: '天晟集团风险处置建议报告',
  tag: '草稿',
  summary: '归集集中度 10.8% 触发 R1a 橙色预警，建议冻结新增授信并核查关联交易……',
  meta: '生成 14:32 · 依据 3 表 2 规则 · 审计 #A-1024',
  fileName: '天晟集团风险处置建议报告.md',
  md: [
    '### 一、风险现状',
    '天晟集团归集集中度 **10.8%**（**86.4 亿** ÷ 并表资本 **800 亿**），达到并超过监管预警线 **10%**（`CAP_WARN_LINE`），触发 **R1a 橙色预警**。三家机构单家占比——银行 **8.0%**、证券 **5.5%**、资管 **8.2%**——均在各自参考线之内，风险集中于归集维度。',
    '',
    '### 二、计算过程与依据',
    '- 数据来源：`ap_group_customer`（1,284 行，T-1 快照）、`ap_concentration_limit`、`base.ap_sys_param`；',
    '- 勾稽：明细外部 **86.4** + 内部抵销 **0.0** = 台账归集 **86.4** ✓；',
    '- 定级：阈值 `CAP_WARN_LINE=10%`（金控办法 32/33 自设，安平风管部 2025-06-30 批）。',
    '',
    '### 三、处置建议',
    '1. **冻结天晟集团新增授信**：R1a 预警关闭前暂停新增授信审批；',
    '2. **核查关联交易**：按 2023 关联交易办法第二十三条对归集敞口逐笔复核；',
    '3. **一周内复算**：处置生效后按同口径复算归集集中度，确认回落至 **10%** 以下。',
    '',
    '### 四、审批与留痕',
    '本报告为草稿；处置动作须经人工批准并留痕后写回源系统，全程审计可追溯（审计 `#A-1024`）。',
  ].join('\n'),
};

// —— 空态建议 chips（§3.2 六问，文案终稿）——
export type ChipIcon = 'alert' | 'question' | 'calc' | 'chart' | 'report' | 'table';
export interface ChipSpec {
  key: string;
  icon: ChipIcon;
  text: string;
}
export const SUGGESTION_CHIPS: ChipSpec[] = [
  { key: 'c1', icon: 'alert', text: '天晟集团现在有什么风险预警？' },
  { key: 'c2', icon: 'question', text: '为什么各家机构都安全，归集反而触发橙色预警？' },
  { key: 'c3', icon: 'calc', text: 'R1a 归集集中度怎么算的？分母是什么？' },
  { key: 'c4', icon: 'chart', text: '画一张各机构占比与预警线的对比图' },
  { key: 'c5', icon: 'report', text: '生成天晟集团风险处置建议报告' },
  { key: 'c6', icon: 'table', text: '天晟集团哪些机构触达参考线？' },
];

// —— 证据链抽屉（§6.2 四区；表名来自 fakeData.EVIDENCE.tables，行数/快照为 spec §6.2 假设 5 占位值）——
export const EVIDENCE_DETAIL = {
  tables: [
    { name: 'ap_group_customer', rows: '1,284 行', snapshot: '快照 08:00' },
    { name: 'ap_concentration_limit', rows: '36 行', snapshot: '快照 08:00' },
    { name: 'base.ap_sys_param', rows: '112 行', snapshot: '快照 08:00' },
  ],
  rules: [
    {
      name: 'R1a 归集集中度',
      expr: 'concentration = Σ 归集敞口 ÷ CAP_GROUP_CONSOLIDATED ≥ CAP_WARN_LINE(10%) → 橙色预警',
      source: '阈值 CAP_WARN_LINE=10% · 金控办法 32/33 自设 · 安平风管部 2025-06-30 批',
    },
    {
      name: 'R1b 机构参考线',
      expr: 'ratio ≥ ref → 触达（当前：证券 5.5% / 资管 8.2% 触达，银行在行内限额内）',
      source: '参考线与阈值同源 · 安平风管部 2025-06-30 批',
    },
  ],
  caliber: [
    { key: '分母', value: '集团并表资本 800 亿（CAP_GROUP_CONSOLIDATED）' },
    { key: '统计周期', value: 'T-1 日终' },
  ],
  timeline: [
    { time: '14:31:02', action: '查询归集明细' },
    { time: '14:31:03', action: '勾稽对账通过' },
    { time: '14:31:04', action: 'R1a 定级 orange' },
  ],
  footer: '本回答全部数字可回溯至以上来源',
};