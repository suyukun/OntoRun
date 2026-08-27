/// <reference types="vitest/globals" />
// App 集成冒烟 —— 浅色风险壳在 / 渲染价值 Landing；旧 /risk/chat 兜底进数据工作台（双栏同屏）
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import App from './App';
import { miniSnapshot } from './risk/testFixtures';

const mockFetch = vi.fn();
(globalThis as typeof globalThis & { fetch: typeof mockFetch }).fetch = mockFetch;

beforeEach(() => {
  mockFetch.mockReset();
  // S1 /meta/schema（MetaProvider 挂载即拉取）+ 风险快照
  mockFetch.mockImplementation((url: string) => {
    if (url === '/api/meta/schema') {
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ outcome: 'ok', data: { objects: [], links: [], actions: [] } }) });
    }
    if (url === '/risk-demo/risk-snapshot.json') {
      return Promise.resolve({ ok: true, json: () => Promise.resolve(miniSnapshot) });
    }
    return Promise.reject(new Error('unhandled ' + url));
  });
  localStorage.clear();
});

describe('App 路由', () => {
  it('/ 渲染风险价值 Landing（浅色壳）', async () => {
    render(<App />);
    await waitFor(() => {
      expect(screen.getAllByText(/风险预警系统/).length).toBeGreaterThan(0);
    });
    expect(screen.getAllByText(/用自然语言问风险问题/).length).toBeGreaterThan(0);
  });

  it('旧链接 /risk/chat 兜底重定向到数据工作台：左侧数据浏览与右侧对话同屏', async () => {
    window.history.pushState({}, '', '/risk/chat');
    render(<App />);
    // 左栏（DataExplorer）：对象侧栏分组标题出现
    await waitFor(() => {
      expect(screen.getByText('业务对象')).toBeTruthy();
    });
    // 右栏（RiskChatPanel）：对话面板标题出现 —— 双栏同屏证据
    expect(screen.getByText(/风险对话 · 人机双签/)).toBeTruthy();
    expect(screen.getByPlaceholderText(/输入风险问题或指令/)).toBeTruthy();
    // 对话入口不再是独立菜单项（并入工作台后菜单无 /risk/chat）
    expect(screen.queryAllByText('风险对话窗口').length).toBe(0);
  });
});
