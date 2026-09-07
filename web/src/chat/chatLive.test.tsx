/// <reference types="vitest/globals" />
// 批 3 smoke：live 模式契约（fetch mock）——会话连续性 / 真实载荷渲染 / 证据抽屉 / 图表派生 /
// 错误重试 / need_confirm 不写回。按「脚手架 smoke 级」只锁主路径契约。
import { describe, it, expect, beforeAll, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { message as antdMessage } from 'antd';
import ChatRoutes from './index';
import { chartSeriesFromEvidence, intentLabel, setChatModeOverride } from './chatApi';
import type { ChatApiResponse } from './chatApi';

vi.mock('./blocks/BlockChart', () => ({
  default: vi.fn((props: { series?: unknown }) => (
    <div data-testid="chart-block" data-series={JSON.stringify(props.series ?? null)} />
  )),
}));

beforeAll(() => {
  (globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = false;
  Object.defineProperty(window, 'innerWidth', { configurable: true, value: 1440 });
  class IOStub {
    observe() {}
    unobserve() {}
    disconnect() {}
    takeRecords() {
      return [];
    }
  }
  (globalThis as unknown as { IntersectionObserver?: unknown }).IntersectionObserver ??= IOStub;
});

const REPLY = '归集集中度 **10.8%** 超预警线 **10%**，橙色预警成立。';

/** SSE 流 mock（批 4-②）：工具直播帧 + token 帧 + final 帧 */
const sse = (frames: object[]): Response =>
  new Response(
    new ReadableStream({
      start(c) {
        const enc = new TextEncoder();
        for (const fr of frames) c.enqueue(enc.encode(`data: ${JSON.stringify(fr)}

`));
        c.close();
      },
    }),
    { status: 200, headers: { 'Content-Type': 'text/event-stream' } },
  );

const okResponse = (overrides: Partial<ChatApiResponse>, withTools = true): Response =>
  sse([
    ...(withTools
      ? [
          { type: 'tool_start', name: 'risk_query:group_customer' },
          { type: 'tool_result', name: 'risk_query:group_customer', outcome: 'ok' },
          { type: 'tool_start', name: 'act1_group_reveal' },
          { type: 'tool_result', name: 'act1_group_reveal', outcome: 'ok' },
        ]
      : []),
    { type: 'token', text: overrides.reply ?? REPLY },
    {
      type: 'final',
      session_id: 'sess_test1',
      reply: REPLY,
      need_confirm: null,
      outcome: 'ok',
      evidence: null,
      ...overrides,
    },
  ]);

const revealRow = {
  row_ref: 'customer.ap_subsidiary_credit_detail#group=GRP-1&org=安平银行',
  org_name: '安平银行',
  ratio_display: '8.0%',
  org_reference_ratio: 0.08,
};
const EVIDENCE = [
  { intent: 'risk_query:group_customer', conclusion: '查询 group_customer 命中 1 行', basis_tables: ['customer.ap_group_customer'], rules_hits: [], denominator: null, detail_rows: [] },
  { intent: 'act1_group_reveal', conclusion: '天晟集团 归集 10.8%', basis_tables: ['customer.ap_subsidiary_credit_detail'], rules_hits: [{ rule: 'R1a', name: '集团层归集集中度', clause: '金控办法第三十二/三十三条', lines: '关注 9%/预警 10%/限额 12%', computed: { ratio: 0.108 } }], denominator: { name: '集团并表资本', value_yi: 800, source: 'base.ap_sys_param' }, detail_rows: [revealRow] },
];

function mockFetchSeq(handlers: Array<() => Response | Promise<Response>>) {
  const fn = vi.fn();
  handlers.forEach((h) => fn.mockImplementationOnce(h));
  vi.stubGlobal('fetch', fn);
  return fn;
}

function renderChat() {
  return render(
    <MemoryRouter initialEntries={['/chat']}>
      <ChatRoutes />
    </MemoryRouter>,
  );
}

async function sendAndSettle(text: string) {
  const ta = screen.getByRole('textbox');
  fireEvent.change(ta, { target: { value: text } });
  fireEvent.keyDown(ta, { key: 'Enter' });
  // 回答完成 = 操作条出现（status done）
  await screen.findAllByText(/查看证据链/, undefined, { timeout: 20000 });
}

describe('载荷派生纯函数（intent 标签 / 图表序列）', () => {
  it('intentLabel：risk_query 前缀 / 剧本幕次 / 兜底原文', () => {
    expect(intentLabel('risk_query:warning_signal')).toBe('实查 warning_signal');
    expect(intentLabel('act1_group_reveal')).toBe('第 1 幕 · 逐家归集揭示');
    expect(intentLabel('act4_approval_chain')).toBe('第 4 幕 · 处置审批链');
    expect(intentLabel('custom_tool')).toBe('custom_tool');
  });

  it('chartSeriesFromEvidence：org 行 + R1a 集团行；无占比载荷返回 null', () => {
    const evs = [
      { intent: 'x', detail_rows: [{ org_name: '安平银行', ratio_display: '8.0%', org_reference_ratio: 0.08 }] },
      { intent: 'y', rules_hits: [{ rule: 'R1a', computed: { ratio: 0.108 } }] },
    ];
    expect(chartSeriesFromEvidence(evs)).toEqual([
      { org: '安平银行', ratio: 8, refRatio: 8, isGroup: false },
      { org: '集团归集', ratio: 10.8, refRatio: null, isGroup: true },
    ]);
    expect(chartSeriesFromEvidence([{ intent: 'x', detail_rows: [{ pk: 1 }] }])).toBeNull();
  });
});

describe('live 真实问数契约（批 3）', () => {
  beforeEach(() => {
    setChatModeOverride('live');
    vi.spyOn(antdMessage, 'info').mockImplementation(() => undefined as never);
  });
  afterEach(() => {
    setChatModeOverride(null);
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
    cleanup();
  });

  it('chip 提问 → 请求载荷正确 + 会话连续（第二条带 session_id）+ 回答与证据项渲染', async () => {
    const fetchFn = mockFetchSeq([
      () => okResponse({ session_id: 'sess_test1', evidence: EVIDENCE }),
      () => okResponse({ session_id: 'sess_test1', evidence: [] }),
    ]);
    renderChat();
    await screen.findByText('今天要看什么风险？');

    fireEvent.click(screen.getByText('天晟集团有限公司现在有什么风险预警？'));
    await screen.findByText('查看证据链 · 证据 2 项', undefined, { timeout: 20000 });

    expect(fetchFn).toHaveBeenCalledTimes(1);
    const [url1, init1] = fetchFn.mock.calls[0];
    expect(String(url1)).toBe('/api/agent/risk/chat/stream');
    const body1 = JSON.parse(String(init1?.body));
    expect(body1.message).toBe('天晟集团有限公司现在有什么风险预警？');
    expect(body1.session_id).toBeUndefined();
    expect(init1?.headers?.['X-Actor']).toBe('human');

    // tools 完成态折叠摘要（§5.5）= 直播步数；正文 = 真实 reply
    expect(screen.getAllByText('实查 2 项 · 证据链随答返回').length).toBeGreaterThan(0);
    await waitFor(() => expect(screen.getAllByText(/10.8%/).length).toBeGreaterThan(0));

    // 第二条：会话连续性
    await sendAndSettle('分母是什么？');
    expect(fetchFn).toHaveBeenCalledTimes(2);
    const body2 = JSON.parse(String(fetchFn.mock.calls[1][1]?.body));
    expect(body2.session_id).toBe('sess_test1');

    // 批 3.1：首答后侧栏会话自动以问题命名（真实列表，无 fake 条目）
    expect(screen.getAllByText('天晟集团有限公司现在有什').length).toBeGreaterThanOrEqual(2);
  }, 60000);

  it('证据抽屉渲染真实载荷（basis 表/命中规则/分母/明细行引用）', async () => {
    mockFetchSeq([() => okResponse({ evidence: EVIDENCE })]);
    renderChat();
    await screen.findByText('今天要看什么风险？');
    await sendAndSettle('天晟集团有限公司现在有什么风险预警？');

    fireEvent.click(screen.getByText('查看证据链 · 证据 2 项'));
    expect(await screen.findByText('customer.ap_group_customer')).toBeInTheDocument();
    expect(screen.getByText('R1a · 集团层归集集中度')).toBeInTheDocument();
    expect(screen.getByText('集团并表资本')).toBeInTheDocument();
    expect(screen.getByText(/800 亿/)).toBeInTheDocument();
    expect(screen.getByText(/ap_subsidiary_credit_detail#group=GRP-1/)).toBeInTheDocument();
  }, 60000);

  it('画图提问 + 揭示载荷 → 图表块收到派生序列（真实数字，不手写）', async () => {
    mockFetchSeq([() => okResponse({ evidence: EVIDENCE })]);
    renderChat();
    await screen.findByText('今天要看什么风险？');
    await sendAndSettle('画一张天晟集团各机构占比与预警线的对比图');

    const chart = await screen.findByTestId('chart-block', undefined, { timeout: 20000 });
    const series = JSON.parse(chart.getAttribute('data-series') ?? 'null');
    expect(series).toEqual([
      { org: '安平银行', ratio: 8, refRatio: 8, isGroup: false },
      { org: '集团归集', ratio: 10.8, refRatio: null, isGroup: true },
    ]);
  }, 60000);

  it('HTTP 500 → 错误卡；重试重发原问题成功', async () => {
    const fetchFn = mockFetchSeq([
      () => new Response(JSON.stringify({ detail: 'boom' }), { status: 500 }),
      () => okResponse({ evidence: [] }),
    ]);
    renderChat();
    await screen.findByText('今天要看什么风险？');

    fireEvent.click(screen.getByText('天晟集团有限公司现在有什么风险预警？'));
    await screen.findByText('本次回答生成失败', undefined, { timeout: 20000 });
    expect(screen.getByText(/服务异常|网络异常/)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /重\s*试/ }));
    await screen.findByText('查看证据链 · 证据 0 项', undefined, { timeout: 20000 });
    expect(fetchFn).toHaveBeenCalledTimes(2);
    expect(JSON.parse(String(fetchFn.mock.calls[1][1]?.body)).message).toBe('天晟集团有限公司现在有什么风险预警？');
  }, 60000);

  it('need_confirm → confirm 卡展示真实提议；拍板不发起写回请求（批 3 只接问数）', async () => {
    const fetchFn = mockFetchSeq([
      () =>
        okResponse({
          need_confirm: { id: 'tc1', name: '冻结天晟集团新增授信', arguments: { group: 'GRP-2026-900001' } },
          evidence: [],
        }),
    ]);
    renderChat();
    await screen.findByText('今天要看什么风险？');
    await sendAndSettle('冻结天晟集团新增授信');

    // 提议名与用户消息同文（用户点 chip 发起），至少两处 = 用户气泡 + confirm 卡
    expect(screen.getAllByText('冻结天晟集团新增授信').length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText(/group=GRP-2026-900001/)).toBeInTheDocument();

    const calls = fetchFn.mock.calls.length;
    fireEvent.click(screen.getByRole('button', { name: /批\s*准\s*执\s*行/ }));
    expect(antdMessage.info).toHaveBeenCalledWith('写回链路将在后续批次接入；当前 M5 演示走剧本流程');
    expect(fetchFn.mock.calls.length).toBe(calls); // 不发 /confirm
  }, 60000);
});