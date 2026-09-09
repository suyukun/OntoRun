import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act, cleanup, fireEvent, render, renderHook, screen, waitFor, within } from '@testing-library/react';
import App from '../App';
import { deriveFinal } from '../state/deriveStatus';
import { useChatStream } from '../hooks/useChatStream';
import type { FinalResult } from '../types';

beforeEach(() => {
  // /api/profile 拉取失败 → 验证 mock 降级路径
  vi.stubGlobal('fetch', vi.fn(() => Promise.reject(new Error('backend down'))));
});

// vitest globals 关闭时 testing-library 不自动 cleanup，DOM 会跨用例堆叠（与 messageCard.test 一致）
afterEach(() => cleanup());

const baseResult: FinalResult = {
  request_id: 'R',
  started_at: '',
  question: 'q',
  rule: 'X',
  path: 'hot',
  answer: 'a',
  sql: null,
  rows: [{ a: 1 }],
  tables: [],
  steps: [],
};

describe('deriveFinal 八状态映射（v0.2 §4.2 path→状态一对一）', () => {
  it('覆盖全部 path 与 block_reason 分支', () => {
    expect(deriveFinal({ ...baseResult })).toBe('success');
    expect(deriveFinal({ ...baseResult, path: 'cold_adhoc' })).toBe('success');
    expect(deriveFinal({ ...baseResult, rows: [] })).toBe('success_empty');
    expect(deriveFinal({ ...baseResult, degraded: true })).toBe('success_degraded');
    expect(deriveFinal({ ...baseResult, path: 'blocked_param', block_reason: 'missing_param' })).toBe('ask_param');
    expect(deriveFinal({ ...baseResult, path: 'blocked_param', block_reason: 'out_of_range' })).toBe('out_of_range');
    expect(deriveFinal({ ...baseResult, path: 'rejected' })).toBe('rejected');
    expect(deriveFinal({ ...baseResult, path: 'unregistered' })).toBe('unregistered');
    expect(deriveFinal({ ...baseResult, path: 'validation_failed' })).toBe('validation_failed');
    expect(deriveFinal({ ...baseResult, path: 'mystery' })).toBe('error');
  });
});

describe('mock 模式核心流程（验收主链路）', () => {
  it('profile 失败降级 mock → L1 动态更新 → 回答流式 → viz=bar 柱状图渲染 → L2/L3 可展开', async () => {
    const { container } = render(<App />);
    expect(await screen.findByText('mock 数据')).toBeTruthy();

    fireEvent.change(screen.getByPlaceholderText('输入问题…'), { target: { value: '8月按渠道的注册用户数？' } });
    fireEvent.click(screen.getByRole('button', { name: '发送' }));

    // L1 生成期动态进度（final 前必须出现过；步数动态，只报当前步 n）
    await waitFor(() => expect(screen.getByText(/第 \d+ 步 · /)).toBeTruthy(), { timeout: 3000 });

    // final 后：路径徽章（业务化文案，附录 G） + 回答 + viz=bar → SVG 柱状图（D7：与表格同源同一 rows）
    await waitFor(() => expect(screen.getByText('明细即席计算')).toBeTruthy(), { timeout: 15000 });
    expect(screen.getByText(/共 2,893 人/)).toBeTruthy();
    expect(container.querySelectorAll('.bub svg rect').length).toBeGreaterThanOrEqual(4); // 4 渠道各一柱，来自同一 rows
    expect(screen.getByText('1,240')).toBeTruthy(); // TOP1 APP 数值常显
    expect(screen.queryByRole('table')).toBeNull(); // viz=bar 走图表渲染器，非表格

    // 思考区：点击「已思考」展开步骤列表
    fireEvent.click(screen.getByText(/已思考 \d+ 步/));
    expect(screen.getByText(/意图路由/)).toBeTruthy();

    // 详情抽屉（审计视图，无 tab）：命中规则等一次性可查
    fireEvent.click(screen.getByRole('button', { name: '详情' }));
    const drawer = screen.getByRole('dialog');
    expect(within(drawer).getByText(/REG_BY_CHANNEL/)).toBeTruthy();
  });

  it('viz=kpi：热路径总数（REG_TOTAL=kpi）渲染为大数字指标卡，不出现表格/SVG', async () => {
    const { container } = render(<App />);
    fireEvent.change(await screen.findByPlaceholderText('输入问题…'), { target: { value: '8月注册用户数是多少？' } });
    fireEvent.click(screen.getByRole('button', { name: '发送' }));
    await waitFor(() => expect(screen.getByText('月报口径（预聚合）')).toBeTruthy(), { timeout: 15000 });
    expect(screen.getByText('2,893')).toBeTruthy(); // 大数字 = rows[0].total，同源不另算
    expect(container.querySelector('.bub svg[role="img"]')).toBeNull(); // 无图表 svg（UI 功能图标 aria-hidden 不计入）
    expect(screen.queryByRole('table')).toBeNull();
  });
});

describe('useChatStream 真实 SSE 路径（fetch reader 解析）', () => {
  const okResponse = (payload: string) =>
    Promise.resolve(
      new Response(
        new ReadableStream({
          start(c) {
            c.enqueue(new TextEncoder().encode(payload));
            c.close();
          },
        }),
        { status: 200 },
      ),
    );

  it('demo 帧格式（data-only + kind 字段）按序分派 step/token/final 并收尾', async () => {
    const payload = [
      'data: {"kind":"step","step":{"n":1,"title":"意图路由","status":"ok","detail":"x"}}',
      '',
      'data: {"kind":"token","text":"你好"}',
      '',
      'data: {"kind":"final","result":{"request_id":"R1","started_at":"","question":"q","rule":"R","path":"hot","answer":"你好","sql":null,"rows":[{"a":1}],"tables":[],"steps":[]}}',
      '',
    ].join('\n') + '\n\n'; // SSE 规范：每帧以空行终止（demo server 亦如此）
    vi.stubGlobal('fetch', vi.fn(() => okResponse(payload)));
    const events: string[] = [];
    const { result } = renderHook(() =>
      useChatStream({
        endpoint: '/api/chat',
        mock: false,
        callbacks: {
          onStep: () => events.push('step'),
          onToken: () => events.push('token'),
          onFinal: () => events.push('final'),
          onEnded: (why) => events.push('ended:' + why),
        },
      }),
    );
    act(() => result.current.send('q'));
    await waitFor(() => expect(events.join(',')).toBe('step,token,final,ended:final'));
    expect(result.current.busy).toBe(false);
  });

  it('标准 SSE event-name 风格 error 帧 → error 收尾', async () => {
    const payload = 'event: error\ndata: {"code":"E_SQL","message":"查询执行出错"}\n\n';
    vi.stubGlobal('fetch', vi.fn(() => okResponse(payload)));
    const ended: string[] = [];
    const { result } = renderHook(() =>
      useChatStream({
        endpoint: '/api/chat',
        mock: false,
        callbacks: {
          onStep: () => undefined,
          onToken: () => undefined,
          onFinal: () => undefined,
          onEnded: (why, err) => ended.push(why + ':' + (err?.code ?? '')),
        },
      }),
    );
    act(() => result.current.send('q'));
    await waitFor(() => expect(ended).toEqual(['error:E_SQL']));
  });
});