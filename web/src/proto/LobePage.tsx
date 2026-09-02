import { useEffect, useRef, useState } from 'react';
import { ConfigProvider as LobeConfigProvider, Markdown } from '@lobehub/ui';
import { motion } from 'motion/react';
import { Avatar, Button, Card, Input, List, Steps, Tag, Typography } from 'antd';
import { RobotOutlined, SendOutlined, UserOutlined } from '@ant-design/icons';
import EchartsBlock from './EchartsBlock';
import { CONFIRM, ECHOPT, EVIDENCE, REVEAL_TEXT, SESSIONS, TABLE_ROWS, TOOL_STEPS } from './fakeData';

type Block =
  | { type: 'user'; text: string }
  | { type: 'tools' }
  | { type: 'ai-text'; text: string }
  | { type: 'table' }
  | { type: 'chart' }
  | { type: 'confirm' };

const MD_TABLE = [
  '| 机构 | 敞口 | 占比 | 参考线 | 状态 |',
  '| --- | --- | --- | --- | --- |',
  ...TABLE_ROWS.map((r) => `| ${r.org} | ${r.exposure} | ${r.ratio} | ${r.ref} | ${r.level} |`),
].join('\n');

function AiRow({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
      <Avatar icon={<RobotOutlined />} style={{ background: '#fa8c16', flex: '0 0 auto' }} />
      <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', gap: 10 }}>{children}</div>
    </div>
  );
}

function UserRow({ text }: { text: string }) {
  return (
    <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
      <div style={{ background: '#1677ff', color: '#fff', borderRadius: 12, padding: '8px 12px', maxWidth: '70%' }}>{text}</div>
      <Avatar icon={<UserOutlined />} style={{ background: '#1677ff', flex: '0 0 auto' }} />
    </div>
  );
}

// @lobehub/ui 要求外部注入 motion 组件（避免 motion 多实例），否则整页抛错
// 选型信号：@lobehub/ui 自带嵌套 motion-dom，与顶层 motion 类型不同源，必须断言绕过
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const lobeMotion = motion as any;

