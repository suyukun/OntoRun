// 第 3 幕 · 后果链帧 —— 红色预警之后的处置行动链：
// submit_disposal（冻结未用额度 + 追加押品）→ warning_push（向附属机构督办）→ risk_project（立项跟进）。
// 静态文案（口径包§七 第 3 幕）；动作名回链 12 对象 × 9 动作门面。
import { ArrowRightOutlined } from '@ant-design/icons';
import { FrameShell } from './actFrame';
import { RISK_COLORS as C } from './riskTheme';

const CHAIN: { action: string; title: string; desc: string }[] = [
  {
    action: 'submit_disposal',
    title: '处置方案 · 冻结未用额度 + 追加押品',
    desc: '冻结天晟未用授信额度，追加押品缓释敞口；押品对象联动更新（collateral），动作写回源数据。',
  },
  {
    action: 'warning_push',
    title: '金控向附属机构督办',
    desc: '对涉及机构下发督办单（warning_push），明确压降时限与跟进要求，按月催办汇报。',
  },
  {
    action: 'risk_project',
    title: '立项跟进',
    desc: '红色预警单独立项（risk_project），指派风险经理跟进处置进展，全过程留痕。',
  },
];

export default function ActConsequence() {
  return (
    <FrameShell
      actNo="第 3 幕"
      title="后果链：红色预警之后的处置行动"
      subtitle="预警触发处置——冻结额度、追加押品、向附属机构督办、立项跟进；每个动作都可审计、可回放。"
    >
      <div style={{ display: 'flex', alignItems: 'stretch', gap: 12, flexWrap: 'wrap' }}>
        {CHAIN.map((c, i) => (
          <div key={c.action} style={{ flex: '1 1 220px', minWidth: 200, display: 'flex', alignItems: 'stretch', gap: 12 }}>
            <div
              data-testid={'consequence-' + c.action}
              style={{ flex: 1, border: '1px solid ' + C.border, borderRadius: 8, background: C.surface, padding: 14 }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                <span
                  style={{
                    width: 22, height: 22, borderRadius: 6, flex: '0 0 auto',
                    display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                    background: C.accent + '14', border: '1px solid ' + C.accent + '44', color: C.accent, fontSize: 12, fontWeight: 600,
                  }}
                >
                  {i + 1}
                </span>
                <code style={{ fontSize: 11, color: C.textFaint }}>{c.action}</code>
              </div>
              <div style={{ fontWeight: 600, fontSize: 13.5, marginBottom: 6 }}>{c.title}</div>
              <div style={{ fontSize: 12.5, color: C.textDim, lineHeight: 1.7 }}>{c.desc}</div>
            </div>
            {i < CHAIN.length - 1 && (
              <div style={{ display: 'flex', alignItems: 'center', flex: '0 0 auto' }}>
                <ArrowRightOutlined style={{ color: C.textFaint, fontSize: 14 }} />
              </div>
            )}
          </div>
        ))}
      </div>
      <div style={{ marginTop: 14, fontSize: 12.5, color: C.textFaint, lineHeight: 1.7 }}>
        处置不解除按月催办汇报（口径包§四 生命周期状态机）；红色案例结束于「处置中 / 已督办」。
      </div>
    </FrameShell>
  );
}
