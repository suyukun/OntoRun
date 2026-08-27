// 风险对话面板（数据工作台右栏）—— 精准问答 + 动作双签 + 域外拒答。
// 对接 /agent/risk/chat + /agent/risk/confirm；会话持久化（localStorage key 与原独立页一致）。
// 双签卡片见 ConfirmCard.tsx；本组件不持有 ConfigProvider/页面底色：主题由 RiskShell 统一提供。
import { useEffect, useMemo, useRef, useState } from 'react';
import { Button, Collapse, Input, Tag, Tooltip, Typography, Spin } from 'antd';
import {
  AuditOutlined,
  CheckCircleFilled,
  DeleteOutlined,
  MessageOutlined,
  RobotOutlined,
  SendOutlined,
  StopOutlined,
  UserOutlined,
  WarningFilled,
} from '@ant-design/icons';
import './risk.css';
import ConfirmCard from './ConfirmCard';
import type { ConfirmInfo } from './ConfirmCard';
import { RISK_COLORS as C, WARN_TAG_TINTS } from './riskTheme';
import { useRiskSnapshot, formatRiskValue } from './riskData';
import { EXAMPLE_PROMPTS, KIND_TAG } from './riskExamples';
import type { RiskActionMeta, RiskSnapshot } from './riskData';

const { Text, Paragraph } = Typography;

const MSGS_KEY = 'ontorun.risk.messages';
const SESSION_KEY = 'ontorun.risk.sessionId';

interface ChatMsg {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  decline?: boolean;
  confirm?: ConfirmInfo | null;
  confirmResolved?: 'applied' | 'rejected' | 'error' | null;
  confirmReply?: string;
}

const uid = () => Math.random().toString(36).slice(2, 10);

function loadMessages(): ChatMsg[] {
  try {
    const raw = localStorage.getItem(MSGS_KEY);
    return raw ? (JSON.parse(raw) as ChatMsg[]) : [];
  } catch {
    return [];
  }
}
function loadSessionId(): string | null {
  try {
    return localStorage.getItem(SESSION_KEY);
  } catch {
    return null;
  }
}
function avatarTint(role: ChatMsg['role']): { bg: string; fg: string } {
  if (role === 'user') return { bg: C.blue + '1A', fg: C.blue };
  if (role === 'system') return { bg: C.red + '1A', fg: C.red };
  return { bg: C.accent + '14', fg: C.accent };
}
const quickReplyNeeded = (m: ChatMsg) =>
  m.role === 'assistant' && !m.decline && !m.confirm && /确认|同意|是否执行|请执行|是否同意/.test(m.content);

