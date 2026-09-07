// 三区骨架 + 顶栏 + 断点 + 证据抽屉（docs/chat-ux-spec-v1.md §2/§6/§9）
import { useCallback, useEffect, useState } from 'react';
import { FileSearchOutlined, MenuFoldOutlined, MenuUnfoldOutlined, SafetyOutlined } from '@ant-design/icons';
import { RISK_COLORS, WARN_TAG_TINTS } from '../risk/riskTheme';
import { accentAlpha, chatFocusRing, chatFontMono, chatHitRowBg } from './chatTokens';
import { useChatEngine, type ChatMessage } from './useChatEngine';
import type { EvidenceBlock } from './chatApi';
import { EVIDENCE } from '../proto/fakeData';
import SessionSidebar from './SessionSidebar';
import MessageFlow from './MessageFlow';
import ChatComposer from './ChatComposer';
import EvidenceDrawer from './EvidenceDrawer';

const SIDEBAR_KEY = 'chat.sidebar.collapsed';
const EASE = 'cubic-bezier(0.2, 0, 0, 1)';

function useViewport() {
  const [w, setW] = useState(() => window.innerWidth);
  useEffect(() => {
    const on = () => setW(window.innerWidth);
    window.addEventListener('resize', on);
    return () => window.removeEventListener('resize', on);
  }, []);
  return w;
}

