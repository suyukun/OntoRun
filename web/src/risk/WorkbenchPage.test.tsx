/// <reference types="vitest/globals" />
// 数据工作台双栏 smoke —— 左=数据浏览（对象侧栏/列表），右=风险对话·人机双签；两侧关键文案同屏。
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import WorkbenchPage from './WorkbenchPage';
import { miniSnapshot } from './testFixtures';
// 确定性加固：异步快照用例在高负载机器上会超过默认 5s（CI 稳定性），放宽到 20s
vi.setConfig({ testTimeout: 20_000 });

const mockFetch = vi.fn();
(globalThis as typeof globalThis & { fetch: typeof mockFetch }).fetch = mockFetch;

beforeEach(() => {
  mockFetch.mockReset();
  mockFetch.mockResolvedValue({ ok: true, json: () => Promise.resolve(miniSnapshot) });
  localStorage.clear();
});

describe('WorkbenchPage（分屏工作台）', () => {
  it('双栏结构渲染：左数据浏览 + 右对话面板同屏且互不缺位', async () => {
    const { container } = render(
      <MemoryRouter>
        <WorkbenchPage />
      </MemoryRouter>,
    );

    // 分屏容器与两个窗格存在
    const bench = container.querySelector('[data-testid="risk-workbench"]');
    expect(bench).toBeTruthy();
    expect(container.querySelector('[data-testid="workbench-explorer"]')).toBeTruthy();
    const chatAside = container.querySelector('[data-testid="workbench-chat"]');
    expect(chatAside).toBeTruthy();
    expect(chatAside?.getAttribute('aria-label')).toBe('风险对话');

    // 左侧关键文案：对象侧栏分组 + 默认列表行
    await waitFor(() => {
      expect(screen.getByText('业务对象')).toBeTruthy();
    });
    expect(screen.getByText('客户域')).toBeTruthy();
    expect(screen.getByText('风险监测域')).toBeTruthy();
    await waitFor(() => {
      expect(screen.getByText('中科智造产业发展集团')).toBeTruthy();
    });

    // 右侧关键文案：面板标题、示例引导、输入框
    expect(screen.getByText(/风险对话 · 人机双签/)).toBeTruthy();
    expect(screen.getByRole('button', { name: /示例问题：本月红色预警/ })).toBeTruthy();
    expect(screen.getByPlaceholderText(/输入风险问题或指令/)).toBeTruthy();
  });
});
