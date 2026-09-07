// 消息流 —— Bubble.List（@ant-design/x 内置 autoscroll 引擎：贴底/上滑停跟/回底重贴，Safari 兼容）
// 本组件不实现任何 stick-to-bottom 逻辑；onScroll 仅驱动 §8.5「回到底部」按钮可见性与未读数（视觉按规格）。
import { useCallback, useEffect, useRef, useState, type ReactNode } from 'react';
import { ArrowDownOutlined } from '@ant-design/icons';
import { Bubble } from '@ant-design/x';
import type { BubbleItemType } from '@ant-design/x';
import type { BubbleListRef, RoleType } from '@ant-design/x/es/bubble/interface';
import { RISK_COLORS, WARN_TAG_TINTS } from '../risk/riskTheme';
import { chatUserBubbleBg } from './chatTokens';
import type { AiBlockState, ChatMessage, ChatSession } from './useChatEngine';
import EmptyState from './EmptyState';
import BlockText from './blocks/BlockText';
import BlockTable from './blocks/BlockTable';
import BlockChart from './blocks/BlockChart';
import BlockReport from './blocks/BlockReport';
import BlockTools from './blocks/BlockTools';
import BlockConfirm from './blocks/BlockConfirm';
import { ActionBar, AiHeader, ErrorCard, ThinkingSkeleton } from './MessageItem';

/** 每会话滚动位置独立记忆（§8.4；autoScroll 为 column-reverse，距底距离 = -scrollTop） */
const scrollMem = new Map<string, number>();

function distFromBottom(box: HTMLDivElement): number {
  const reversed = getComputedStyle(box).flexDirection === 'column-reverse';
  return reversed ? Math.max(0, -box.scrollTop) : Math.max(0, box.scrollHeight - box.scrollTop - box.clientHeight);
}

interface BlockPayload {
  block: AiBlockState;
  streaming: boolean;
  last: boolean;
}

function renderPayload(
  payload: BlockPayload,
  onEvidence: () => void,
  streaming: boolean,
  message?: ChatMessage,
): ReactNode {
  const b = payload.block;
  const wrap = (node: ReactNode) => (
    <div style={{ paddingLeft: 32 }} className="chat-fade-120">
      {node}
    </div>
  );
  switch (b.type) {
    case 'tools':
      return wrap(
        <BlockTools phase={b.toolsPhase ?? 'done'} stepStatus={b.stepStatus ?? []} stepLabels={b.stepLabels} />,
      );
    case 'text':
      return wrap(<BlockText md={b.md ?? ''} streaming={streaming && payload.last} />);
    case 'table':
      return wrap(<BlockTable onEvidence={onEvidence} />);
    case 'chart':
      return wrap(<BlockChart onEvidence={onEvidence} series={message?.chartSeries} />);
    case 'report':
      return wrap(<BlockReport phase={b.reportPhase ?? 'done'} />);
    case 'confirm':
      return wrap(
        <BlockConfirm
          onEvidence={onEvidence}
          live={message?.mode === 'live' && message.needConfirm
            ? { proposal: message.needConfirm.name, arguments: message.needConfirm.arguments }
            : undefined}
        />,
      );
  }
}

function buildMessageItems(session: ChatSession): BubbleItemType[] {
  const items: BubbleItemType[] = [];
  for (const message of session.messages) {
    if (message.role === 'user') {
      items.push({ key: message.id, role: 'user', content: message.text ?? '' });
      continue;
    }
    if (message.status === 'error') {
      items.push({ key: `${message.id}:error`, role: 'ai-error', content: message });
      continue;
    }
    if (message.status === 'thinking') {
      items.push({ key: `${message.id}:thinking`, role: 'ai-thinking', content: message, extraInfo: { time: message.time } });
      continue;
    }
    const last = message.blocks[message.blocks.length - 1];
    for (const b of message.blocks) {
      items.push({
        key: b.key,
        role: b === message.blocks[0] ? 'ai-head' : 'ai-body',
        content: { block: b, streaming: message.status === 'streaming', last: b === last } satisfies BlockPayload,
        extraInfo: { time: message.time, message },
      });
    }
    if (message.status === 'done' && message.blocks.length > 0) {
      items.push({ key: `${message.id}:ops`, role: 'ai-ops', content: message });
    }
  }
  return items;
}

