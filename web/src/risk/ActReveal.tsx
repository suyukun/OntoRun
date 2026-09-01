// 第 1 幕 · 揭示帧（money shot）—— 逐家机构 → 合计 10.8% 橙色预警的递进展示。
// 「单看都安全」：每家给分母与参考线；汇总后对 R1a 预警线 10% → 橙。数字来自口径包§五种子常量。
import { Button } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import { useState } from 'react';
import { FrameShell } from './actFrame';
import { TIANSHENG } from './sevenAct';
import LevelBadge from './LevelBadge';
import { RISK_COLORS as C } from './riskTheme';

const ORANGE = '橙';
const TOTAL_LEVEL = ORANGE;

export default function ActReveal() {
  // 揭示进度：0..N 家已亮 → 全部亮起后进入合计态
  const [revealed, setRevealed] = useState(0);
  const [showTotal, setShowTotal] = useState(false);
  const allShown = revealed >= TIANSHENG.institutions.length;

  const step = () => {
    if (!allShown) {
      setRevealed((r) => Math.min(r + 1, TIANSHENG.institutions.length));
    } else if (!showTotal) {
      setShowTotal(true);
    }
  };

  return (
    <FrameShell
      actNo="第 1 幕"
      title={'揭示：' + TIANSHENG.name + ' 风险有多大？'}
      subtitle="联合授信台账逐家亮出——单看每家都安全；归集后对预警线，橙色预警自动生成。"
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {TIANSHENG.institutions.map((inst, i) => {
          const shown = i < revealed;
          return (
            <div
              key={inst.org}
              data-testid={'reveal-row-' + i}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 14,
                padding: '12px 14px',
                border: '1px solid ' + (shown ? C.border : C.borderSoft),
                borderRadius: 8,
                background: shown ? C.surface : C.panelAlt,
                minHeight: 56,
              }}
            >
              <span
                style={{
                  width: 26, height: 26, borderRadius: 6, flex: '0 0 auto',
                  display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                  background: shown ? C.accent + '14' : 'transparent',
                  border: '1px solid ' + (shown ? C.accent + '55' : C.border),
                  color: shown ? C.accent : C.textFaint, fontWeight: 600, fontSize: 12,
                }}
              >
                {i + 1}
              </span>
              <div style={{ flex: '0 0 130px', fontWeight: 600, fontSize: 13.5 }}>{inst.org}</div>
              {shown ? (
                <div style={{ display: 'flex', alignItems: 'center', gap: 14, flexWrap: 'wrap', flex: 1 }}>
                  <span className="risk-num" style={{ fontSize: 17, fontWeight: 600 }}>{inst.balanceYi} 亿</span>
                  <span className="risk-num" style={{ fontSize: 13, color: C.textDim }}>
                    {inst.ratioPct.toFixed(1)}% · 分母 {inst.denominatorYi} 亿
                  </span>
                  <span style={{ fontSize: 12.5, color: C.green, background: C.green + '12', border: '1px solid ' + C.green + '44', padding: '3px 8px', borderRadius: 999 }}>
                    单看都安全 · {inst.refLine}
                  </span>
                </div>
              ) : (
                <div style={{ flex: 1, color: C.textFaint, fontSize: 13 }}>… 待揭示（逐家亮出）</div>
              )}
            </div>
          );
        })}
      </div>

      {/* 合计 → 10.8% 橙 */}
      {allShown && (
        <div
          data-testid="reveal-total"
          className="risk-fade-up"
          style={{
            marginTop: 14,
            border: '1px solid ' + (showTotal ? C.orange + '99' : C.border),
            borderRadius: 8,
            background: showTotal ? C.orange + '0F' : C.surface,
            padding: 14,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
            <span style={{ fontSize: 14, color: C.textDim }}>归集合计</span>
            <span className="risk-num" style={{ fontSize: 22, fontWeight: 600 }}>{TIANSHENG.consolidatedYi} 亿</span>
            <span style={{ color: C.textFaint }}>÷ 集团并表资本 {TIANSHENG.capitalYi} 亿</span>
            <span style={{ color: C.textDim, fontSize: 13 }}>=</span>
            <span className="risk-num" style={{ fontSize: 22, fontWeight: 600 }}>{TIANSHENG.ratioPct}%</span>
            {showTotal ? (
              <LevelBadge level={TOTAL_LEVEL} size="md" />
            ) : (
              <span style={{ fontSize: 12.5, color: C.textFaint }}>点击「汇总归集」对限额 →</span>
            )}
          </div>
          {showTotal && (
            <div className="risk-fade-up" style={{ marginTop: 10, fontSize: 12.5, color: C.textDim, lineHeight: 1.7 }}>
              {TIANSHENG.ratioPct}% ≥ 预警线 10% → <span style={{ color: C.orange, fontWeight: 600 }}>橙色预警已自动生成</span>（{TIANSHENG.ruleBasis}）
            </div>
          )}
        </div>
      )}

      <div style={{ display: 'flex', gap: 10, marginTop: 16 }}>
        <Button type="primary" onClick={step} disabled={showTotal}>
          {!allShown ? '揭示下一家 →' : showTotal ? '已完成揭示' : '汇总归集，对限额 →'}
        </Button>
        <Button
          icon={<ReloadOutlined />}
          onClick={() => {
            setRevealed(0);
            setShowTotal(false);
          }}
        >
          重置
        </Button>
      </div>
    </FrameShell>
  );
}
