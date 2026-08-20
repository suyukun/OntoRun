// LLM 对话面板 —— 对接 /agent/chat 和 /agent/confirm 端点
import { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Button, Card, Input, Space, Tag, Typography, Spin, Alert } from 'antd';
import { RobotOutlined, UserOutlined, WarningOutlined } from '@ant-design/icons';
import { agentChat, agentConfirm } from '../api';
import type { AgentChatResponse } from '../types';

const { Text, Paragraph } = Typography;

interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  confirmCall?: {
    id: string;
    name: string;
    arguments: Record<string, unknown>;
  };
}

export default function ChatPanel() {
  const { t } = useTranslation();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [pendingConfirm, setPendingConfirm] = useState<{
    callId: string;
    name: string;
    args: Record<string, unknown>;
  } | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text) return;
    setInput('');
    const userMsg: ChatMessage = { role: 'user', content: text };
    setMessages((prev: ChatMessage[]) => [...prev, userMsg]);
    setLoading(true);

    try {
      const body: { message: string; session_id?: string } = { message: text };
      if (sessionId) body.session_id = sessionId;
      const res: AgentChatResponse = await agentChat(body);
      setSessionId(res.session_id);

      if (res.need_confirm) {
        const call = res.need_confirm;
        setPendingConfirm({ callId: call.id, name: call.name, args: call.arguments });
        const assistantMsg: ChatMessage = {
          role: 'assistant',
          content: t('chat.willExecute', { name: call.name }) + ' ' + JSON.stringify(call.arguments, null, 2),
          confirmCall: call,
        };
        setMessages((prev: ChatMessage[]) => [...prev, assistantMsg]);
      } else if (res.reply) {
        const reply = res.reply;
        const assistantMsg: ChatMessage = { role: 'assistant', content: reply };
        setMessages((prev: ChatMessage[]) => [...prev, assistantMsg]);
      }
    } catch (err) {
      const errMsg: ChatMessage = { role: 'system', content: t('chat.error', { msg: (err as Error).message }) };
      setMessages((prev: ChatMessage[]) => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async (confirmed: boolean) => {
    if (!pendingConfirm || !sessionId) return;
    const pc = pendingConfirm;
    setPendingConfirm(null);

    try {
      const res = await agentConfirm({ session_id: sessionId, call_id: pc.callId, confirmed });
      if (res.reply) {
        const reply = res.reply;
        const assistantMsg: ChatMessage = { role: 'assistant', content: reply };
        setMessages((prev: ChatMessage[]) => [...prev, assistantMsg]);
      }
    } catch (err) {
      const errMsg: ChatMessage = { role: 'system', content: t('chat.confirmFailed', { msg: (err as Error).message }) };
      setMessages((prev: ChatMessage[]) => [...prev, errMsg]);
    }
  };

  return (
    <Card
      title={
        <Space>
          <RobotOutlined />
          <span>{t('chat.title')}</span>
          {sessionId && <Tag color="green">{t('chat.sessionActive')}</Tag>}
        </Space>
      }
      style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
      styles={{ body: { flex: 1, display: 'flex', flexDirection: 'column', padding: 12 } }}
    >
      {/* 消息列表 */}
      <div style={{ flex: 1, overflowY: 'auto', marginBottom: 12, maxHeight: 400 }}>
        {messages.length === 0 && (
          <Paragraph type="secondary" style={{ textAlign: 'center', marginTop: 40 }}>
            {t('chat.emptyHint')}
          </Paragraph>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              marginBottom: 12,
              padding: 8,
              borderRadius: 8,
              background: msg.role === 'user' ? '#e6f7ff' : msg.role === 'system' ? '#fff2f0' : '#f6ffed',
              border: '1px solid ' + (msg.role === 'user' ? '#91d5ff' : msg.role === 'system' ? '#ffccc7' : '#b7eb8f'),
            }}
          >
            <Space>
              {msg.role === 'user' ? <UserOutlined /> : msg.role === 'system' ? <WarningOutlined /> : <RobotOutlined />}
              <Text strong>
                {msg.role === 'user' ? t('chat.you') : msg.role === 'system' ? t('chat.system') : t('chat.ai')}
              </Text>
            </Space>
            <Paragraph style={{ margin: '4px 0 0 0', whiteSpace: 'pre-wrap' }}>{msg.content}</Paragraph>
            {msg.confirmCall && (
              <div style={{ marginTop: 8 }}>
                <Alert
                  type="warning"
                  message={t('chat.confirmExecute') + ': ' + msg.confirmCall.name}
                  description={
                    <pre style={{ margin: 0, fontSize: 12 }}>{JSON.stringify(msg.confirmCall.arguments, null, 2)}</pre>
                  }
                />
                <Space style={{ marginTop: 8 }}>
                  <Button type="primary" size="small" onClick={() => void handleConfirm(true)} disabled={!pendingConfirm}>
                    {t('chat.confirmExecute')}
                  </Button>
                  <Button danger size="small" onClick={() => void handleConfirm(false)} disabled={!pendingConfirm}>
                    {t('chat.reject')}
                  </Button>
                </Space>
              </div>
            )}
          </div>
        ))}
        {loading && <Spin style={{ display: 'block', margin: '8px auto' }} />}
        <div ref={bottomRef} />
      </div>

      {/* 输入框 */}
      <Space.Compact style={{ width: '100%' }}>
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onPressEnter={() => void handleSend()}
          placeholder={t('chat.placeholder')}
          disabled={loading}
        />
        <Button type="primary" onClick={() => void handleSend()} loading={loading}>
          {t('chat.send')}
        </Button>
      </Space.Compact>
    </Card>
  );
}
