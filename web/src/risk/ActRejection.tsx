// 第 4 幕 · 双签高光帧（人拦 AI）—— AI 提议拆分授信绕开归集 → 审批人按 2023 办法第二十三条当场驳回。
// 演出「LLM 提议 ≠ 直接生效」：驳回理由本身展示专业（gov.cn 原文条款）。
import { Button } from 'antd';
import { CloseCircleFilled, RobotOutlined, SafetyCertificateOutlined, UndoOutlined } from '@ant-design/icons';
import { useState } from 'react';
import { FrameShell } from './actFrame';
import { AI_SPLIT_PROPOSAL, REG_2023_ARTICLE_23_3 } from './sevenAct';
import { RISK_COLORS as C } from './riskTheme';

export default function ActRejection() {
  const [rejected, setRejected] = useState(false);

  return (
    <FrameShell
      actNo="第 4 幕"
      title="双签高光：人拦 AI——合规腾挪被当场驳回"
      subtitle="AI 的提议看着「合规」，审批人一眼识破——这是隐匿关联关系的拆分交易，按 2023 关联交易办法第二十三条驳回。"
    >
      {/* AI 提议卡 */}
      <div
        data-testid="ai-proposal"
        style={{
          border: '1px solid ' + (rejected ? C.border : C.accent + '66'),
          borderRadius: 8,
          background: rejected ? C.surface : C.accent + '0A',
          padding: 16,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
          <RobotOutlined style={{ color: C.accent }} />
          <span style={{ fontWeight: 600, fontSize: 14 }}>{AI_SPLIT_PROPOSAL.title}</span>
          {rejected && (
            <span data-testid="rejected-tag" style={{ marginLeft: 'auto', fontSize: 12, color: C.red, background: C.red + '14', border: '1px solid ' + C.red + '55', padding: '3px 8px', borderRadius: 999 }}>
              已驳回 · 未执行
            </span>
          )}
        </div>
        <div style={{ fontSize: 13, color: C.textDim, lineHeight: 1.7, marginBottom: 12 }}>{AI_SPLIT_PROPOSAL.summary}</div>
        <div style={{ border: '1px solid ' + C.border, borderRadius: 6, overflow: 'hidden', marginBottom: 10 }}>
          {AI_SPLIT_PROPOSAL.args.map((a) => (
            <div key={a.label} style={{ display: 'flex', borderBottom: '1px solid ' + C.borderSoft, background: C.surface }}>
              <div style={{ width: 140, flex: '0 0 auto', padding: '8px 12px', color: C.textDim, fontSize: 12.5, borderRight: '1px solid ' + C.borderSoft, background: C.panelAlt }}>
                {a.label}
              </div>
              <div style={{ padding: '8px 12px', fontSize: 13 }}>{a.value}</div>
            </div>
          ))}
        </div>
        <div style={{ fontSize: 12.5, color: C.textFaint, lineHeight: 1.7 }}>{AI_SPLIT_PROPOSAL.issue}</div>
      </div>

      {/* 审批人操作 */}
      <div style={{ marginTop: 14, display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
        {!rejected ? (
          <>
            <Button
              type="primary"
              danger
              icon={<CloseCircleFilled />}
              onClick={() => setRejected(true)}
              data-testid="reject-button"
              size="large"
            >
              审批人驳回（依据 2023 办法第二十三条）
            </Button>
            <span style={{ fontSize: 12.5, color: C.textFaint }}>演示「人拦 AI」：AI 提议 ≠ 直接生效</span>
          </>
        ) : (
          <>
            <Button icon={<UndoOutlined />} onClick={() => setRejected(false)}>
              重新演示
            </Button>
            <span style={{ fontSize: 12.5, color: C.green }}>已退回重新起草——AI 学习后重新提出合规处置方案。</span>
          </>
        )}
      </div>

      {/* 驳回理由 */}
      {rejected && (
        <div
          data-testid="rejection-reason"
          className="risk-fade-up"
          style={{
            marginTop: 14,
            border: '1px solid ' + C.red + '66',
            borderRadius: 8,
            background: C.red + '0D',
            padding: 16,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
            <SafetyCertificateOutlined style={{ color: C.red }} />
            <span style={{ fontWeight: 600, fontSize: 14, color: C.red }}>驳回理由 · {REG_2023_ARTICLE_23_3.ref}</span>
          </div>
          <div style={{ fontSize: 13.5, color: C.text, lineHeight: 1.8, background: C.surface, border: '1px solid ' + C.border, borderRadius: 6, padding: '12px 14px' }}>
            「{REG_2023_ARTICLE_23_3.text}」
          </div>
          <div style={{ marginTop: 8, fontSize: 12.5, color: C.textDim, lineHeight: 1.7 }}>{REG_2023_ARTICLE_23_3.note}</div>
        </div>
      )}
    </FrameShell>
  );
}