interface Props {
  session: ChatSession;
  onAsk: (q: string) => void;
  onEvidence: (m: ChatMessage) => void;
  onRetry: (id: string) => void;
  onRegenerate: (id: string) => void;
}

export default function MessageFlow({ session, onAsk, onEvidence, onRetry, onRegenerate }: Props) {
  const listRef = useRef<BubbleListRef>(null);
  const [showBack, setShowBack] = useState(false);
  const [unread, setUnread] = useState(0);
  const sigRef = useRef('');

  // 会话切换：恢复该会话滚动位置（§8.4；首访无记忆 → 吸底，命令式操作，不挂监听）
  useEffect(() => {
    const box = listRef.current?.scrollBoxNativeElement;
    const remembered = scrollMem.get(session.key);
    const raf = requestAnimationFrame(() => {
      if (box) {
        const reversed = getComputedStyle(box).flexDirection === 'column-reverse';
        if (remembered === undefined) {
          box.scrollTop = reversed ? 0 : box.scrollHeight;
        } else {
          box.scrollTop = reversed ? -remembered : remembered;
        }
      }
      setShowBack(false);
      setUnread(0);
    });
    return () => cancelAnimationFrame(raf);
  }, [session.key]);

  // 未读数：出现新消息/新块且视口离底 > 80px 时 +1（§8.5；贴底判定归 X 内置引擎）
  useEffect(() => {
    const last = session.messages[session.messages.length - 1];
    const sig = `${session.messages.length}:${last?.blocks.length ?? 0}`;
    if (sig === sigRef.current) return;
    sigRef.current = sig;
    const box = listRef.current?.scrollBoxNativeElement;
    if (box && distFromBottom(box) > 80) setUnread((u) => u + 1);
  }, [session]);

  // X Bubble.List 自带 onScroll 透传：仅用于按钮可见性（贴底逻辑全部在内置引擎内）
  const onScroll = useCallback(
    (e: React.UIEvent<HTMLDivElement>) => {
      const d = distFromBottom(e.currentTarget);
      scrollMem.set(session.key, d);
      setShowBack(d > 80);
      if (d < 120) setUnread(0);
    },
    [session.key],
  );

  const goBottom = () => {
    listRef.current?.scrollTo({ top: 'bottom', behavior: 'smooth' });
    setShowBack(false);
    setUnread(0);
  };

  const roles: RoleType = {
    user: {
      placement: 'end',
      variant: 'filled',
      styles: {
        content: {
          background: chatUserBubbleBg,
          color: RISK_COLORS.text,
          fontSize: 15,
          lineHeight: '24px',
          maxWidth: 560,
          borderRadius: 12,
          borderTopRightRadius: 4,
          padding: '10px 14px',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
        },
      },
    },
    'ai-head': {
      placement: 'start',
      variant: 'borderless',
      styles: {
        content: { padding: 0, background: 'transparent', width: '100%' },
      },
    },
    'ai-body': {
      placement: 'start',
      variant: 'borderless',
      styles: {
        content: { padding: 0, background: 'transparent', width: '100%' },
        root: { marginLeft: 32, marginTop: 12 },
      },
    },
    'ai-thinking': {
      placement: 'start',
      variant: 'borderless',
      styles: {
        content: { padding: 0, background: 'transparent', width: '100%' },
      },
    },
    'ai-error': {
      placement: 'start',
      variant: 'borderless',
      styles: {
        content: { padding: 0, background: 'transparent', width: '100%' },
        root: { marginLeft: 32, marginTop: 20 },
      },
    },
    'ai-ops': {
      placement: 'start',
      variant: 'borderless',
      styles: {
        content: { padding: 0, background: 'transparent', width: '100%' },
        root: { marginLeft: 32, marginTop: 10, marginBottom: 28 },
      },
    },
  };

  const evidenceTarget = session.messages[session.messages.length - 1];
  const handlers = {
    onEvidence: () => onEvidence(evidenceTarget),
    onRetry,
    onRegenerate,
  };

  // contentRender 统一入口（role 配置内无法直接引用 handlers 前置声明，这里用函数式 role 注入）
  const rolesWithRender: RoleType = {
    ...roles,
    'ai-head': {
      ...roles['ai-head'],
      contentRender: (payload: BlockPayload, info) => (
        <div className="chat-fade-80">
          <AiHeader time={String(info.extraInfo?.time ?? '')} />
          <div style={{ marginTop: 8 }}>
            {renderPayload(
              payload,
              handlers.onEvidence,
              Boolean(payload.streaming),
              info.extraInfo?.message as ChatMessage | undefined,
            )}
          </div>
        </div>
      ),
    },
    'ai-body': {
      ...roles['ai-body'],
      contentRender: (payload: BlockPayload, info) =>
        renderPayload(
          payload,
          handlers.onEvidence,
          Boolean(payload.streaming),
          info.extraInfo?.message as ChatMessage | undefined,
        ),
    },
    'ai-thinking': {
      ...roles['ai-thinking'],
      contentRender: (m: ChatMessage, info) => (
        <div className="chat-fade-80">
          <AiHeader time={String(info.extraInfo?.time ?? '')} />
          <div style={{ marginTop: 8 }}>
            <ThinkingSkeleton hint={m.thinkingHint} stage={m.thinkingStage} />
          </div>
        </div>
      ),
    },
    'ai-error': {
      ...roles['ai-error'],
      contentRender: (m: ChatMessage) => <ErrorCard message={m} onRetry={() => onRetry(m.id)} />,
    },
    'ai-ops': {
      ...roles['ai-ops'],
      contentRender: (m: ChatMessage) => <ActionBar message={m} onEvidence={handlers.onEvidence} onRegenerate={() => onRegenerate(m.id)} />,
    },
  };

  const items: BubbleItemType[] = buildMessageItems(session);

  return (
    <div style={{ flex: 1, minHeight: 0, position: 'relative', display: 'flex' }}>
      {session.messages.length === 0 ? (
        <div style={{ flex: 1, overflowY: 'auto' }}>
          <EmptyState onAsk={onAsk} />
        </div>
      ) : (
        <Bubble.List
          ref={listRef}
          className="chat-bubbles"
          style={{ height: '100%', width: '100%' }}
          items={items}
          role={rolesWithRender}
          autoScroll
          onScroll={onScroll}
        />
      )}

      {/* 回到底部：输入区上方 12px，36x36 圆形白底 + 未读数圆标（§8.5 视觉；滚动机制为 X 内置） */}
      {showBack && (
        <button
          className="chat-fade-120"
          onClick={goBottom}
          title="回到底部"
          style={{
            position: 'absolute',
            bottom: 12,
            left: '50%',
            transform: 'translateX(-50%)',
            width: 36,
            height: 36,
            borderRadius: '50%',
            background: '#fff',
            border: `1px solid ${RISK_COLORS.borderSoft}`,
            boxShadow: '0 1px 2px rgba(16, 24, 40, 0.06)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: RISK_COLORS.textDim,
            zIndex: 20,
          }}
        >
          <ArrowDownOutlined style={{ fontSize: 16 }} />
          {unread > 0 && (
            <span
              style={{
                position: 'absolute',
                top: -6,
                right: -6,
                minWidth: 18,
                height: 18,
                borderRadius: 9,
                background: WARN_TAG_TINTS.BLUE.bg,
                color: RISK_COLORS.accent,
                fontSize: 12,
                lineHeight: '18px',
                textAlign: 'center',
                padding: '0 4px',
                fontVariantNumeric: 'tabular-nums',
              }}
            >
              {unread}
            </span>
          )}
        </button>
      )}
    </div>
  );
}