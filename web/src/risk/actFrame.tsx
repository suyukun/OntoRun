// 七幕剧本帧公共外壳 —— 统一的「第 N 幕」帧头 + 内容区。
// 浅色金融风；帧头带幕序徽章（accent 蓝）与标题/副标题。
import type { ReactNode } from 'react';
import { RISK_COLORS as C } from './riskTheme';

export function FrameShell({
  actNo,
  title,
  subtitle,
  children,
  accent = C.accent,
}: {
  actNo: string;
  title: string;
  subtitle?: string;
  children: ReactNode;
  accent?: string;
}) {
  return (
    <div
      data-testid={'act-frame-' + actNo}
      style={{ background: C.panel, border: '1px solid ' + C.border, borderRadius: 10, overflow: 'hidden' }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          padding: '14px 18px',
          borderBottom: '1px solid ' + C.border,
          background: C.panelAlt,
        }}
      >
        <span
          style={{
            flex: '0 0 auto',
            minWidth: 30,
            height: 30,
            paddingInline: 8,
            borderRadius: 8,
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: accent + '14',
            border: '1px solid ' + accent + '55',
            color: accent,
            fontWeight: 600,
            fontSize: 13,
          }}
        >
          {actNo}
        </span>
        <div style={{ minWidth: 0 }}>
          <div style={{ fontSize: 16, fontWeight: 600, letterSpacing: '-0.01em', color: C.text }}>{title}</div>
          {subtitle && (
            <div style={{ fontSize: 12.5, color: C.textFaint, marginTop: 2, lineHeight: 1.6 }}>{subtitle}</div>
          )}
        </div>
      </div>
      <div style={{ padding: 18 }}>{children}</div>
    </div>
  );
}

// 帧内小节标题
export function FrameSub({ children }: { children: ReactNode }) {
  return (
    <div style={{ fontSize: 12, color: C.textFaint, letterSpacing: '0.1em', margin: '18px 0 10px', fontWeight: 600 }}>
      {children}
    </div>
  );
}
