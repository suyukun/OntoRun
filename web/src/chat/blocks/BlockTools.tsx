// tools 块 —— 过程透明（docs/chat-ux-spec-v1.md §5.5：完成态折叠一行，展开为垂直步骤列表）
import { useState, type ReactNode } from 'react';
import { CheckCircleOutlined, DownOutlined, LoadingOutlined, UpOutlined } from '@ant-design/icons';
import { TOOLS_SUMMARY, TOOL_STEPS_VIEW } from '../scriptData';
import { RISK_COLORS } from '../../risk/riskTheme';
import { chatFontMono } from '../chatTokens';

/** desc 内反引号片段 → 行内 code 样式（§5.5 技术标识内联 code） */
function DescText({ text }: { text: string }) {
  const parts = text.split(/`([^`]+)`/g);
  return (
    <>
      {parts.map((seg, i) =>
        i % 2 === 1 ? (
          <code key={i} style={{ fontFamily: chatFontMono, fontSize: 12.5, background: RISK_COLORS.panelAlt, borderRadius: 4, padding: '1px 6px' }}>
            {seg}
          </code>
        ) : (
          <span key={i}>{seg}</span>
        ),
      )}
    </>
  );
}

function ToggleRow({ done, onToggle, summary }: { done: boolean; onToggle: () => void; summary: string }) {
  return (
    <button
      className="chat-tools-row"
      onClick={onToggle}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 6,
        width: '100%',
        border: 0,
        background: 'transparent',
        cursor: 'pointer',
        padding: '4px 8px',
        borderRadius: 6,
        textAlign: 'left',
      }}
    >
      {done ? (
        <CheckCircleOutlined style={{ fontSize: 14, color: RISK_COLORS.textFaint }} />
      ) : (
        <LoadingOutlined style={{ fontSize: 14, color: RISK_COLORS.accent }} />
      )}
      <span style={{ fontSize: 13, lineHeight: '20px', color: RISK_COLORS.textDim }}>{done ? summary : '正在核查…'}</span>
      <span style={{ flex: 1 }} />
      {done ? <DownOutlined style={{ fontSize: 12, color: RISK_COLORS.textFaint }} /> : <UpOutlined style={{ fontSize: 12, color: RISK_COLORS.textFaint }} />}
    </button>
  );
}

function StepNode({ children }: { children: ReactNode }) {
  return <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: 14, flexShrink: 0 }}>{children}</div>;
}

export default function BlockTools({
  phase,
  stepStatus,
  stepLabels,
}: {
  phase: 'skeleton' | 'running' | 'done';
  stepStatus: ('process' | 'finish')[];
  /** live（批 3）：真实证据 intent 步骤文案；缺省走剧本演示步骤 */
  stepLabels?: string[];
}) {
  const steps = stepLabels ?? TOOL_STEPS_VIEW.map((s) => s.action);
  const summary = stepLabels
    ? `实查 ${steps.length} 项 · 证据链随答返回`
    : TOOLS_SUMMARY;
  // 展开记忆（§5.5）：进行中默认展开，完成折叠；用户手动切换后以用户为准（单次回答内保持）
  const [override, setOverride] = useState<boolean | null>(null);
  const expanded = override ?? phase !== 'done';

  if (phase === 'skeleton') {
    // §5.5 骨架先行（两行 Skeleton 高 14、宽 60%/40%）
    return (
      <div style={{ padding: '2px 0' }}>
        <div className="chat-skel" style={{ width: '60%' }} />
        <div className="chat-skel" style={{ width: '40%', marginTop: 10 }} />
      </div>
    );
  }

  if (!expanded) {
    return <ToggleRow done={phase === 'done'} onToggle={() => setOverride(true)} summary={summary} />;
  }

  return (
    <div>
      <ToggleRow done={phase === 'done'} onToggle={() => setOverride(false)} summary={summary} />
      <div style={{ marginTop: 8, display: 'flex', flexDirection: 'column', gap: 12 }}>
        {steps.map((label, i) => {
          const st = stepStatus[i];
          if (!st) return null; // 未到达的步骤不渲染（逐步 fade-in，§5.5）
          return (
            <div key={label + i} className="chat-fade-120" style={{ display: 'flex', gap: 8 }}>
              <StepNode>
                {st === 'finish' ? (
                  <span style={{ width: 6, height: 6, borderRadius: 3, background: RISK_COLORS.green, marginTop: 7 }} />
                ) : (
                  <LoadingOutlined style={{ fontSize: 14, color: RISK_COLORS.accent }} />
                )}
                {i < steps.length - 1 && stepStatus[i + 1] && (
                  <span style={{ flex: 1, width: 1, background: RISK_COLORS.borderSoft, minHeight: 12, marginTop: 4 }} />
                )}
              </StepNode>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontSize: 13, fontWeight: 600 }}>{label}</span>
                </div>
                {stepLabels == null && (
                  <div style={{ marginTop: 2, fontSize: 12.5, lineHeight: '20px', color: RISK_COLORS.textDim }}>
                    <DescText text={TOOL_STEPS_VIEW[i].desc} />
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}