export default function LobePage() {
  const [blocks, setBlocks] = useState<Block[]>([
    { type: 'user', text: '天晟集团的风险有多大？' },
    { type: 'tools' },
    { type: 'ai-text', text: '' },
    { type: 'table' },
    { type: 'chart' },
    { type: 'confirm' },
  ]);
  const [confirmState, setConfirmState] = useState<'idle' | 'applied' | 'rejected'>('idle');
  const [input, setInput] = useState('');
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    let i = 0;
    timer.current = setInterval(() => {
      i += 2;
      setBlocks((bs) => bs.map((b) => (b.type === 'ai-text' && b.text.length < REVEAL_TEXT.length ? { ...b, text: REVEAL_TEXT.slice(0, i) } : b)));
      if (i >= REVEAL_TEXT.length && timer.current) clearInterval(timer.current);
    }, 24);
    return () => {
      if (timer.current) clearInterval(timer.current);
    };
  }, []);

  const send = () => {
    const t = input.trim();
    if (!t) return;
    setBlocks((bs) => [...bs, { type: 'user', text: t }]);
    setInput('');
    setTimeout(() => {
      setBlocks((bs) => [...bs, { type: 'ai-text', text: '已按证据链复核：归集 10.8%（86.4 亿 ÷ 800 亿），橙色预警成立。需要我起草处置提议吗？（原型固定应答）' }]);
    }, 600);
  };

  return (
    <LobeConfigProvider motion={lobeMotion}>
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', background: '#f5f7fa' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 16px', background: '#fff', borderBottom: '1px solid #eee' }}>
        <b>原型对决 · B：@lobehub/ui</b>
        <Button size="small" href="/proto/antd-x">切换到 A：@ant-design/x</Button>
      </div>
      <div style={{ flex: 1, display: 'flex', minHeight: 0 }}>
        <div style={{ width: 240, borderRight: '1px solid #eee', background: '#fff', padding: 8, overflowY: 'auto' }}>
          <List
            size="small"
            dataSource={SESSIONS}
            renderItem={(s) => (
              <List.Item style={{ cursor: 'pointer', padding: '8px 10px', borderRadius: 8, background: s.key === 's1' ? '#e6f4ff' : undefined }}>
                <Typography.Text style={{ fontSize: 13 }}>{s.label}</Typography.Text>
              </List.Item>
            )}
          />
        </div>
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
          <div style={{ flex: 1, overflowY: 'auto', padding: '16px 24px', display: 'flex', flexDirection: 'column', gap: 12 }}>
            {blocks.map((b, i) => {
              if (b.type === 'user') return <UserRow key={i} text={b.text} />;
              if (b.type === 'ai-text')
                return (
                  <AiRow key={i}>
                    <div style={{ background: '#fff', border: '1px solid #eee', borderRadius: 12, padding: '10px 14px' }}>
                      <Markdown style={{ fontSize: 14 }}>{b.text}</Markdown>
                    </div>
                  </AiRow>
                );
              if (b.type === 'tools')
                return (
                  <AiRow key={i}>
                    <Card size="small" style={{ maxWidth: 620 }} styles={{ body: { padding: '8px 12px' } }}>
                      <Steps direction="vertical" size="small" items={TOOL_STEPS.map((s) => ({ title: s.title, description: s.description, status: s.status }))} />
                    </Card>
                  </AiRow>
                );
              if (b.type === 'table')
                return (
                  <AiRow key={i}>
                    <Card size="small" style={{ maxWidth: 620 }} styles={{ body: { padding: '4px 12px' } }}>
                      <Markdown style={{ fontSize: 13 }}>{MD_TABLE}</Markdown>
                    </Card>
                  </AiRow>
                );
              if (b.type === 'chart')
                return (
                  <AiRow key={i}>
                    <Card size="small" style={{ maxWidth: 620 }} styles={{ body: { padding: 8 } }}>
                      <EchartsBlock option={ECHOPT} height={200} />
                    </Card>
                  </AiRow>
                );
              return (
                <AiRow key={i}>
                  <Card size="small" style={{ maxWidth: 620, borderColor: '#fa8c16' }} title={CONFIRM.title}>
                    <Typography.Paragraph type="secondary" style={{ fontSize: 12.5 }}>{CONFIRM.reason}</Typography.Paragraph>
                    {confirmState === 'idle' ? (
                      <Button type="primary" onClick={() => setConfirmState('applied')}>确认执行（人拍板）</Button>
                    ) : (
                      <Tag color={confirmState === 'applied' ? 'green' : 'red'}>{confirmState === 'applied' ? CONFIRM.appliedReply : '已驳回 · 退回重新起草'}</Tag>
                    )}
                  </Card>
                </AiRow>
              );
            })}
          </div>
          <div style={{ padding: '12px 24px', background: '#fff', borderTop: '1px solid #eee', display: 'flex', gap: 8 }}>
            <Input.TextArea value={input} onChange={(e) => setInput(e.target.value)} onPressEnter={send} placeholder="问点啥…（原型固定应答）" autoSize={{ minRows: 1, maxRows: 4 }} />
            <Button type="primary" icon={<SendOutlined />} onClick={send} />
          </div>
        </div>
        <div style={{ width: 300, borderLeft: '1px solid #eee', background: '#fff', padding: 12, overflowY: 'auto' }}>
          <Card size="small" title="证据链">
            <p style={{ fontSize: 12.5, margin: '4px 0' }}><b>basis 表</b>{EVIDENCE.tables.map((t) => <Tag key={t} style={{ marginTop: 4 }}>{t}</Tag>)}</p>
            <p style={{ fontSize: 12.5, margin: '4px 0' }}><b>规则</b>{EVIDENCE.rules.map((t) => <Tag key={t} color="orange" style={{ marginTop: 4 }}>{t}</Tag>)}</p>
            <p style={{ fontSize: 12.5, margin: '4px 0' }}><b>分母</b>{EVIDENCE.denominator}</p>
            <p style={{ fontSize: 12.5, margin: '4px 0' }}><b>审计</b>{EVIDENCE.audit}</p>
          </Card>
        </div>
      </div>
    </div>
    </LobeConfigProvider>
  );
}
