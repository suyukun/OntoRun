/// <reference types="vitest/globals" />
// 批 2 smoke：多轮路由（chips × 剧本 × 追问链）+ 会话隔离 + 停止/错误重试有效性。
// 按项目「脚手架 smoke 级」约定只锁主路径，不逐字段断言。
// 流式引擎由真实 setTimeout 驱动：本文件关闭 act 环境标志避免流式更新刷 act 告警，断言统一走 waitFor 轮询。
import { describe, it, expect, beforeAll, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import ChatRoutes from './index';
import { SUGGESTION_CHIPS, matchScript, matchScriptInContext, SCRIPTS } from './scriptData';

// jsdom 无 canvas：mock BlockChart（默认会话 s1 预置剧本含 chart 块；本批 smoke 用例不覆盖 chart 渲染）
vi.mock('./blocks/BlockChart', () => ({
  default: () => <div>各机构占比 vs 预警线（jsdom 占位）</div>,
}));

beforeAll(() => {
  (globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = false;
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

function renderChat() {
  return render(
    <MemoryRouter initialEntries={['/chat']}>
      <ChatRoutes />
    </MemoryRouter>,
  );
}

describe('chips × 剧本路由（问数优先，§12.1 裁决）', () => {
  it('空态 6 个 chips 各命中真实剧本（overview/reveal/formula/chart/report/reached）', () => {
    const expected = ['overview', 'reveal', 'formula', 'chart', 'report', 'reached'];
    SUGGESTION_CHIPS.forEach((c, i) => expect(matchScript(c.text).id).toBe(expected[i]));
  });

  it('追问链①：上一轮 reached → 本轮问分母 → formulaCtx 且复用前轮机构与数字', () => {
    const s = matchScriptInContext('分母是什么？怎么算的？', 'reached');
    expect(s.id).toBe('formulaCtx');
    expect(SCRIPTS.formulaCtx).toBeDefined();
    const text = s.blocks.find((b): b is Extract<typeof b, { type: 'text' }> => b.type === 'text');
    expect(text?.md).toContain('证券 **5.5%**');
    expect(text?.md).toContain('资管 **8.2%**');
    expect(text?.md).toContain('86.4 亿');
    expect(text?.md).toContain('800 亿');
  });

  it('无 reached 上下文时退回基础 formula 路由', () => {
    expect(matchScriptInContext('分母是什么？', 'overview').id).toBe('formula');
    expect(matchScriptInContext('分母是什么？').id).toBe('formula');
  });
});

describe('多轮与会话隔离 smoke（组件级，真实计时）', () => {
  it('追问链两轮同屏；切走切回历史保持', async () => {
    renderChat();
    // 默认 s1 预置剧本流；切到空会话 s2
    await screen.findByText('查看证据链 · 审计 #A-1024');
    fireEvent.click(screen.getByText('瑞华能源黄档解除'));
    await screen.findByText('今天要看什么风险？');

    // chip 点击 = 直接发送（§3.3）：第一轮触达问题
    fireEvent.click(screen.getByText('天晟集团哪些机构触达参考线？'));
    await waitFor(
      () => expect(screen.getAllByText(/证券 5\.5%/).length).toBeGreaterThan(0),
      { timeout: 20000 },
    );
    // 等第一轮完成（操作条常显）再追问，规避生成中 Enter 不发送（§7.2）
    await screen.findByText('查看证据链 · 审计 #A-1024', undefined, { timeout: 20000 });

    const ta = screen.getByRole('textbox');
    fireEvent.change(ta, { target: { value: '分母是什么？怎么算的？' } });
    fireEvent.keyDown(ta, { key: 'Enter' });

    // 第二轮上下文化应答（复用前轮机构/数字）
    await waitFor(
      () => expect(screen.getAllByText(/接着刚才的触达情况/).length).toBeGreaterThan(0),
      { timeout: 20000 },
    );
    await waitFor(() => expect(screen.getAllByText('查看证据链 · 审计 #A-1024')).toHaveLength(2), {
      timeout: 20000,
    });
    // 两轮用户消息与两条回答同屏
    expect(screen.getAllByText('天晟集团哪些机构触达参考线？').length).toBeGreaterThan(0);
    expect(screen.getAllByText('分母是什么？怎么算的？').length).toBeGreaterThan(0);

    // 切走 → 空态；切回 → 历史保持（§8.4）
    fireEvent.click(screen.getByText('000098 勾稽质询'));
    await screen.findByText('今天要看什么风险？');
    fireEvent.click(screen.getByText('瑞华能源黄档解除'));
    await waitFor(
      () => expect(screen.getAllByText(/接着刚才的触达情况/).length).toBeGreaterThan(0),
      { timeout: 10000 },
    );
    expect(screen.getAllByText('查看证据链 · 审计 #A-1024')).toHaveLength(2);
  }, 90000);

  it('生成中停止后引擎可继续；fallback 首答错误态可重试成功', async () => {
    renderChat();
    fireEvent.click(screen.getByText('瑞华能源黄档解除'));
    await screen.findByText('今天要看什么风险？');

    // 生成中出现停止钮，点击打断（§7.2）
    fireEvent.click(screen.getByText('天晟集团有限公司现在有什么风险预警？'));
    fireEvent.click(await screen.findByTitle('停止生成'));
    await waitFor(() => expect(screen.queryByTitle('停止生成')).toBeNull());

    // 停止后继续问：未命中 → fallback 首答错误态（§8.3）
    const ta = screen.getByRole('textbox');
    fireEvent.change(ta, { target: { value: 'xyzabc 未命中剧本' } });
    fireEvent.keyDown(ta, { key: 'Enter' });
    await screen.findByText('本次回答生成失败', undefined, { timeout: 20000 });

    // 重试：移除错误卡并成功出答（antd 对两字中文按钮自动插空格「重 试」，名字用正则匹配）
    fireEvent.click(screen.getByRole('button', { name: /重\s*试/ }));
    await waitFor(
      () => expect(screen.getAllByText(/本轮演示剧本覆盖/).length).toBeGreaterThan(0),
      { timeout: 20000 },
    );
    await waitFor(() => expect(screen.queryByText('本次回答生成失败')).toBeNull());
  }, 90000);
});