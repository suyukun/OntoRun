/// <reference types="vitest/globals" />
// a11y 复核（批 2）：/chat 三态（剧本流 / 空态 / 证据抽屉展开）以批 1 组件 + 假数据渲染后 axe-core 扫描。
// 门槛与先例 scan.test.tsx 一致：critical/serious 违规 = 0；moderate 及以下与 incomplete 以 console.log 留档。
// 说明：jsdom 无布局引擎，axe color-contrast 只能判 incomplete（同先例）；echarts canvas 在 jsdom 不可用，
// BlockChart mock 为静态占位（块容器/标题/图标钮仍参与扫描）。
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { act, render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import axe from 'axe-core';
import ChatRoutes from '../chat';

vi.mock('../chat/blocks/BlockChart', () => ({
  default: () => (
    <div>
      <div>各机构占比 vs 预警线</div>
      <div role="img" aria-label="各机构占比与预警线对比图（jsdom 占位）" />
    </div>
  ),
}));

type AxeResult = axe.AxeResults['violations'][number];

beforeEach(() => {
  localStorage.clear();
  // 演示目标视口 ≥1440（§2.7）：左栏展开态参与扫描
  Object.defineProperty(window, 'innerWidth', { configurable: true, value: 1440 });
  // jsdom 无 IntersectionObserver：仅本文件注入空实现，供 @ant-design/x Bubble.List autoScroll 挂载
  // （不动全局 setup：空 stub 会改变 motion 等库对 in-view 的判定，殃及其它套件）
  class IOStub {
    observe() {}
    unobserve() {}
    disconnect() {}
    takeRecords() {
      return [];
    }
  }
  (globalThis as typeof globalThis & { IntersectionObserver?: unknown }).IntersectionObserver ??= IOStub;
});

interface ScanOutcome {
  blockers: AxeResult[];
  others: AxeResult[];
  incomplete: AxeResult[];
  rulesPassed: number;
}

// 与先例相同的 act 包裹策略：axe.run 是异步长任务，扫描期间组件异步更新会落到 act 外
async function scanContainer(container: HTMLElement): Promise<ScanOutcome> {
  const actEnv = globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT?: boolean };
  const prev = actEnv.IS_REACT_ACT_ENVIRONMENT;
  actEnv.IS_REACT_ACT_ENVIRONMENT = true;
  let res: axe.AxeResults;
  try {
    res = await act(async (): Promise<axe.AxeResults> => axe.run(container, { resultTypes: ['violations', 'incomplete'] }));
  } finally {
    actEnv.IS_REACT_ACT_ENVIRONMENT = prev;
  }
  return {
    blockers: res.violations.filter((v) => v.impact === 'critical' || v.impact === 'serious'),
    others: res.violations.filter((v) => v.impact !== 'critical' && v.impact !== 'serious'),
    incomplete: res.incomplete,
    rulesPassed: res.passes.length,
  };
}

function summarize(list: AxeResult[]): unknown[] {
  return list.map((r) => ({
    id: r.id,
    impact: r.impact,
    nodes: r.nodes.length,
    help: r.help,
    targets: r.nodes.slice(0, 3).map((n) => n.target.join(' ')),
  }));
}

function renderChat() {
  return render(
    <MemoryRouter initialEntries={['/chat']}>
      <ChatRoutes />
    </MemoryRouter>,
  );
}

describe('axe 可达性复核 · /chat 三态（critical/serious = 0）', () => {
  it('剧本流（s1 预置全六块会话）：0 critical/serious', async () => {
    const { container } = renderChat();
    await screen.findByText('查看证据链 · 审计 #A-1024');
    const out = await scanContainer(container);
    console.log('[a11y:chat-flow] rules passed:', out.rulesPassed);
    console.log('[a11y:chat-flow] moderate/minor:', JSON.stringify(summarize(out.others)));
    console.log('[a11y:chat-flow] incomplete:', JSON.stringify(summarize(out.incomplete)));
    expect(out.blockers).toEqual([]);
  }, 30000);

  it('空态（切到空会话）：0 critical/serious', async () => {
    const { container } = renderChat();
    await screen.findByText('查看证据链 · 审计 #A-1024');
    fireEvent.click(screen.getByText('瑞华能源黄档解除'));
    await screen.findByText('今天要看什么风险？');
    const out = await scanContainer(container);
    console.log('[a11y:chat-empty] rules passed:', out.rulesPassed);
    console.log('[a11y:chat-empty] moderate/minor:', JSON.stringify(summarize(out.others)));
    console.log('[a11y:chat-empty] incomplete:', JSON.stringify(summarize(out.incomplete)));
    expect(out.blockers).toEqual([]);
  }, 30000);

  it('证据抽屉展开：0 critical/serious', async () => {
    const { container } = renderChat();
    await screen.findByText('查看证据链 · 审计 #A-1024');
    fireEvent.click(screen.getByTitle('证据链'));
    await screen.findByText('数据来源（basis 表）');
    const out = await scanContainer(container);
    console.log('[a11y:chat-drawer] rules passed:', out.rulesPassed);
    console.log('[a11y:chat-drawer] moderate/minor:', JSON.stringify(summarize(out.others)));
    console.log('[a11y:chat-drawer] incomplete:', JSON.stringify(summarize(out.incomplete)));
    expect(out.blockers).toEqual([]);
  }, 30000);
});
