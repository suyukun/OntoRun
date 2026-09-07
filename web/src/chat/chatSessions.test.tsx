/// <reference types="vitest/globals" />
// 批 4 会话管理 smoke：置顶排序 / 行内重命名 / Popconfirm 删除（含删除当前会话自动切换）。
// fake 模式跑（会话管理行为模式无关）；a11y 由 chatScan 既有三态覆盖。
import { describe, it, expect, beforeAll, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import ChatRoutes from './index';

vi.mock('./blocks/BlockChart', () => ({
  default: () => <div>各机构占比 vs 预警线（jsdom 占位）</div>,
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
  (globalThis as typeof globalThis & { IntersectionObserver?: unknown }).IntersectionObserver ??= IOStub;
});

function renderChat() {
  return render(
    <MemoryRouter initialEntries={['/chat']}>
      <ChatRoutes />
    </MemoryRouter>,
  );
}

function itemsInOrder(): string[] {
  return [...document.querySelectorAll<HTMLElement>('.chat-session-item')].map(
    (el) => el.querySelector('.chat-session-main')?.textContent ?? el.title,
  );
}

describe('会话管理（批 4）：置顶 / 重命名 / 删除', () => {
  it('置顶：pinned 会话排到列表首位并可取消', async () => {
    renderChat();
    await screen.findByText('查看证据链 · 审计 #A-1024');
    expect(itemsInOrder()[0]).toBe('天晟集团风险归集');

    fireEvent.click(screen.getByRole('button', { name: '置顶 000098 勾稽质询' }));
    await waitFor(() => expect(itemsInOrder()[0]).toBe('000098 勾稽质询'));
    expect(screen.getByRole('button', { name: '取消置顶 000098 勾稽质询' })).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: '取消置顶 000098 勾稽质询' }));
    await waitFor(() => expect(itemsInOrder()[0]).toBe('天晟集团风险归集'));
  }, 30000);

  it('重命名：行内编辑 Enter 提交，侧栏与顶栏同步', async () => {
    renderChat();
    await screen.findByText('查看证据链 · 审计 #A-1024');

    fireEvent.click(screen.getByRole('button', { name: '重命名 瑞华能源黄档解除' }));
    const input = await screen.findByLabelText('重命名会话');
    fireEvent.change(input, { target: { value: '瑞华黄档复盘' } });
    fireEvent.keyDown(input, { key: 'Enter' });

    await waitFor(() => expect(screen.getAllByTitle('瑞华黄档复盘').length).toBeGreaterThanOrEqual(1)); // 侧栏条目（折叠/展开态同 title）
    // Esc 取消路径：开编辑 → 改字 → Esc → 恢复原名
    fireEvent.click(screen.getByRole('button', { name: '重命名 瑞华黄档复盘' }));
    const input2 = await screen.findByLabelText('重命名会话');
    fireEvent.change(input2, { target: { value: '不该保存' } });
    fireEvent.keyDown(input2, { key: 'Escape' });
    await waitFor(() => expect(screen.queryByDisplayValue('不该保存')).toBeNull());
    expect(screen.getByText('瑞华黄档复盘')).toBeInTheDocument();
  }, 30000);

  it('删除：非当前会话移除；删除当前会话自动切相邻；删空自动补新对话', async () => {
    renderChat();
    await screen.findByText('查看证据链 · 审计 #A-1024');

    // 删非当前（000098）：Popconfirm 确认
    fireEvent.click(screen.getByRole('button', { name: '删除 000098 勾稽质询' }));
    fireEvent.click(await screen.findByRole('button', { name: /^删\s*除$/ }));
    await waitFor(() => expect(screen.queryByTitle('000098 勾稽质询')).toBeNull());

    // 删当前（瑞华）：自动切到相邻（天晟）
    fireEvent.click(screen.getByText('瑞华能源黄档解除'));
    fireEvent.click(screen.getByRole('button', { name: '删除 瑞华能源黄档解除' }));
    fireEvent.click(await screen.findByRole('button', { name: /^删\s*除$/ }));
    await waitFor(() => expect(screen.queryByTitle('瑞华能源黄档解除')).toBeNull());
    expect(screen.getAllByText('天晟集团风险归集').length).toBeGreaterThanOrEqual(2); // 当前切到天晟

    // 删空：自动补一个「新对话」
    fireEvent.click(screen.getByRole('button', { name: '删除 天晟集团风险归集' }));
    fireEvent.click(await screen.findByRole('button', { name: /^删\s*除$/ }));
    await waitFor(() => expect(screen.getAllByTitle('新对话').length).toBeGreaterThanOrEqual(1));
    expect(await screen.findByText('今天要看什么风险？')).toBeInTheDocument(); // 空态 chips
  }, 60000);
});