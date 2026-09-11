import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act, cleanup, fireEvent, render, renderHook, screen } from '@testing-library/react';
import App from '../App';
import { useChatStream, type StreamCallbacks } from '../hooks/useChatStream';
import { PHRASE_POOL, pickThinkingPhrase } from '../components/thinkingPhrases';
import { MIN_THINKING_MS } from '../config';
import { buildMockEvents } from '../mock/stream';
import type { ChatEvent, FinalResult, StepInfo } from '../types';

beforeEach(() => {
  vi.useFakeTimers();
});

afterEach(() => {
  cleanup();
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

const baseResult: FinalResult = {
  request_id: 'R1',
  started_at: '',
  question: 'q',
  rule: 'R',
  path: 'hot',
  answer: '2026-08 月注册 2,893 人。',
  sql: null,
  rows: [{ total: 2893 }],
  tables: [],
  steps: [],
};

/** 秒回 SSE：全部帧一次性到达（模拟后端全程 <2.5s 的快速响应） */
function instantSse(steps: StepInfo[]) {
  return vi.fn(() =>
    Promise.resolve(
      new Response(
        new ReadableStream({
          start(c) {
            const frames = [
              ...steps.map((s) => 'data: ' + JSON.stringify({ kind: 'step', step: s })),
              'data: ' + JSON.stringify({ kind: 'token', text: '答' }),
              'data: ' + JSON.stringify({ kind: 'final', result: baseResult }),
            ];
            c.enqueue(new TextEncoder().encode(frames.join('\n\n') + '\n\n'));
            c.close();
          },
        }),
        { status: 200 },
      ),
    ),
  );
}

function makeCollector() {
  const c = {
    steps: [] as StepInfo[],
    stepAt: [] as number[],
    finals: [] as FinalResult[],
    ended: [] as string[],
    sendAt: 0,
    finalAt: -1,
    callbacks: null as unknown as StreamCallbacks,
  };
  c.callbacks = {
    onStep: (s) => {
      c.steps.push(s);
      c.stepAt.push(Date.now());
    },
    onToken: () => undefined,
    onFinal: (r) => {
      c.finals.push(r);
      c.finalAt = Date.now();
    },
    onEnded: (why) => c.ended.push(why),
  };
  return c;
}

describe('US3 演示节奏（演示模式开，总时长兜底：步骤自然速度＋final 落点 ≥2.5s）', () => {
  const steps3: StepInfo[] = [
    { n: 1, title: '意图路由', status: 'ok', detail: 'd1' },
    { n: 2, title: '口径声明', status: 'ok', detail: 'd2' },
    { n: 3, title: '下推执行', status: 'ok', detail: 'd3' },
  ];

  it('SSE 秒回时：中间步骤不被拖慢（首步 <1000ms 量级自然出现），final 展示落点兜底 ≥2.5s', async () => {
    vi.stubGlobal('fetch', instantSse(steps3));
    const t = makeCollector();
    const { result } = renderHook(() =>
      useChatStream({ endpoint: '/api/chat', mock: false, pacing: true, callbacks: t.callbacks }),
    );
    act(() => {
      t.sendAt = Date.now();
      result.current.send('q');
    });
    // 排空微任务：fetch 响应 + 流读取（秒回，全部事件已入队）
    await act(async () => {
      await vi.advanceTimersByTimeAsync(0);
    });

    // ① 中间步骤不被拖慢：真实步骤在 1s 内全部出现（不再被节拍器均匀铺满压住）
    await act(async () => {
      await vi.advanceTimersByTimeAsync(1000);
    });
    expect(t.steps).toHaveLength(steps3.length);
    expect(t.stepAt[0] - t.sendAt).toBeLessThan(1000); // 首步 <1000ms 量级
    expect(t.finals).toHaveLength(0); // 步骤放完 ≠ 提前收尾

    // ② final 展示落点 ≥2.5s：2.4s 时不得提前收尾
    await act(async () => {
      await vi.advanceTimersByTimeAsync(MIN_THINKING_MS - 1000 - 400);
    });
    expect(t.finals).toHaveLength(0);
    expect(t.ended).toEqual([]);

    // 过点即收尾：全程 ≥2.5s
    await act(async () => {
      await vi.advanceTimersByTimeAsync(400);
    });
    expect(t.ended).toEqual(['final']);
    expect(t.finalAt - t.sendAt).toBeGreaterThanOrEqual(MIN_THINKING_MS);
  });

  it('演示节奏关（对照）：秒回 SSE 即时收尾，不额外拖长', async () => {
    vi.stubGlobal('fetch', instantSse(steps3));
    const t = makeCollector();
    const { result } = renderHook(() =>
      useChatStream({ endpoint: '/api/chat', mock: false, pacing: false, callbacks: t.callbacks }),
    );
    act(() => {
      t.sendAt = Date.now();
      result.current.send('q');
    });
    await act(async () => {
      await vi.advanceTimersByTimeAsync(0);
    });
    expect(t.ended).toEqual(['final']);
    expect(t.steps).toHaveLength(steps3.length);
    expect(t.finalAt - t.sendAt).toBeLessThan(MIN_THINKING_MS);
  });
});

describe('US3 假步骤零（展示步骤集合 ⊆ 真实 SSE 事件集合）', () => {
  it('hook 层：补间释放的步骤与真实 SSE 事件逐项深相等（无插入、无篡改、顺序一致）', async () => {
    const sseSteps: StepInfo[] = [
      { n: 1, title: '意图路由', status: 'ok', detail: 'd1' },
      { n: 2, title: '口径声明', status: 'ok', detail: 'd2' },
      { n: 3, title: '参数抽取+校验', status: 'ok', detail: 'd3' },
      { n: 4, title: 'SQL 编译', status: 'ok', detail: 'd4' },
      { n: 5, title: '结果校验', status: 'ok', detail: 'd5' },
    ];
    vi.stubGlobal('fetch', instantSse(sseSteps));
    const t = makeCollector();
    const { result } = renderHook(() =>
      useChatStream({ endpoint: '/api/chat', mock: false, pacing: true, callbacks: t.callbacks }),
    );
    act(() => result.current.send('q'));
    await act(async () => {
      await vi.advanceTimersByTimeAsync(MIN_THINKING_MS + 500);
    });
    expect(t.ended).toEqual(['final']);
    expect(t.steps).toEqual(sseSteps);
  });

  it('UI 层：App 渲染的思考步骤 ⊆ mock SSE 事件集合，真实步骤不丢不多', async () => {
    const question = '8月注册用户数是多少？';
    vi.stubGlobal('fetch', vi.fn(() => Promise.reject(new Error('backend down')))); // → mock 模式
    render(<App />);
    await act(async () => {
      await vi.advanceTimersByTimeAsync(0);
    });
    expect(screen.getByText('mock 数据')).toBeTruthy();
    fireEvent.change(screen.getByPlaceholderText('输入问题…'), { target: { value: question } });
    fireEvent.click(screen.getByRole('button', { name: '发送' }));
    await act(async () => {
      await vi.advanceTimersByTimeAsync(MIN_THINKING_MS + 500);
    });
    fireEvent.click(screen.getByText(/已思考 \d+ 步/));
    const rendered = Array.from(document.querySelectorAll('.steps .stp b')).map((el) => el.textContent ?? '');
    const sseTitles = buildMockEvents(question)
      .filter((e): e is Extract<ChatEvent, { kind: 'step' }> => e.kind === 'step')
      .map((e) => e.step.title);
    expect(rendered.length).toBeGreaterThan(0);
    for (const title of rendered) expect(sseTitles).toContain(title); // ⊆ 零假步骤
    expect(rendered.length).toBe(sseTitles.length); // 真实步骤不丢
  });
});

describe('US3 思考流话术模板池', () => {
  it('同一步骤类型多次取样不全同（随机取用，避免每次一字不差）', () => {
    const picks = new Set(Array.from({ length: 12 }, () => pickThinkingPhrase('意图路由')));
    expect(picks.size).toBeGreaterThanOrEqual(2);
  });

  it('每个已登记步骤类型至少 2 个模板；未登记类型回落通用池且非空', () => {
    for (const pool of Object.values(PHRASE_POOL)) expect(pool.length).toBeGreaterThanOrEqual(2);
    expect(pickThinkingPhrase('不存在的步骤类型')).not.toBe('');
  });

  it('模板内容克制：无数字、无夸张自夸（数字与事实永远来自结构化字段）', () => {
    const pools = [...Object.values(PHRASE_POOL), ['正在处理']];
    for (const pool of pools) {
      for (const p of pool) {
        expect(p).not.toMatch(/\d/);
        expect(p).not.toMatch(/最强|超强|厉害|完美|秒杀|逆天/);
      }
    }
  });
});
