// 风险对话窗口（/risk/chat）—— 精准问答 + 动作双签 + 域外拒答
// 对接 /agent/risk/chat + /agent/risk/confirm；会话持久化（localStorage，独立于 S1）。
// 双签流程：LLM 提议高风险动作 → 参数卡片 + 人机双签（确认/驳回）→ 执行结果 + 审计。
import { useEffect, useMemo, useRef, useState } from 'react';
import { Button, Input, Tag, Tooltip, Typography, Spin, ConfigProvider, theme as antdTheme } from 'antd';
import {
  AuditOutlined,
  CheckCircleFilled,
  CloseCircleFilled,
  DeleteOutlined,
  MessageOutlined,
  RobotOutlined,
  SafetyCertificateOutlined,
  SendOutlined,
  StopOutlined,
  UserOutlined,
  WarningFilled,
} from '@ant-design/icons';
import './risk.css';
import { RISK_COLORS, riskDarkTheme } from './riskTheme';
import { useRiskSnapshot, formatRiskValue } from './riskData';
import { EXAMPLE_PROMPTS, KIND_TAG } from './riskExamples';
import type { RiskActionMeta, RiskSnapshot } from './riskData';

const { Text, Paragraph } = Typography;

const MSGS_KEY = 'ontorun.risk.messages';
const SESSION_KEY = 'ontorun.risk.sessionId';