export default function RiskChatPanel() {
  const [messages, setMessages] = useState<ChatMsg[]>(loadMessages);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(loadSessionId);
  const [confirming, setConfirming] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const { data: snapshot } = useRiskSnapshot();

  const actionMeta = useMemo(() => {
    const map = new Map<string, RiskActionMeta>();
    (snapshot?.meta.actions ?? []).forEach((a) => map.set(a.name, a));
    return map;
  }, [snapshot]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [messages, loading]);

  useEffect(() => {
    try {
      localStorage.setItem(MSGS_KEY, JSON.stringify(messages));
    } catch {
      // ignore
    }
  }, [messages]);
  useEffect(() => {
    try {
      if (sessionId) localStorage.setItem(SESSION_KEY, sessionId);
      else localStorage.removeItem(SESSION_KEY);
    } catch {
      // ignore
    }
  }, [sessionId]);

  const pendingConfirm = useMemo(() => {
    for (let i = messages.length - 1; i >= 0; i--) {
      const m = messages[i];
      if (m.confirm && !m.confirmResolved) return { msg: m, confirm: m.confirm };
      if (m.role === 'user') return null;
    }
    return null;
  }, [messages]);

  const append = (m: Omit<ChatMsg, 'id'>) => setMessages((prev) => [...prev, { ...m, id: uid() }]);

  const handleSend = async (text?: string) => {
    const content = (text ?? input).trim();
    if (!content || loading) return;
    setInput('');
    append({ role: 'user', content });
    setLoading(true);
    try {
      const body: { message: string; session_id?: string } = { message: content };
      if (sessionId) body.session_id = sessionId;
      const res = await fetch('/api/agent/risk/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const json = (await res.json()) as {
        session_id: string;
        reply?: string;
        need_confirm?: { id: string; name: string; arguments: Record<string, unknown> } | null;
      };
      if (!res.ok) throw new Error('HTTP ' + res.status + ': ' + (json as { error?: { message: string } }).error?.message);
      if (json.session_id) setSessionId(json.session_id);

      if (json.need_confirm) {
        append({
          role: 'assistant',
          content: json.reply || '系统提议执行一个高风险动作，请人机双签确认。',
          confirm: { callId: json.need_confirm.id, name: json.need_confirm.name, args: json.need_confirm.arguments },
        });
      } else if (json.reply) {
        append({ role: 'assistant', content: json.reply, decline: isDecline(json.reply) });
      }
    } catch (err) {
      append({ role: 'system', content: '请求失败：' + (err as Error).message + '。请确认后端服务已启动（含 DEEPSEEK_API_KEY）。' });
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async (confirmed: boolean) => {
    if (!pendingConfirm || !sessionId || confirming) return;
    const { msg, confirm } = pendingConfirm;
    setConfirming(true);
    try {
      const res = await fetch('/api/agent/risk/confirm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, call_id: confirm.callId, confirmed }),
      });
      const json = (await res.json()) as { reply?: string; outcome?: string };
      if (!res.ok) throw new Error('HTTP ' + res.status + ': ' + (json as { error?: { message: string } }).error?.message);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === msg.id
            ? { ...m, confirmResolved: confirmed ? (json.outcome === 'applied' ? 'applied' : 'rejected') : 'rejected', confirmReply: json.reply }
            : m,
        ),
      );
      if (json.reply) append({ role: 'assistant', content: json.reply });
    } catch (err) {
      setMessages((prev) => prev.map((m) => (m.id === msg.id ? { ...m, confirmResolved: 'error', confirmReply: (err as Error).message } : m)));
    } finally {
      setConfirming(false);
    }
  };

  const clearAll = () => {
    setMessages([]);
    setSessionId(null);
  };

  return (
    <div style={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column', background: C.surface }}>
      {/* 栏头 */}
      <div style={{ borderBottom: '1px solid ' + C.border, padding: '12px 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8, flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, minWidth: 0 }}>
          <RobotOutlined style={{ color: C.accent, fontSize: 18 }} />
          <div>
            <div style={{ fontWeight: 600, letterSpacing: '-0.01em', fontSize: 15 }}>风险对话 · 人机双签</div>
            <div style={{ fontSize: 11.5, color: C.textFaint }}>自然语言精准问答 · 动作双签 · 全程审计</div>
          </div>
          <Tag style={{ marginLeft: 4, background: WARN_TAG_TINTS.YELLOW.bg, borderColor: WARN_TAG_TINTS.YELLOW.border }}>人机双签</Tag>
          {sessionId && (
            <Tag style={{ color: C.green, background: C.green + '14', borderColor: C.green + '66' }}>会话活跃</Tag>
          )}
        </div>
        <Tooltip title="清空当前会话（聊天记录与 session）">
          <Button size="small" icon={<DeleteOutlined />} onClick={clearAll}>清空会话</Button>
        </Tooltip>
      </div>

      {/* 示例问题引导（空会话时） */}
      {messages.length === 0 && (
        <div style={{ padding: '14px 16px 6px', borderBottom: '1px solid ' + C.borderSoft }}>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {EXAMPLE_PROMPTS.map((p) => (
              <button
                key={p.label}
                onClick={() => void handleSend(p.text)}
                style={{
                  display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer',
                  background: C.panelAlt, border: '1px solid ' + C.border,
                  color: C.text, borderRadius: 6, padding: '7px 12px', fontSize: 12.5,
                }}
                aria-label={'示例问题：' + p.label}
              >
                <span style={{ width: 6, height: 6, borderRadius: '50%', background: KIND_TAG[p.kind].color, flex: '0 0 auto' }} />
                {p.label}
              </button>
            ))}
          </div>
          <div style={{ marginTop: 10, fontSize: 12, color: C.textFaint, paddingBottom: 6 }}>
            点一下上面的示例问题，或直接输入；<span style={{ color: C.yellow }}>橙色（双签）</span>示例会演示"AI 提议 → 参数卡片 → 人机双签 → 执行 + 审计"的完整闭环。
          </div>
        </div>
      )}

      {/* 消息列表（独立滚动） */}
      <div style={{ flex: 1, minHeight: 0, overflowY: 'auto', padding: '14px 16px 8px' }}>
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', padding: '48px 0', color: C.textFaint }}>
            <MessageOutlined style={{ fontSize: 28, marginBottom: 12, display: 'block' }} />
            向系统提问，例如"本月新增红色预警信号有几条？"
          </div>
        )}
        {messages.map((m) => (
          <MessageRow
            key={m.id}
            m={m}
            actionMeta={actionMeta.get(m.confirm?.name ?? '')}
            disabled={!!m.confirmResolved || confirming}
            onConfirm={(v) => void handleConfirm(v)}
            onQuick={() => void handleSend('我确认，请执行')}
          />
        ))}
        {loading && (
          <div style={{ display: 'flex', gap: 10 }}>
            <AvatarChip role="assistant" />
            <div style={bubble()}><Spin size="small" /> <Text style={{ color: C.textDim, fontSize: 12.5, marginLeft: 8 }}>正在通过业务本体理解问题…</Text></div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* 我可查/可办范围（折叠条，替代原独立页的右侧宽栏） */}
      <ScopePanel snapshot={snapshot} />

      {/* 输入框 */}
      <div style={{ padding: '10px 16px 14px', borderTop: '1px solid ' + C.border }}>
        <div style={{ display: 'flex', gap: 8 }}>
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onPressEnter={() => void handleSend()}
            placeholder="输入风险问题或指令（例：把某条黄色预警升为红色）…"
            aria-label="风险问题输入框"
            disabled={loading}
          />
          <Button type="primary" icon={<SendOutlined />} loading={loading} onClick={() => void handleSend()}>
            发送
          </Button>
        </div>
      </div>
    </div>
  );
}

function AvatarChip({ role }: { role: ChatMsg['role'] }) {
  const tint = avatarTint(role);
  return (
    <div style={{ width: 30, height: 30, borderRadius: 6, flex: '0 0 auto', display: 'flex', alignItems: 'center', justifyContent: 'center', background: tint.bg, color: tint.fg }}>
      {role === 'user' ? <UserOutlined /> : role === 'system' ? <WarningFilled /> : <RobotOutlined />}
    </div>
  );
}

function bubble(extra?: React.CSSProperties): React.CSSProperties {
  return { background: C.panel, border: '1px solid ' + C.borderSoft, borderRadius: 8, ...(extra ?? {}) };
}

function MessageRow({
  m, actionMeta, disabled, onConfirm, onQuick,
}: {
  m: ChatMsg;
  actionMeta?: RiskActionMeta;
  disabled: boolean;
  onConfirm: (v: boolean) => void;
  onQuick: () => void;
}) {
  return (
    <div style={{ marginBottom: 14, display: 'flex', gap: 10 }}>
      <AvatarChip role={m.role} />
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 12, color: C.textFaint, marginBottom: 4 }}>
          {m.role === 'user' ? '我' : m.role === 'system' ? '系统提示' : 'AI 助手'}
        </div>
        {m.decline ? (
          <div style={{ ...bubble(), borderColor: C.red, borderLeft: '3px solid ' + C.red, padding: 14 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
              <StopOutlined style={{ color: C.red }} />
              <span style={{ fontWeight: 600, color: C.red, fontSize: 13.5 }}>超出系统可答范围（fail-closed 拒答）</span>
            </div>
            <Paragraph style={{ color: C.textDim, margin: 0, fontSize: 13.5, whiteSpace: 'pre-wrap', lineHeight: 1.7 }}>{m.content}</Paragraph>
          </div>
        ) : (
          <div style={bubble({ padding: 14, background: m.role === 'user' ? C.blue + '0D' : C.panel, borderColor: m.role === 'user' ? C.blue + '33' : C.borderSoft })}>
            <Paragraph style={{ margin: 0, color: C.text, fontSize: 13.5, whiteSpace: 'pre-wrap', lineHeight: 1.75 }}>{m.content}</Paragraph>

            {m.confirm && (
              <ConfirmCard
                confirm={m.confirm}
                actionMeta={actionMeta}
                resolved={m.confirmResolved}
                confirmReply={m.confirmReply}
                disabled={disabled}
                onConfirm={onConfirm}
              />
            )}

            {!m.confirm && quickReplyNeeded(m) && (
              <Button size="small" type="primary" icon={<CheckCircleFilled />} style={{ marginTop: 10 }} onClick={onQuick}>
                我确认，请执行
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function isDecline(reply: string): boolean {
  return /^DECLINE/i.test(reply) || /无法|不能.*(计算|查询|导出|预测)|超出.*(范围|可表达集)/.test(reply.slice(0, 120));
}

// ---- 可查域 + 演示建议（折叠条；域外明确拒答、不编数字） ----
function ScopePanel({ snapshot }: { snapshot: RiskSnapshot | null }) {
  const objs = snapshot?.meta.objects.filter((o) => (snapshot.totals[o.api_name] ?? 0) > 0) ?? [];
  const acts = snapshot?.meta.actions ?? [];
  return (
    <div style={{ borderTop: '1px solid ' + C.border }}>
      <Collapse
        ghost
        size="small"
        items={[
          {
            key: 'scope',
            label: (
              <span style={{ fontSize: 12.5, fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                <AuditOutlined style={{ color: C.accent }} /> 我可查/可办范围
                <span style={{ color: C.textFaint, fontWeight: 400 }}>· 域外明确拒答，不编数字</span>
              </span>
            ),
            children: (
              <div style={{ paddingTop: 2 }}>
                <div style={{ fontSize: 12, color: C.textDim, marginBottom: 6 }}>可查对象</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 12 }}>
                  {objs.map((o) => (
                    <Tag key={o.api_name} style={{ color: C.text, borderColor: C.border, background: C.panelAlt }}>
                      {o.description.replace(/（.*?）.*$/, '').replace(/（.*$/, '')}
                    </Tag>
                  ))}
                </div>
                <div style={{ fontSize: 12, color: C.textDim, marginBottom: 6 }}>风控动作（{acts.length} 类）</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
                  {acts.map((a) => (
                    <div key={a.name} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12.5, color: C.textDim }}>
                      {a.high_risk ? (
                        <Tag style={{ background: WARN_TAG_TINTS.YELLOW.bg, borderColor: WARN_TAG_TINTS.YELLOW.border, fontSize: 10, lineHeight: '16px', paddingInline: 5 }}>双签</Tag>
                      ) : (
                        <span style={{ width: 14 }} />
                      )}
                      <span>{a.name}</span>
                    </div>
                  ))}
                </div>
                <div style={{ marginTop: 12, paddingTop: 8, borderTop: '1px dashed ' + C.border, fontSize: 12, color: C.textFaint, lineHeight: 1.7 }}>
                  <WarningFilled style={{ color: C.yellow, marginRight: 4 }} />
                  演示建议：先问一个精准问题，再点橙色"双签"示例，最后问一个巴塞尔问题看拒答。
                </div>
              </div>
            ),
          },
        ]}
      />
    </div>
  );
}
