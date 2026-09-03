// confirm 块 —— 双签卡（docs/chat-ux-spec-v1.md §5.6；终态不可逆，卡保留在消息流中）
// 注：2026-09-03 视觉走查裁决——收敛为「处置依据 + 批准执行/驳回 + 状态条」，不渲染审批意见输入框。
import { useState } from 'react';
import { Button } from 'antd';
import { AuditOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { CONFIRM } from '../../proto/fakeData';
import { RISK_COLORS, WARN_TAG_TINTS } from '../../risk/riskTheme';

const PROPOSAL = CONFIRM.title.replace('AI 提议 · ', '');
const CONFIRM_LOADING_MS = 600; // §5.6 批准 loading 600ms 模拟写回

const hhmm = () => {
  const d = new Date();
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
};

function StatusTag({ state }: { state: 'pending' | 'applied' | 'rejected' }) {
  if (state === 'applied')
    return (
      <span style={{ fontSize: 12, lineHeight: '20px', color: RISK_COLORS.green, background: RISK_COLORS.panelAlt, border: `1px solid ${RISK_COLORS.borderSoft}`, borderRadius: 4, padding: '0 8px' }}>
        已执行
      </span>
    );
  if (state === 'rejected')
    return (
      <span style={{ fontSize: 12, lineHeight: '20px', color: RISK_COLORS.textDim, background: RISK_COLORS.panelAlt, border: `1px solid ${RISK_COLORS.borderSoft}`, borderRadius: 4, padding: '0 8px' }}>
        已驳回
      </span>
    );
  return (
    <span
      style={{
        fontSize: 12,
        lineHeight: '20px',
        color: RISK_COLORS.orange,
        background: WARN_TAG_TINTS.ORANGE.bg,
        border: `1px solid ${WARN_TAG_TINTS.ORANGE.border}`,
        borderRadius: 4,
        padding: '0 8px',
      }}
    >
      待确认
    </span>
  );
}

export default function BlockConfirm({ onEvidence }: { onEvidence: () => void }) {
  const [state, setState] = useState<'pending' | 'applied' | 'rejected'>('pending');
  const [loading, setLoading] = useState(false);
  const [doneAt, setDoneAt] = useState('');

  const approve = () => {
    if (loading || state !== 'pending') return;
    setLoading(true); // 提交即双钮 disabled 防重复（§5.6）
    setTimeout(() => {
      setState('applied');
      setLoading(false);
      setDoneAt(hhmm());
    }, CONFIRM_LOADING_MS);
  };
  const reject = () => {
    if (loading || state !== 'pending') return;
    setState('rejected');
    setDoneAt(hhmm());
  };

  const decided = state !== 'pending';

  return (
    <div
      style={{
        background: '#fff',
        // 待确认：1px 橙边 + 左缘 3px 橙；已处置：边框退灰且不可逆（§5.6）
        border: decided ? `1px solid ${RISK_COLORS.borderSoft}` : `1px solid ${WARN_TAG_TINTS.ORANGE.border}`,
        borderLeft: decided ? `1px solid ${RISK_COLORS.borderSoft}` : `3px solid ${RISK_COLORS.orange}`,
        borderRadius: 8,
        padding: 12,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <AuditOutlined style={{ fontSize: 16, color: decided ? RISK_COLORS.textDim : RISK_COLORS.orange }} />
        <span style={{ fontSize: 13, lineHeight: '20px', fontWeight: 600, color: decided ? RISK_COLORS.textDim : RISK_COLORS.orange }}>
          {decided ? 'AI 提议 · 已处置' : 'AI 提议 · 需人工拍板'}
        </span>
        <span style={{ flex: 1 }} />
        <StatusTag state={state} />
      </div>
      <div style={{ marginTop: 8, fontSize: 14, lineHeight: '24px' }}>{PROPOSAL}</div>
      <div style={{ marginTop: 4, fontSize: 12.5, lineHeight: '20px', color: RISK_COLORS.textDim }}>
        {CONFIRM.reason}{' '}
        <button className="chat-link" style={{ background: 'none', border: 0, padding: 0, fontSize: 12.5 }} onClick={onEvidence}>
          查看依据
        </button>
      </div>

      {state === 'pending' && (
        <div style={{ marginTop: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
          <Button type="primary" loading={loading} disabled={loading} onClick={approve}>
            批准执行
          </Button>
          <Button disabled={loading} onClick={reject}>
            驳回
          </Button>
        </div>
      )}

      {decided && (
        <div
          style={{
            marginTop: 12,
            paddingTop: 10,
            borderTop: `1px solid ${RISK_COLORS.borderSoft}`,
            display: 'flex',
            alignItems: 'center',
            gap: 6,
          }}
        >
          {state === 'applied' && <CheckCircleOutlined style={{ fontSize: 14, color: RISK_COLORS.green }} />}
          <span style={{ fontSize: 13, color: state === 'applied' ? RISK_COLORS.green : RISK_COLORS.textDim }}>
            {state === 'applied'
              ? `${CONFIRM.appliedReply} · 操作人 张处长 · ${doneAt}`
              : `已驳回 · 退回 AI 重新起草 · ${doneAt}`}
          </span>
        </div>
      )}
    </div>
  );
}