interface ConfirmInfo {
  callId: string;
  name: string;
  args: Record<string, unknown>;
}
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

  const quickReplyNeeded = (m: ChatMsg) =>
    m.role === 'assistant' && !m.decline && !m.confirm && /确认|同意|是否执行|请执行|是否同意/.test(m.content);

  return (
    <ConfigProvider theme={{ ...riskDarkTheme, algorithm: antdTheme.darkAlgorithm }}>
      <div className="risk-bg" style={{ minHeight: '100vh', color: RISK_COLORS.text, display: 'flex', flexDirection: 'column' }}>
        {/* 顶栏 */}
        <div style={{ borderBottom: '1px solid ' + RISK_COLORS.border, padding: '14px 28px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 10, background: RISK_COLORS.surface }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <RobotOutlined style={{ color: RISK_COLORS.accent, fontSize: 18 }} />
            <div>
              <div style={{ fontWeight: 700, fontSize: 15 }}>风险对话窗口</div>
              <div style={{ fontSize: 12, color: RISK_COLORS.textFaint }}>自然语言精准问答 · 动作双签 · 全程审计</div>
            </div>
            <Tag color="gold" style={{ marginLeft: 8 }}>人机双签</Tag>
            {sessionId && (
              <Tag style={{ background: 'rgba(61,220,151,0.12)', borderColor: RISK_COLORS.green, color: RISK_COLORS.green }}>会话活跃</Tag>
            )}
          </div>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <Tooltip title="清空当前会话（聊天记录与 session）">
              <Button size="small" icon={<DeleteOutlined />} onClick={clearAll} style={{ background: 'transparent', borderColor: RISK_COLORS.border, color: RISK_COLORS.textDim }}>
                清空会话
              </Button>
            </Tooltip>
          </div>
        </div>

        <div style={{ flex: 1, display: 'flex', minHeight: 0 }}>
          {/* 主对话区 */}
          <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column' }}>
            {/* 示例问题引导 */}
            {messages.length === 0 && (
              <div style={{ padding: '20px 28px 8px' }}>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                  {EXAMPLE_PROMPTS.map((p) => (
                    <button
                      key={p.label}
                      onClick={() => void handleSend(p.text)}
                      style={{
                        display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer',
                        background: 'rgba(242,176,76,0.06)', border: '1px solid ' + RISK_COLORS.border,
                        color: RISK_COLORS.text, borderRadius: 4, padding: '7px 12px', fontSize: 12.5,
                      }}
                      aria-label={'示例问题：' + p.label}
                    >
                      <span style={{ width: 6, height: 6, borderRadius: '50%', background: KIND_TAG[p.kind].color, flex: '0 0 auto' }} />
                      {p.label}
                    </button>
                  ))}
                </div>
                <div style={{ marginTop: 10, fontSize: 12, color: RISK_COLORS.textFaint }}>
                  点一下上面的示例问题，或直接输入；<span style={{ color: RISK_COLORS.accent }}>橙色（双签）</span>示例会演示"AI 提议 → 参数卡片 → 人机双签 → 执行 + 审计"的完整闭环。
                </div>
              </div>
            )}

            {/* 消息列表 */}
            <div style={{ flex: 1, overflowY: 'auto', padding: '16px 28px 8px' }}>
              {messages.length === 0 && (
                <div style={{ textAlign: 'center', padding: '60px 0', color: RISK_COLORS.textFaint }}>
                  <MessageOutlined style={{ fontSize: 30, marginBottom: 12, display: 'block' }} />
                  向系统提问，例如"本月新增红色预警信号有几条？"
                </div>
              )}
              {messages.map((m) => (
                <div key={m.id} style={{ marginBottom: 14, display: 'flex', gap: 10 }}>
                  <div
                    style={{
                      width: 30, height: 30, borderRadius: 6, flex: '0 0 auto', display: 'flex', alignItems: 'center', justifyContent: 'center',
                      background: m.role === 'user' ? 'rgba(76,141,255,0.16)' : m.role === 'system' ? 'rgba(240,82,77,0.16)' : 'rgba(242,176,76,0.14)',
                      color: m.role === 'user' ? RISK_COLORS.blue : m.role === 'system' ? RISK_COLORS.red : RISK_COLORS.accent,
                    }}
                  >
                    {m.role === 'user' ? <UserOutlined /> : m.role === 'system' ? <WarningFilled /> : <RobotOutlined />}
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 12, color: RISK_COLORS.textFaint, marginBottom: 4 }}>
                      {m.role === 'user' ? '我' : m.role === 'system' ? '系统提示' : 'AI 助手'}
                    </div>
                    {m.decline ? (
                      <div style={{ ...panel(), borderColor: RISK_COLORS.red, borderLeft: '3px solid ' + RISK_COLORS.red, padding: 14 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                          <StopOutlined style={{ color: RISK_COLORS.red }} />
                          <span style={{ fontWeight: 700, color: RISK_COLORS.red, fontSize: 13.5 }}>超出系统可答范围（fail-closed 拒答）</span>
                        </div>
                        <Paragraph style={{ color: RISK_COLORS.textDim, margin: 0, fontSize: 13.5, whiteSpace: 'pre-wrap', lineHeight: 1.7 }}>{m.content}</Paragraph>
                      </div>
                    ) : (
                      <div style={{ ...panel(), padding: 14, background: m.role === 'user' ? 'rgba(76,141,255,0.05)' : RISK_COLORS.panel }}>
                        <Paragraph style={{ margin: 0, color: m.role === 'user' ? RISK_COLORS.text : RISK_COLORS.text, fontSize: 13.5, whiteSpace: 'pre-wrap', lineHeight: 1.75 }}>{m.content}</Paragraph>

                        {/* 双签卡片 */}
                        {m.confirm && (
                          <ConfirmCard
                            confirm={m.confirm}
                            actionMeta={actionMeta.get(m.confirm.name)}
                            resolved={m.confirmResolved}
                            confirmReply={m.confirmReply}
                            disabled={!!m.confirmResolved || confirming}
                            onConfirm={(v) => void handleConfirm(v)}
                          />
                        )}

                        {/* 文本提议后的快捷确认（推动到参数卡片） */}
                        {quickReplyNeeded(m) && (
                          <Button
                            size="small"
                            type="primary"
                            icon={<CheckCircleFilled />}
                            style={{ marginTop: 10, background: RISK_COLORS.accent, borderColor: RISK_COLORS.accent, color: RISK_COLORS.accentText }}
                            onClick={() => void handleSend('我确认，请执行')}
                          >
                            我确认，请执行
                          </Button>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {loading && (
                <div style={{ display: 'flex', gap: 10 }}>
                  <div style={{ width: 30, height: 30, borderRadius: 6, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(242,176,76,0.14)', color: RISK_COLORS.accent }}>
                    <RobotOutlined />
                  </div>
                  <div style={{ ...panel(), padding: '12px 16px' }}><Spin size="small" /> <Text style={{ color: RISK_COLORS.textDim, fontSize: 12.5, marginLeft: 8 }}>正在通过业务本体理解问题…</Text></div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>

            {/* 输入框 */}
            <div style={{ padding: '10px 28px 20px', borderTop: '1px solid ' + RISK_COLORS.border, background: RISK_COLORS.surface }}>
              <div style={{ display: 'flex', gap: 10 }}>
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onPressEnter={() => void handleSend()}
                  placeholder="输入风险问题或指令（例：把某条黄色预警升为红色）…"
                  disabled={loading}
                  variant="filled"
                  style={{ background: RISK_COLORS.ink, borderColor: RISK_COLORS.border, color: RISK_COLORS.text }}
                />
                <Button
                  type="primary"
                  icon={<SendOutlined />}
                  loading={loading}
                  style={{ background: RISK_COLORS.accent, borderColor: RISK_COLORS.accent, color: RISK_COLORS.accentText }}
                  onClick={() => void handleSend()}
                >
                  发送
                </Button>
              </div>
            </div>
          </div>

          {/* 右侧：可查域 + 演示建议 */}
          <SidePanel snapshot={snapshot} />
        </div>
      </div>
    </ConfigProvider>
  );
}

// ---- 双签卡片（高光时刻） ----
function ConfirmCard({
  confirm,
  actionMeta,
  resolved,
  confirmReply,
  disabled,
  onConfirm,
}: {
  confirm: ConfirmInfo;
  actionMeta?: RiskActionMeta;
  resolved?: 'applied' | 'rejected' | 'error' | null;
  confirmReply?: string;
  disabled: boolean;
  onConfirm: (v: boolean) => void;
}) {
  return (
    <div style={{ marginTop: 12, border: '1px solid ' + RISK_COLORS.accent, borderRadius: 6, background: 'rgba(242,176,76,0.05)', overflow: 'hidden' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 14px', background: 'rgba(242,176,76,0.10)', borderBottom: '1px solid rgba(242,176,76,0.25)' }}>
        <SafetyCertificateOutlined style={{ color: RISK_COLORS.accent }} />
        <span style={{ fontWeight: 700, fontSize: 13.5 }}>高风险动作 · 人机双签</span>
        <Tag color="gold" style={{ marginLeft: 'auto' }}>AI 只提议 · 人类确认后才执行</Tag>
      </div>
      <div style={{ padding: '12px 14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10, flexWrap: 'wrap' }}>
          <span style={{ fontSize: 15, fontWeight: 700 }}>{confirm.name}</span>
          <Tag style={{ color: RISK_COLORS.textDim, borderColor: RISK_COLORS.border, background: RISK_COLORS.panel }}>{actionMeta?.description || '风控动作'}</Tag>
        </div>
        <div style={{ border: '1px solid ' + RISK_COLORS.border, borderRadius: 6, overflow: 'hidden', marginBottom: 12 }}>
          {Object.entries(confirm.args).map(([k, v]) => (
            <div key={k} style={{ display: 'flex', borderBottom: '1px solid ' + RISK_COLORS.border, background: RISK_COLORS.panel }}>
              <div style={{ width: 130, flex: '0 0 auto', padding: '8px 12px', color: RISK_COLORS.textDim, fontSize: 12.5, borderRight: '1px solid ' + RISK_COLORS.border, background: 'rgba(148,163,184,0.05)' }}>
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
            <Button type="primary" icon={<CheckCircleFilled />} disabled={disabled} style={{ background: RISK_COLORS.accent, borderColor: RISK_COLORS.accent, color: RISK_COLORS.accentText }} onClick={() => onConfirm(true)}>
              确认执行
            </Button>
            <Button danger icon={<CloseCircleFilled />} disabled={disabled} style={{ borderColor: RISK_COLORS.red, color: RISK_COLORS.red, background: 'transparent' }} onClick={() => onConfirm(false)}>
              驳回
            </Button>
          </div>
        ) : (
          <div style={{ fontSize: 13 }}>
            <span style={{ color: resolved === 'applied' ? RISK_COLORS.green : RISK_COLORS.red, fontWeight: 600 }}>
              {resolved === 'applied' ? '✓ 已执行（真实写回 + 审计留痕）' : resolved === 'rejected' ? '✕ 已驳回，未执行任何写回' : '✕ 执行出错'}
            </span>
            {confirmReply && <div style={{ color: RISK_COLORS.textDim, marginTop: 6, whiteSpace: 'pre-wrap', fontSize: 12.5 }}>{confirmReply}</div>}
          </div>
        )}
      </div>
    </div>
  );
}

function paramTitle(actionMeta: RiskActionMeta | undefined, key: string): string {
  return actionMeta?.params_schema?.properties?.[key]?.title ?? key;
}

function isDecline(reply: string): boolean {
  return /^DECLINE/i.test(reply) || /无法|不能.*(计算|查询|导出|预测)|超出.*(范围|可表达集)/.test(reply.slice(0, 120));
}

// ---- 右侧可查域面板 ----
function SidePanel({ snapshot }: { snapshot: RiskSnapshot | null }) {
  const objs = snapshot?.meta.objects.filter((o) => (snapshot.totals[o.api_name] ?? 0) > 0) ?? [];
  const acts = snapshot?.meta.actions ?? [];
  return (
    <div className="risk-side-panel" style={{ width: 280, flex: '0 0 auto', borderLeft: '1px solid ' + RISK_COLORS.border, padding: '18px 20px', background: RISK_COLORS.surface }}>
      <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 4, display: 'flex', alignItems: 'center', gap: 8 }}>
        <AuditOutlined style={{ color: RISK_COLORS.accent }} /> 我可查/可办范围
      </div>
      <div style={{ fontSize: 12, color: RISK_COLORS.textFaint, marginBottom: 14 }}>域外问题会明确拒答并引导，不编数字。</div>
      <div style={{ fontSize: 12.5, color: RISK_COLORS.textDim, marginBottom: 8 }}>可查对象</div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 16 }}>
        {objs.map((o) => (
          <Tag key={o.api_name} style={{ color: RISK_COLORS.text, borderColor: RISK_COLORS.border, background: RISK_COLORS.panel }}>
            {o.description.replace(/（.*?）.*$/, '').replace(/（.*$/, '')}
          </Tag>
        ))}
      </div>
      <div style={{ fontSize: 12.5, color: RISK_COLORS.textDim, marginBottom: 8 }}>风控动作（{acts.length} 类）</div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {acts.map((a) => (
          <div key={a.name} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12.5, color: RISK_COLORS.textDim }}>
            {a.high_risk ? (
              <Tag color="volcano" style={{ fontSize: 10, lineHeight: '16px', paddingInline: 5 }}>双签</Tag>
            ) : (
              <span style={{ width: 14 }} />
            )}
            <span>{a.name}</span>
          </div>
        ))}
      </div>
      <div style={{ marginTop: 18, borderTop: '1px solid ' + RISK_COLORS.border, paddingTop: 12, fontSize: 12, color: RISK_COLORS.textFaint, lineHeight: 1.7 }}>
        <WarningFilled style={{ color: RISK_COLORS.yellow, marginRight: 4 }} />
        演示建议：先问一个精准问题，再点橙色"双签"示例，最后问一个巴塞尔问题看拒答。
      </div>
    </div>
  );
}

function panel() {
  return {
    background: RISK_COLORS.panel,
    border: '1px solid ' + RISK_COLORS.border,
    borderRadius: 6,
  };
}
