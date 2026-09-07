// 左栏会话列表 —— 展开 240 / 折叠 56 两态（docs/chat-ux-spec-v1.md §2.3/§2.4）
// 批 4：会话管理——置顶 / 重命名（行内编辑）/ 删除（Popconfirm）；条目 div[role=button]（内嵌操作按钮）
import { useEffect, useRef, useState } from 'react';
import { DeleteOutlined, EditOutlined, PlusOutlined, PushpinFilled, PushpinOutlined } from '@ant-design/icons';
import { Popconfirm } from 'antd';
import { RISK_COLORS } from '../risk/riskTheme';

export interface SidebarSession {
  key: string;
  label: string;
  pinned?: boolean;
}

interface Props {
  sessions: SidebarSession[];
  currentKey: string;
  collapsed: boolean;
  overlay: boolean;
  generatingKeys: string[];
  onSelect: (key: string) => void;
  onNew: () => void;
  onDelete: (key: string) => void;
  onRename: (key: string, label: string) => void;
  onTogglePin: (key: string) => void;
}

const EASE = 'cubic-bezier(0.2, 0, 0, 1)';
const iconBtnStyle = {
  width: 22,
  height: 22,
  borderRadius: 5,
  border: 0,
  background: 'transparent',
  cursor: 'pointer',
  display: 'inline-flex',
  alignItems: 'center',
  justifyContent: 'center',
  color: RISK_COLORS.textFaint,
  fontSize: 13,
  padding: 0,
} as const;

function SessionRow({
  session,
  current,
  generating,
  onSelect,
  onDelete,
  onRename,
  onTogglePin,
}: {
  session: SidebarSession;
  current: boolean;
  generating: boolean;
  onSelect: () => void;
  onDelete: () => void;
  onRename: (label: string) => void;
  onTogglePin: () => void;
}) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(session.label);
  const inputRef = useRef<HTMLInputElement>(null);
  useEffect(() => {
    if (editing) inputRef.current?.select();
  }, [editing]);

  const commit = () => {
    setEditing(false);
    if (draft.trim() && draft.trim() !== session.label) onRename(draft);
    else setDraft(session.label);
  };

  return (
    <div
      className="chat-session-item"
      title={session.label}
      style={{
        position: 'relative',
        display: 'flex',
        alignItems: 'center',
        gap: 4,
        width: '100%',
        height: 36,
        borderRadius: 6,
        padding: '0 8px 0 12px',
        fontSize: 13,
        lineHeight: '20px',
        textAlign: 'left',
        color: RISK_COLORS.text,
        background: current ? RISK_COLORS.panelAlt : undefined,
      }}
    >
      {current && (
        <span style={{ position: 'absolute', left: 0, top: 10, width: 2, height: 16, borderRadius: 1, background: RISK_COLORS.accent }} />
      )}
      {session.pinned && !editing && (
        <PushpinFilled style={{ fontSize: 11, color: RISK_COLORS.accent, flexShrink: 0 }} aria-label="已置顶" />
      )}
      {editing ? (
        <input
          ref={inputRef}
          value={draft}
          onChange={(e) => setDraft(e.target.value.slice(0, 20))}
          onKeyDown={(e) => {
            if (e.key === 'Enter') commit();
            if (e.key === 'Escape') {
              setDraft(session.label);
              setEditing(false);
            }
          }}
          onBlur={commit}
          aria-label="重命名会话"
          style={{
            flex: 1,
            minWidth: 0,
            fontSize: 13,
            lineHeight: '20px',
            border: `1px solid ${RISK_COLORS.accent}`,
            borderRadius: 4,
            padding: '2px 6px',
            outline: 'none',
            fontFamily: 'inherit',
            color: RISK_COLORS.text,
            background: '#fff',
          }}
        />
      ) : (
        <button
          type="button"
          className="chat-session-main"
          onClick={onSelect}
          title={session.label}
          aria-current={current || undefined}
          style={{
            flex: 1,
            minWidth: 0,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
            textAlign: 'left',
            fontSize: 13,
            lineHeight: '20px',
            fontFamily: 'inherit',
            background: 'transparent',
            border: 0,
            padding: 0,
            cursor: 'pointer',
            color: RISK_COLORS.text,
          }}
        >
          {session.label}
        </button>
      )}
      {generating ? (
        <span title="生成中" style={{ display: 'inline-flex', gap: 3, alignItems: 'center', paddingRight: 2 }}>
          <span className="chat-dot" />
          <span className="chat-dot" />
          <span className="chat-dot" />
        </span>
      ) : (
        !editing && (
          <span className="chat-more" style={{ display: 'inline-flex', alignItems: 'center', gap: 2 }} onClick={(e) => e.stopPropagation()}>
            <button
              type="button"
              className="chat-icon-btn"
              title={`${session.pinned ? '取消置顶' : '置顶'} ${session.label}`}
              aria-label={`${session.pinned ? '取消置顶' : '置顶'} ${session.label}`}
              style={iconBtnStyle}
              onClick={onTogglePin}
            >
              {session.pinned ? <PushpinFilled style={{ color: RISK_COLORS.accent }} /> : <PushpinOutlined />}
            </button>
            <button
              type="button"
              className="chat-icon-btn"
              title="重命名"
              aria-label={`重命名 ${session.label}`}
              style={iconBtnStyle}
              onClick={() => {
                setDraft(session.label);
                setEditing(true);
              }}
            >
              <EditOutlined />
            </button>
            <Popconfirm
              title="删除会话"
              description="删除后不可恢复，确认？"
              okText="删除"
              cancelText="取消"
              onConfirm={onDelete}
            >
              <button
                type="button"
                className="chat-icon-btn"
                title="删除"
                aria-label={`删除 ${session.label}`}
                style={{ ...iconBtnStyle, color: RISK_COLORS.red }}
              >
                <DeleteOutlined />
              </button>
            </Popconfirm>
          </span>
        )
      )}
    </div>
  );
}

export default function SessionSidebar({
  sessions,
  currentKey,
  collapsed,
  overlay,
  generatingKeys,
  onSelect,
  onNew,
  onDelete,
  onRename,
  onTogglePin,
}: Props) {
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
          {sessions.map((s) => (
            <SessionRow
              key={s.key}
              session={s}
              current={s.key === currentKey}
              generating={generatingKeys.includes(s.key)}
              onSelect={() => onSelect(s.key)}
              onDelete={() => onDelete(s.key)}
              onRename={(label) => onRename(s.key, label)}
              onTogglePin={() => onTogglePin(s.key)}
            />
          ))}
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
                  position: 'relative',
                }}
              >
                {s.label.slice(0, 1)}
                {s.pinned && (
                  <span
                    aria-hidden
                    style={{ position: 'absolute', top: -1, right: -1, width: 7, height: 7, borderRadius: 4, background: RISK_COLORS.accent }}
                  />
                )}
              </button>
            );
          })}
        </div>
      )}
    </nav>
  );
}