export default function ChatShell() {
  const engine = useChatEngine();
  const session = engine.sessions.find((s) => s.key === engine.currentKey) ?? engine.sessions[0];
  const vw = useViewport();
  const overlayMode = vw < 1024;
  const drawerW = vw >= 1440 ? 400 : vw >= 1024 ? 360 : Math.min(400, Math.round(vw * 0.92));

  // 折叠态：localStorage 优先；无记录时 1024–1439 默认折叠（§2.4/§2.7）
  const [collapsed, setCollapsed] = useState(() => {
    const stored = localStorage.getItem(SIDEBAR_KEY);
    if (stored != null) return stored === '1';
    return window.innerWidth < 1440;
  });
  const toggleSidebar = useCallback(() => {
    setCollapsed((c) => {
      localStorage.setItem(SIDEBAR_KEY, c ? '0' : '1');
      return !c;
    });
  }, []);

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [auditId, setAuditId] = useState(EVIDENCE.audit);
  const [liveBlocks, setLiveBlocks] = useState<EvidenceBlock[] | undefined>(undefined);
  const openEvidence = useCallback((m?: ChatMessage) => {
    // 批 3：live 消息带真实证据载荷；fake 走剧本演示数据
    if (m?.mode === 'live' && m.evidence?.length) {
      setLiveBlocks(m.evidence);
      setAuditId('读实查 · ap_anping 六库');
    } else {
      setLiveBlocks(undefined);
      setAuditId(EVIDENCE.audit);
    }
    setDrawerOpen(true);
  }, []);

  // 顶栏开关：锚定当前会话最近一条带依据的 AI 回答；无则禁用（§6.1-3）
  const lastEvidenceMsg = [...session.messages].reverse().find((m) => m.role === 'ai' && m.blocks.length > 0);
  const evidenceAvail = lastEvidenceMsg !== undefined;

  const generatingKeys = Object.entries(engine.generating)
    .filter(([, v]) => v)
    .map(([k]) => k);
  const sessionGenerating = generatingKeys.includes(session.key);

  // §9.6/§9.1：CSS 变量注入，颜色全部来自 riskTheme / chatTokens
  const cssVars = {
    '--chat-accent': RISK_COLORS.accent,
    '--chat-surface': RISK_COLORS.surface,
    '--chat-panel-alt': RISK_COLORS.panelAlt,
    '--chat-border': RISK_COLORS.border,
    '--chat-border-soft': RISK_COLORS.borderSoft,
    '--chat-text': RISK_COLORS.text,
    '--chat-text-dim': RISK_COLORS.textDim,
    '--chat-text-faint': RISK_COLORS.textFaint,
    '--chat-hit-bg': chatHitRowBg,
    '--chat-hit-bar': RISK_COLORS.orange,
    '--chat-focus-ring': chatFocusRing,
    '--chat-focus-ring-strong': accentAlpha(0.12),
    '--chat-blue-tint': WARN_TAG_TINTS.BLUE.bg,
    '--chat-mono': chatFontMono,
  } as React.CSSProperties;

  return (
    <div
      className="chat-root"
      style={{
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        background: RISK_COLORS.ink,
        color: RISK_COLORS.text,
        ...cssVars,
      }}
    >
      {/* 顶栏 48px（§2.2） */}
      <header
        style={{
          height: 48,
          flexShrink: 0,
          background: RISK_COLORS.surface,
          borderBottom: `1px solid ${RISK_COLORS.borderSoft}`,
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          padding: '0 12px',
          position: 'relative',
          zIndex: 20,
        }}
      >
        <button
          className="chat-collapse-btn"
          onClick={toggleSidebar}
          title={collapsed ? '展开侧栏（⌘B）' : '折叠侧栏（⌘B）'}
          style={{
            width: 28,
            height: 28,
            borderRadius: 6,
            background: 'transparent',
            border: 0,
            cursor: 'pointer',
            color: RISK_COLORS.textDim,
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 16,
          }}
        >
          {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
        </button>
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
            }}
          >
            <SafetyOutlined style={{ color: '#fff', fontSize: 14 }} />
          </span>
          <span style={{ fontSize: 14, lineHeight: '22px', fontWeight: 600 }}>OntoRun 风险智能体</span>
        </div>
        <span
          title={session.label}
          style={{
            marginLeft: 4,
            fontSize: 14,
            lineHeight: '22px',
            color: RISK_COLORS.textDim,
            maxWidth: 320,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {session.label}
        </span>
        <span
          style={{
            fontSize: 12,
            lineHeight: '20px',
            color: RISK_COLORS.textFaint,
            background: RISK_COLORS.panelAlt,
            borderRadius: 4,
            padding: '1px 8px',
            whiteSpace: 'nowrap',
          }}
        >
          安平金控 · 监管口径 v0.3
        </span>
        <span style={{ flex: 1 }} />
        <button
          onClick={() => {
            if (!evidenceAvail) return;
            if (drawerOpen) {
              setDrawerOpen(false); // 再次点顶栏开关关闭（§6.3）
            } else {
              openEvidence();
            }
          }}
          disabled={!evidenceAvail}
          title={evidenceAvail ? '证据链' : '当前会话暂无带依据的回答'}
          style={{
            height: 28,
            borderRadius: 6,
            border: 0,
            cursor: evidenceAvail ? 'pointer' : 'default',
            padding: '0 10px',
            display: 'inline-flex',
            alignItems: 'center',
            gap: 6,
            fontSize: 13,
            lineHeight: '20px',
            color: drawerOpen ? RISK_COLORS.accent : evidenceAvail ? RISK_COLORS.text : RISK_COLORS.textFaint,
            background: drawerOpen ? WARN_TAG_TINTS.BLUE.bg : RISK_COLORS.surface,
          }}
        >
          <FileSearchOutlined style={{ fontSize: 16 }} />
          证据链
        </button>
        <span
          title="风险合规部 · 张处长（演示）"
          style={{
            width: 24,
            height: 24,
            borderRadius: '50%',
            background: RISK_COLORS.textDim,
            color: '#fff',
            fontSize: 12,
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          张
        </span>
      </header>

      {/* 左栏 + 中栏 */}
      <div style={{ flex: 1, display: 'flex', minHeight: 0, position: 'relative' }}>
        {overlayMode && !collapsed && (
          <div
            onClick={() => setCollapsed(true)}
            style={{ position: 'absolute', inset: 0, background: 'rgba(16, 24, 40, 0.32)', zIndex: 39 }}
          />
        )}
        <SessionSidebar
          sessions={[...engine.sessions]
            .sort((a, b) => Number(b.pinned ?? false) - Number(a.pinned ?? false))
            .map((s) => ({ key: s.key, label: s.label, pinned: s.pinned }))}
          currentKey={session.key}
          collapsed={collapsed}
          overlay={overlayMode}
          generatingKeys={generatingKeys}
          onSelect={engine.selectSession}
          onNew={() => {
            engine.newSession();
            if (overlayMode) setCollapsed(true);
          }}
          onDelete={engine.deleteSession}
          onRename={engine.renameSession}
          onTogglePin={engine.togglePin}
        />
        <main style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', background: RISK_COLORS.ink }}>
          <MessageFlow
            session={session}
            onAsk={(q) => engine.sendMessage(session.key, q)}
            onEvidence={openEvidence}
            onRetry={(id) => engine.retry(session.key, id)}
            onRegenerate={(id) => engine.regenerate(session.key, id)}
          />
          <ChatComposer
            generating={sessionGenerating}
            onSend={(t) => engine.sendMessage(session.key, t)}
            onStop={() => engine.stopGenerate(session.key)}
          />
        </main>

        {/* 右抽屉：overlay 不挤压中栏，200ms translateX（§2.6） */}
        <aside
          style={{
            position: 'absolute',
            top: 0,
            right: 0,
            bottom: 0,
            width: drawerW,
            boxSizing: 'border-box',
            background: RISK_COLORS.surface,
            borderLeft: `1px solid ${RISK_COLORS.borderSoft}`,
            boxShadow: '-6px 0 16px rgba(16, 24, 40, 0.08)',
            transform: drawerOpen ? 'translateX(0)' : 'translateX(100%)',
            visibility: drawerOpen ? 'visible' : 'hidden',
            transition: `transform 200ms ${EASE}, visibility 0s ${drawerOpen ? '0s' : '200ms'}`,
            zIndex: 30,
          }}
        >
          <EvidenceDrawer
            open={drawerOpen}
            auditId={auditId}
            onClose={() => setDrawerOpen(false)}
            liveBlocks={liveBlocks}
          />
        </aside>
      </div>
    </div>
  );
}