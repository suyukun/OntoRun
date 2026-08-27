// 演示示例问题（真实可答：数据来自 ap_anping 真实企业）
// kind: read=精准问答 / action=真实动作 / decline=域外拒答
// 色值 = riskTheme.RISK_COLORS 浅底语义色（blue/yellow/red），亮度适配浅底
export interface RiskExamplePrompt {
  label: string;
  text: string;
  kind: 'read' | 'action' | 'decline';
}

export const EXAMPLE_PROMPTS: RiskExamplePrompt[] = [
  { label: '本月红色预警', text: '本月新增红色预警信号有几条？', kind: 'read' },
  { label: '集团成员与编号', text: '中科智造产业发展集团的集团客户编号和成员企业数是多少？', kind: 'read' },
  { label: '集中度占比', text: '中科智造产业发展集团的集中度限额和当前敞口占比是多少？', kind: 'read' },
  { label: '确认预警（低风险）', text: '确认预警信号 WS-2026-00000110', kind: 'action' },
  { label: '等级调整 Y→R（双签）', text: '将预警信号 WS-2026-00000129 的预警等级从黄色调整为红色，理由：押品贬值超过预警阈值，我确认执行', kind: 'action' },
  { label: '巴塞尔资本充足率（拒答）', text: '根据巴塞尔协议 III 计算集团的资本充足率', kind: 'decline' },
];

export const KIND_TAG: Record<string, { color: string; label: string }> = {
  read: { color: '#175cd3', label: '精准问答' },
  action: { color: '#b54708', label: '真实动作' },
  decline: { color: '#b42318', label: '域外拒答' },
};
