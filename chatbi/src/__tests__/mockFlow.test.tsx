import { beforeEach, describe, expect, it, vi } from 'vitest';
import { act, fireEvent, render, renderHook, screen, waitFor, within } from '@testing-library/react';
import App from '../App';
import { deriveFinal } from '../state/deriveStatus';
import { useChatStream } from '../hooks/useChatStream';
import type { FinalResult } from '../types';

beforeEach(() => {
  // /api/profile 拉取失败 → 验证 mock 降级路径
  vi.stubGlobal('fetch', vi.fn(() => Promise.reject(new Error('backend down'))));
});

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
  it('profile 失败降级 mock → L1 动态更新 → 回答流式 → 表格渲染 → L2/L3 可展开', async () => {
    render(<App />);
    expect(await screen.findByText('mock 数据')).toBeTruthy();

    fireEvent.change(screen.getByPlaceholderText('输入问题…'), { target: { value: '8月按渠道的注册用户数？' } });
    fireEvent.click(screen.getByRole('button', { name: '发送' }));

    // L1 生成期动态进度（final 前必须出现过）
    await waitFor(() => expect(screen.getByText(/校验中 · 第 \d+/)).toBeTruthy(), { timeout: 3000 });

    // final 后：路径徽章 + 回答 + 数据表格
    await waitFor(() => expect(screen.getByText('❄ 冷路径·明细下推')).toBeTruthy(), { timeout: 15000 });
    expect(screen.getByText(/共 2,893 人/)).toBeTruthy();
    const tbl = screen.getByRole('table');
    expect(within(tbl).getAllByRole('row').length).toBeGreaterThanOrEqual(5); // 表头 + 4 行渠道

    // L2：点击 L1 展开步骤列表
    fireEvent.click(screen.getByText('❄ 冷路径·明细下推'));
    expect(screen.getByText(/意图路由/)).toBeTruthy();

    // L3：详情抽屉 + Tab 切换（断言收敛在抽屉内，避免与 L2 步骤详情重复匹配）
    fireEvent.click(screen.getByRole('button', { name: '详情' }));
    const drawer = screen.getByRole('dialog');
    fireEvent.click(within(drawer).getByRole('button', { name: '结论依据' }));
    expect(within(drawer).getByText(/REG_BY_CHANNEL/)).toBeTruthy();
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
