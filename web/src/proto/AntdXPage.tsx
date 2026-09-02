import { useEffect, useRef, useState } from 'react';
import { Bubble, Conversations, Sender, ThoughtChain } from '@ant-design/x';
import { Avatar, Button, Card, Table, Tag, Typography } from 'antd';
import { RobotOutlined, UserOutlined } from '@ant-design/icons';
import EchartsBlock from './EchartsBlock';
import { CONFIRM, ECHOPT, EVIDENCE, REVEAL_TEXT, SESSIONS, TABLE_ROWS, TOOL_STEPS } from './fakeData';

type Block =
  | { type: 'user'; text: string }
  | { type: 'tools' }
  | { type: 'ai-text'; text: string }
  | { type: 'table' }
  | { type: 'chart' }
  | { type: 'confirm' };

const FULL_REPLY = REVEAL_TEXT;

export default function AntdXPage() {
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

  // 开场流式模拟：逐字点亮揭示文本
  useEffect(() => {
    let i = 0;
    timer.current = setInterval(() => {
      i += 2;
      setBlocks((bs) => bs.map((b) => (b.type === 'ai-text' && b.text.length < FULL_REPLY.length ? { ...b, text: FULL_REPLY.slice(0, i) } : b)));
      if (i >= FULL_REPLY.length && timer.current) clearInterval(timer.current);
    }, 24);
    return () => {
      if (timer.current) clearInterval(timer.current);
    };
  }, []);

  const send = (text: string) => {
    const t = text.trim();
    if (!t) return;
    setBlocks((bs) => [...bs, { type: 'user', text: t }]);
    setInput('');
    setTimeout(() => {
      setBlocks((bs) => [...bs, { type: 'ai-text', text: '已按证据链复核：归集 10.8%（86.4 亿 ÷ 800 亿），橙色预警成立。需要我起草处置提议吗？（原型固定应答）' }]);
    }, 600);
  };

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', background: '#f5f7fa' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 16px', background: '#fff', borderBottom: '1px solid #eee' }}>
        <b>原型对决 · A：@ant-design/x</b>
        <Button size="small" href="/proto/lobe-ui">切换到 B：@lobehub/ui</Button>
      </div>
      <div style={{ flex: 1, display: 'flex', minHeight: 0 }}>
        {/* 左：会话列表 */}
        <div style={{ width: 240, borderRight: '1px solid #eee', background: '#fff', padding: 8, overflowY: 'auto' }}>
          <Conversations items={SESSIONS} activeKey="s1" onActiveChange={() => {}} style={{ width: '100%' }} />
        </div>
        {/* 中：对话流 */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
          <div style={{ flex: 1, overflowY: 'auto', padding: '16px 24px', display: 'flex', flexDirection: 'column', gap: 12 }}>
            {blocks.map((b, i) => {
              if (b.type === 'user')
                return (
                  <Bubble key={i} placement="end" avatar={<Avatar icon={<UserOutlined />} style={{ background: '#1677ff' }} />} content={b.text} variant="filled" />
                );
              if (b.type === 'ai-text')
                return <Bubble key={i} avatar={<Avatar icon={<RobotOutlined />} style={{ background: '#fa8c16' }} />} content={<Typography.Paragraph style={{ marginBottom: 0 }}>{b.text}</Typography.Paragraph>} variant="shadow" />;
              if (b.type === 'tools')
                return <ThoughtChain key={i} items={TOOL_STEPS.map((s) => ({ title: s.title, description: s.description, status: s.status === 'finish' ? ('success' as const) : ('loading' as const) }))} style={{ marginLeft: 44 }} />;
              if (b.type === 'table')
                return (
                  <Card key={i} size="small" style={{ marginLeft: 44, maxWidth: 620 }} styles={{ body: { padding: 8 } }}>
                    <Table size="small" pagination={false} dataSource={TABLE_ROWS} rowKey={(r) => r.org} columns={[
                      { title: '机构', dataIndex: 'org' },
                      { title: '敞口', dataIndex: 'exposure' },
                      { title: '占比', dataIndex: 'ratio' },
                      { title: '参考线', dataIndex: 'ref' },
                      { title: '状态', dataIndex: 'level', render: (v) => <Tag color={v === '橙色预警' ? 'orange' : v === '触达' ? 'gold' : 'green'}>{v}</Tag> },
                    ]} />
                  </Card>
                );
              if (b.type === 'chart')
                return (
                  <Card key={i} size="small" style={{ marginLeft: 44, maxWidth: 620 }} styles={{ body: { padding: 8 } }}>
                    <EchartsBlock option={ECHOPT} height={200} />
                  </Card>
                );
              return (
                <Card key={i} size="small" style={{ marginLeft: 44, maxWidth: 620, borderColor: '#fa8c16' }} title={CONFIRM.title}>
                  <Typography.Paragraph type="secondary" style={{ fontSize: 12.5 }}>{CONFIRM.reason}</Typography.Paragraph>
                  {confirmState === 'idle' ? (
                    <Button type="primary" onClick={() => setConfirmState('applied')}>确认执行（人拍板）</Button>
                  ) : (
                    <Tag color={confirmState === 'applied' ? 'green' : 'red'}>{confirmState === 'applied' ? CONFIRM.appliedReply : '已驳回 · 退回重新起草'}</Tag>
                  )}
                </Card>
              );
            })}
          </div>
          <div style={{ padding: '12px 24px', background: '#fff', borderTop: '1px solid #eee' }}>
            <Sender value={input} onChange={setInput} onSubmit={send} placeholder="问点啥…（原型固定应答）" />
          </div>
        </div>
        {/* 右：证据链 */}
        <div style={{ width: 300, borderLeft: '1px solid #eee', background: '#fff', padding: 12, overflowY: 'auto' }}>
          <Card size="small" title="证据链">
            <p style={{ fontSize: 12.5, margin: '4px 0' }}><b> basis 表</b>{EVIDENCE.tables.map((t) => <Tag key={t} style={{ marginTop: 4 }}>{t}</Tag>)}</p>
            <p style={{ fontSize: 12.5, margin: '4px 0' }}><b>规则</b>{EVIDENCE.rules.map((t) => <Tag key={t} color="orange" style={{ marginTop: 4 }}>{t}</Tag>)}</p>
            <p style={{ fontSize: 12.5, margin: '4px 0' }}><b>分母</b>{EVIDENCE.denominator}</p>
            <p style={{ fontSize: 12.5, margin: '4px 0' }}><b>审计</b>{EVIDENCE.audit}</p>
          </Card>
        </div>
      </div>
    </div>
  );
}
