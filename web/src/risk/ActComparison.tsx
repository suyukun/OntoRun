// 第 0 幕 · 现状对照帧（30 秒，先痛后甜）—— 手工归集一周 vs 现在一句话。
// 静态文案（口径包§七 第 0 幕）；数据无后端依赖。
import { Button } from 'antd';
import { ClockCircleOutlined, ThunderboltOutlined } from '@ant-design/icons';
import { FrameShell, FrameSub } from './actFrame';
import { MANUAL_WORKFLOW_STEPS, MANUAL_RESULT, NOW_RESULT } from './sevenAct';
import { RISK_COLORS as C } from './riskTheme';

export default function ActComparison({ onStart }: { onStart?: () => void }) {
  return (
    <FrameShell
      actNo="第 0 幕"
      title="现状对照：一周的归集，一句话做完"
      subtitle="同样的联合授信归集——手工时代跨 3 家附属机构等报送、Excel 对账、翻股权图谱，一轮下来一周；现在，一句话。"
    >
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1fr) minmax(0,1fr)', gap: 16 }}>
        {/* 手工时代 */}
        <div
          data-testid="act0-before"
          style={{ border: '1px solid ' + C.border, borderRadius: 8, background: C.surface, padding: 16 }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
            <ClockCircleOutlined style={{ color: C.textFaint }} />
            <span style={{ fontWeight: 600, fontSize: 13.5 }}>手工时代 · 跨机构归集</span>
          </div>
          <ol style={{ margin: 0, paddingLeft: 18, display: 'flex', flexDirection: 'column', gap: 8 }}>
            {MANUAL_WORKFLOW_STEPS.map((s, i) => (
              <li key={i} style={{ fontSize: 13, color: C.textDim, lineHeight: 1.6 }}>
                {s}
              </li>
            ))}
          </ol>
          <div
            style={{
              marginTop: 14,
              padding: '10px 12px',
              borderRadius: 6,
              background: C.panelAlt,
              borderLeft: '3px solid ' + C.textFaint,
              fontSize: 13.5,
              fontWeight: 600,
              color: C.textDim,
            }}
          >
            {MANUAL_RESULT}
          </div>
        </div>

        {/* 现在 */}
        <div
          data-testid="act0-after"
          style={{ border: '1px solid ' + C.accent + '66', borderRadius: 8, background: C.accent + '0A', padding: 16 }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
            <ThunderboltOutlined style={{ color: C.accent }} />
            <span style={{ fontWeight: 600, fontSize: 13.5, color: C.accent }}>现在 · Agent 对话直达</span>
          </div>
          <div
            style={{
              fontSize: 15,
              lineHeight: 1.7,
              color: C.text,
              background: C.surface,
              border: '1px solid ' + C.border,
              borderRadius: 6,
              padding: '10px 12px',
            }}
          >
            问一句<span style={{ fontWeight: 600 }}>「天晟集团风险有多大？」</span>
          </div>
          <div style={{ marginTop: 10, fontSize: 13, color: C.textDim, lineHeight: 1.7 }}>
            系统自动：归集联合授信台账 → 逐家算集中度 → 汇总对限额 → 亮灯 → 每条结论附证据链（真表 / 真规则 / 真分母）。
          </div>
          <div
            style={{
              marginTop: 14,
              padding: '10px 12px',
              borderRadius: 6,
              background: C.surface,
              borderLeft: '3px solid ' + C.accent,
              fontSize: 16,
              fontWeight: 600,
              color: C.accent,
            }}
          >
            {NOW_RESULT}
          </div>
          {onStart && (
            <Button type="primary" size="small" style={{ marginTop: 12 }} onClick={onStart}>
              进入第 1 幕 · 揭示
            </Button>
          )}
        </div>
      </div>
      <FrameSub>数据口径</FrameSub>
      <div style={{ fontSize: 12, color: C.textFaint, lineHeight: 1.7 }}>
        手工链路 = 跨 3 家附属机构（银行 / 证券 / 资管）报送、Excel 对账、人工翻股权图谱查关联（口径包§七 第 0 幕）。
      </div>
    </FrameShell>
  );
}
