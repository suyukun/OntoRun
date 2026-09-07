// 消息级展示组件（docs/chat-ux-spec-v1.md §4.3/§4.4/§8.2/§8.3）
// 滚动/打字机制由 @ant-design/x 内置实现；本文件只含规格视觉的纯组件。
import { Button } from 'antd';
import { CloseCircleOutlined, CopyOutlined, RedoOutlined, SafetyOutlined } from '@ant-design/icons';
import { EVIDENCE } from '../proto/fakeData';
import { RISK_COLORS, WARN_TAG_TINTS } from '../risk/riskTheme';
import type { ChatMessage } from './useChatEngine';

/** 消息头行：24 logo + 风险智能体 + 常显时点（§4.3）；块内容在其下缩进 32 */
export function AiHeader({ time }: { time: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <span
        style={{
          width: 24,
          height: 24,
          borderRadius: 6,
          background: RISK_COLORS.accent,
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
        }}
      >
        <SafetyOutlined style={{ color: '#fff', fontSize: 14 }} />
      </span>
      <span style={{ fontSize: 13, lineHeight: '20px', color: RISK_COLORS.textDim }}>风险智能体</span>
      <span style={{ fontSize: 12, lineHeight: '20px', color: RISK_COLORS.textFaint, fontVariantNumeric: 'tabular-nums' }}>{time}</span>
    </div>
  );
}

/** 思考中骨架（§8.2：两行 60%/40%；>8s 追加业务提示行） */
export function ThinkingSkeleton({ hint }: { hint?: boolean }) {
  return (
    <div style={{ paddingLeft: 32 }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        <div className="chat-skel" style={{ width: '60%' }} />
        <div className="chat-skel" style={{ width: '40%' }} />
      </div>
      {hint && <div style={{ marginTop: 8, fontSize: 12, color: RISK_COLORS.textFaint }}>正在核对口径与阈值…</div>}
    </div>
  );
}

/** §8.3 错误卡：消息流内留痕，重试重发原问题 */
export function ErrorCard({ message, onRetry }: { message: ChatMessage; onRetry: () => void }) {
  return (
    <div
      className="chat-fade-120"
      style={{
        background: WARN_TAG_TINTS.RED.bg,
        border: `1px solid ${WARN_TAG_TINTS.RED.border}`,
        borderRadius: 8,
        padding: '12px 14px',
        display: 'flex',
        alignItems: 'center',
        gap: 8,
      }}
    >
      <CloseCircleOutlined style={{ color: RISK_COLORS.red, fontSize: 16 }} />
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 13, lineHeight: '20px', fontWeight: 600, color: RISK_COLORS.red }}>本次回答生成失败</div>
        <div style={{ fontSize: 12.5, lineHeight: '20px', color: RISK_COLORS.textDim }}>{message.errorReason}</div>
      </div>
      <Button size="small" onClick={onRetry}>
        重试
      </Button>
    </div>
  );
}

/** §4.4 操作条：信任入口常显 + hover 追加复制/重新生成 */
export function ActionBar({ message, onEvidence, onRegenerate }: { message: ChatMessage; onEvidence: () => void; onRegenerate: () => void }) {
  return (
    <div className="chat-msg-bar" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <button
        className="chat-link"
        title="查看证据链"
        onClick={onEvidence}
        style={{ background: 'none', border: 0, padding: 0, fontSize: 13, lineHeight: '20px' }}
      >
        {message.mode === 'live'
          ? `查看证据链 · 证据 ${message.evidence?.length ?? 0} 项`
          : `查看证据链 · 审计 ${EVIDENCE.audit}`}
      </button>
      <span style={{ flex: 1 }} />
      <button
        className="chat-icon-btn chat-hover-reveal"
        title="复制整条回答（Markdown）"
        onClick={() => {
          const md = message.blocks
            .filter((b) => b.type === 'text')
            .map((b) => b.mdFull ?? '')
            .join('\n\n');
          void navigator.clipboard?.writeText(md).catch(() => undefined);
        }}
      >
        <CopyOutlined />
      </button>
      <button className="chat-icon-btn chat-hover-reveal" title="重新生成" onClick={onRegenerate}>
        <RedoOutlined />
      </button>
    </div>
  );
}