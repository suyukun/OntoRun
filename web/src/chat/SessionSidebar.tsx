// 左栏会话列表 —— 展开 240 / 折叠 56 两态（docs/chat-ux-spec-v1.md §2.3/§2.4）
import { MoreOutlined, PlusOutlined } from '@ant-design/icons';
import { RISK_COLORS } from '../risk/riskTheme';

interface Props {
  sessions: { key: string; label: string }[];
  currentKey: string;
  collapsed: boolean;
  overlay: boolean;
  generatingKeys: string[];
  onSelect: (key: string) => void;
  onNew: () => void;
}

const EASE = 'cubic-bezier(0.2, 0, 0, 1)';

export default function SessionSidebar({ sessions, currentKey, collapsed, overlay, generatingKeys, onSelect, onNew }: Props) {
  const expandedVisible = overlay || !collapsed;

  return (
    <nav
      aria-label="会话列表"
      style={{
        width: overlay ? 240 : collapsed ? 56 : 240,
        boxSizing: 'border-box',
        flexShrink: 0,
        background: '#fff',
        borderRight: `1px solid ${RISK_COLORS.borderSoft}`,
        padding: 8,
        overflow: 'hidden',
        position: overlay ? 'absolute' : 'relative',
        left: 0,
        top: 0,
        bottom: 0,
        zIndex: overlay ? 40 : 'auto',
        transform: overlay && collapsed ? 'translateX(-100%)' : 'none',
        transition: overlay
          ? `transform 200ms ${EASE}`
          : `width 180ms ${EASE}`,
      }}
    >
      {/* 展开态内容（固定 224 宽防文字挤压闪烁，§2.4） */}
      <div
        style={{
          position: 'absolute',
          top: 8,
          left: 8,
          width: 224,
          opacity: expandedVisible ? 1 : 0,
          transition: expandedVisible ? `opacity 120ms ${EASE} 60ms` : `opacity 60ms ${EASE}`,
          pointerEvents: expandedVisible ? 'auto' : 'none',
        }}
      >
        <button
          onClick={onNew}
          title="新建对话"
          style={{
            width: '100%',
            height: 36,
            borderRadius: 6,
            background: RISK_COLORS.accent,
            color: '#fff',
            fontSize: 13,
            border: 0,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 6,
          }}
        >
          <PlusOutlined style={{ fontSize: 16 }} />
          新建对话
        </button>
        <div style={{ fontSize: 12, lineHeight: '20px', color: RISK_COLORS.textFaint, padding: '8px 12px 0' }}>今天</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {sessions.map((s) => {
            const current = s.key === currentKey;
            const gen = generatingKeys.includes(s.key) && !current;
            return (
              <button
                type="button"
                key={s.key}
                className="chat-session-item"
                onClick={() => onSelect(s.key)}
                title={s.label}
                aria-current={current || undefined}
                style={{
                  position: 'relative',
                  display: 'flex',
                  alignItems: 'center',
                  width: '100%',
                  height: 36,
                  borderRadius: 6,
                  padding: '0 12px',
                  cursor: 'pointer',
                  fontSize: 13,
                  lineHeight: '20px',
                  fontFamily: 'inherit',
                  textAlign: 'left',
                  border: 0,
                  color: RISK_COLORS.text,
                  // 非当前项不写内联底色：hover 底 panelAlt 交给 .chat-session-item:hover（§2.3）
                  background: current ? RISK_COLORS.panelAlt : undefined,
                }}
              >
                {current && (
                  <span
                    style={{ position: 'absolute', left: 0, top: 10, width: 2, height: 16, borderRadius: 1, background: RISK_COLORS.accent }}
                  />
                )}
                <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{s.label}</span>
                <span style={{ flex: 1 }} />
                {gen ? (
                  <span title="生成中" style={{ display: 'inline-flex', gap: 3, alignItems: 'center', paddingRight: 2 }}>
                    <span className="chat-dot" />
                    <span className="chat-dot" />
                    <span className="chat-dot" />
                  </span>
                ) : (
                  <MoreOutlined className="chat-more" title="更多（演示版未开放）" style={{ fontSize: 16, color: RISK_COLORS.textFaint }} />
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* 折叠态内容（仅非 overlay；最多 5 个会话首字圆标，§2.4） */}
      {!overlay && (
        <div
          style={{
            position: 'absolute',
            top: 8,
            left: 8,
            width: 40,
            opacity: collapsed ? 1 : 0,
            transition: collapsed ? `opacity 60ms ${EASE}` : `opacity 120ms ${EASE} 60ms`,
            pointerEvents: collapsed ? 'auto' : 'none',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 8,
          }}
        >
          <button
            onClick={onNew}
            title="新建对话"
            style={{
              width: 40,
              height: 40,
              borderRadius: 6,
              background: RISK_COLORS.accent,
              color: '#fff',
              border: 0,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <PlusOutlined style={{ fontSize: 16 }} />
          </button>
          {sessions.slice(0, 5).map((s) => {
            const current = s.key === currentKey;
            return (
              <button
                key={s.key}
                title={s.label}
                onClick={() => onSelect(s.key)}
                style={{
                  width: 28,
                  height: 28,
                  borderRadius: 14,
                  background: current ? RISK_COLORS.accent : RISK_COLORS.panelAlt,
                  color: current ? '#fff' : RISK_COLORS.textFaint,
                  fontSize: 12,
                  border: 0,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  padding: 0,
                }}
              >
                {s.label.slice(0, 1)}
              </button>
            );
          })}
        </div>
      )}
    </nav>
  );
}
