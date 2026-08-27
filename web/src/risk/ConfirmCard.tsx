// 双签参数卡片 —— 高风险动作「AI 只提议 · 人类确认后才执行」的显性载体。
// 从 RiskChatPanel 抽出复用；浅色 token 由 riskTheme 提供。
import { Button, Tag } from 'antd';
import { CheckCircleFilled, CloseCircleFilled, SafetyCertificateOutlined } from '@ant-design/icons';
import './risk.css';
import { RISK_COLORS as C, WARN_TAG_TINTS } from './riskTheme';
import { formatRiskValue } from './riskData';
import type { RiskActionMeta } from './riskData';

export interface ConfirmInfo {
  callId: string;
  name: string;
  args: Record<string, unknown>;
}

export type ConfirmOutcome = 'applied' | 'rejected' | 'error' | null | undefined;

function tagTint(t: { bg: string; border: string }) {
  return { background: t.bg, borderColor: t.border } as const;
}

function paramTitle(actionMeta: RiskActionMeta | undefined, key: string): string {
  return actionMeta?.params_schema?.properties?.[key]?.title ?? key;
}

export default function ConfirmCard({
  confirm, actionMeta, resolved, confirmReply, disabled, onConfirm,
}: {
  confirm: ConfirmInfo;
  actionMeta?: RiskActionMeta;
  resolved?: ConfirmOutcome;
  confirmReply?: string;
  disabled: boolean;
  onConfirm: (v: boolean) => void;
}) {
  return (
    <div style={{ marginTop: 12, border: '1px solid ' + C.accent + '66', borderRadius: 8, background: C.accent + '0A', overflow: 'hidden' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 14px', background: C.accent + '12', borderBottom: '1px solid ' + C.accent + '33' }}>
        <SafetyCertificateOutlined style={{ color: C.accent }} />
        <span style={{ fontWeight: 600, fontSize: 13.5 }}>高风险动作 · 人机双签</span>
        <Tag style={{ marginLeft: 'auto', ...tagTint(WARN_TAG_TINTS.YELLOW) }}>AI 只提议 · 人类确认后才执行</Tag>
      </div>
      <div style={{ padding: '12px 14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10, flexWrap: 'wrap' }}>
          <span style={{ fontSize: 15, fontWeight: 600 }}>{confirm.name}</span>
          <Tag style={{ color: C.textDim, borderColor: C.border, background: C.panelAlt }}>{actionMeta?.description || '风控动作'}</Tag>
        </div>
        <div style={{ border: '1px solid ' + C.border, borderRadius: 6, overflow: 'hidden', marginBottom: 12 }}>
          {Object.entries(confirm.args).map(([k, v]) => (
            <div key={k} style={{ display: 'flex', borderBottom: '1px solid ' + C.borderSoft, background: C.surface }}>
              <div style={{ width: 130, flex: '0 0 auto', padding: '8px 12px', color: C.textDim, fontSize: 12.5, borderRight: '1px solid ' + C.borderSoft, background: C.panelAlt }}>
                {paramTitle(actionMeta, k)}
              </div>
              <div className="risk-num" style={{ padding: '8px 12px', fontSize: 13, wordBreak: 'break-all' }}>
                {formatRiskValue(v)}
              </div>
            </div>
          ))}
        </div>
        {!resolved ? (
          <div style={{ display: 'flex', gap: 10 }}>
            <Button type="primary" icon={<CheckCircleFilled />} disabled={disabled} onClick={() => onConfirm(true)}>
              确认执行
            </Button>
            <Button danger icon={<CloseCircleFilled />} disabled={disabled} onClick={() => onConfirm(false)}>
              驳回
            </Button>
          </div>
        ) : (
          <div style={{ fontSize: 13 }}>
            <span style={{ color: resolved === 'applied' ? C.green : C.red, fontWeight: 600 }}>
              {resolved === 'applied' ? '✓ 已执行（真实写回 + 审计留痕）' : resolved === 'rejected' ? '✕ 已驳回，未执行任何写回' : '✕ 执行出错'}
            </span>
            {confirmReply && <div style={{ color: C.textDim, marginTop: 6, whiteSpace: 'pre-wrap', fontSize: 12.5 }}>{confirmReply}</div>}
          </div>
        )}
      </div>
    </div>
  );
}
