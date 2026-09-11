import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import App from '../App';

/** T-U2 主动洞察：命中 → 置顶洞察卡＋「看分解」；无命中 → 常用查询兜底（不出凑数卡）。 */

const HIT_INSIGHT = {
  type: 'channel_day_over_day',
  channel: '中信书院',
  metric: '注册用户数',
  current: 35,
  baseline: 3,
  delta_pct: 1066.7,
  drilldown: { measure: 'reg_user_cnt', dimensions: ['channel_l2'], time: { from: '2026-08-25', to: '2026-08-31' } },
};

function stubInsights(payload: unknown) {
  vi.stubGlobal('fetch', vi.fn((input: RequestInfo | URL) => {
    const url = String(input);
    if (url.includes('/api/insights')) {
      return Promise.resolve(new Response(JSON.stringify(payload), { status: 200 }));
    }
    return Promise.reject(new Error('backend down')); // /api/profile 失败 → mock 模式
  }));
}

beforeEach(() => {
  stubInsights({ insights: [HIT_INSIGHT] });
});

// vitest globals 关闭时 testing-library 不自动 cleanup，DOM 会跨用例堆叠
afterEach(() => cleanup());

describe('主动洞察卡（UX v0.2 US2）', () => {
  it('命中：置顶洞察卡＋事实句＋看分解走既有问答；无命中：不出卡、常用查询兜底', async () => {
    // —— 命中态：洞察卡渲染 ——
    render(<App />);
    expect(await screen.findByText(/中信书院/)).toBeTruthy(); // 事实句含渠道名
    expect(screen.getByText(/\+1066\.7%/)).toBeTruthy(); // 纯事实数字
    expect(screen.queryByText(/因为|由于|原因/)).toBeNull(); // 因果沉默：零归因文案
    const drill = screen.getByRole('button', { name: '看分解' });
    fireEvent.click(drill); // 走现有语义接口（不新增契约）
    expect(
      screen.getByText('8月分渠道按日注册用户数', { selector: '.bub' }),
    ).toBeTruthy(); // 问题由 drilldown 组装发出

    // —— 无命中态：兜底入口，不出凑数卡 ——
    cleanup();
    stubInsights({ insights: [], fallback: 'common_queries' });
    render(<App />);
    await screen.findByText(/试试示例问题，或直接输入/); // 空态就绪（insights 已返回）
    expect(screen.queryByText(/中信书院/)).toBeNull(); // 无命中不出卡
    expect(
      screen.getByRole('button', { name: '8月按渠道的注册用户数？' }),
    ).toBeTruthy(); // 常用查询兜底入口
  });
});
