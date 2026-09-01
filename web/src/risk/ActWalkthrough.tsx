// 七幕剧本演示 stepper —— 幕序选择 + 帧渲染。
// 每幕一个帧组件；演示者逐幕点击推进（对应口径包§七 七幕端到端）。
import { useState } from 'react';
import ActComparison from './ActComparison';
import ActReveal from './ActReveal';
import ActEscalation from './ActEscalation';
import ActConsequence from './ActConsequence';
import ActRejection from './ActRejection';
import ActReporting from './ActReporting';
import ActBoard from './ActBoard';
import { ACTS } from './sevenAct';
import { RISK_COLORS as C } from './riskTheme';

const FRAMES: React.ComponentType[] = [
  ActComparison,
  ActReveal,
  ActEscalation,
  ActConsequence,
  ActRejection,
  ActReporting,
  ActBoard,
];

export default function ActWalkthrough() {
  const [active, setActive] = useState(0);
  const ActiveFrame = FRAMES[active] as React.ComponentType<{ onStart?: () => void }>;

  return (
    <div data-testid="act-walkthrough">
      {/* 幕序选择器 */}
      <div
        role="tablist"
        aria-label="七幕剧本幕序"
        style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 16 }}
      >
        {ACTS.map((act, i) => {
          const selected = i === active;
          return (
            <button
              key={act.no}
              role="tab"
              aria-selected={selected}
              data-testid={'act-tab-' + act.no}
              onClick={() => setActive(i)}
              style={{
                display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer',
                padding: '8px 12px', borderRadius: 8, fontSize: 13,
                background: selected ? C.accent : C.surface,
                border: '1px solid ' + (selected ? C.accent : C.border),
                color: selected ? '#fff' : C.text,
                fontWeight: selected ? 600 : 500,
                transition: 'background-color .15s ease, border-color .15s ease',
              }}
            >
              <span
                style={{
                  width: 20, height: 20, borderRadius: 6, flex: '0 0 auto',
                  display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: 11.5, fontWeight: 700,
                  background: selected ? 'rgba(255,255,255,.18)' : C.accent + '14',
                  color: selected ? '#fff' : C.accent,
                }}
              >
                {act.no}
              </span>
              <span style={{ whiteSpace: 'nowrap' }}>{act.name}</span>
            </button>
          );
        })}
      </div>

      {/* 当前幕帧 */}
      <ActiveFrame
        onStart={active === 0 ? () => setActive(1) : undefined}
      />
    </div>
  );
}
