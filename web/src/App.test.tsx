/// <reference types="vitest/globals" />
// App 集成冒烟 —— 信息架构收敛（口径包§六/§七）：
// - / 直达 Agent 对话（唯一一级入口）+ 七幕剧本演示；
// - 门面菜单收敛为唯一入口「风险对话」，数据浏览/企业模拟/零售撤出门面（仅次级按钮保留）；
// - 旧 /risk/chat 兜底重定向到 /（对话主页）。
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import App from './App';
import { miniSnapshot } from './risk/testFixtures';
// 异步快照用例放宽到 20s（既有范式）
vi.setConfig({ testTimeout: 20_000 });

const mockFetch = vi.fn();
(globalThis as typeof globalThis & { fetch: typeof mockFetch }).fetch = mockFetch;

beforeEach(() => {
  mockFetch.mockReset();
  // S1 /meta/schema（MetaProvider 挂载即拉取）+ 风险快照（对话面板）
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

describe('App 路由 · 信息架构收敛', () => {
  it('/ 直达 Agent 对话（唯一一级入口）+ 七幕剧本演示（默认第 0 幕）', async () => {
    render(<App />);
    await waitFor(() => {
      expect(screen.getAllByText(/用一句话，做一周的归集/).length).toBeGreaterThan(0);
    });
    await waitFor(() => {
      expect(screen.getAllByText(/风险对话 · 人机双签/).length).toBeGreaterThan(0);
    });
    expect(screen.getByTestId('act-frame-第 0 幕')).toBeTruthy();
  });

  it('菜单收敛：门面菜单仅剩唯一入口「风险对话」，数据工作台/企业模拟/零售撤出菜单', async () => {
    render(<App />);
    await waitFor(() => {
      expect(screen.getAllByText(/用一句话，做一周的归集/).length).toBeGreaterThan(0);
    });
    // AntD 门面菜单只渲染 1 个 menuitem = 风险对话（唯一一级入口）
    const menuItems = screen.getAllByRole('menuitem');
    expect(menuItems).toHaveLength(1);
    expect(menuItems[0]).toHaveTextContent('风险对话');
    // 数据工作台 / 企业模拟 / 零售不再是菜单项（撤出门面）
    expect(screen.queryByRole('menuitem', { name: /数据工作台/ })).toBeNull();
    expect(screen.queryByRole('menuitem', { name: /企业模拟/ })).toBeNull();
    expect(screen.queryByRole('menuitem', { name: /零售供应链演示/ })).toBeNull();
    // 次级入口按钮仍保留（路由可达）
    expect(screen.getAllByRole('button', { name: /数据工作台/ }).length).toBeGreaterThan(0);
    expect(screen.getAllByRole('button', { name: /企业模拟/ }).length).toBeGreaterThan(0);
  });

  it('旧链接 /risk/chat 兜底重定向到对话主页（/）', async () => {
    window.history.pushState({}, '', '/risk/chat');
    render(<App />);
    await waitFor(() => {
      expect(screen.getAllByText(/用一句话，做一周的归集/).length).toBeGreaterThan(0);
    });
    expect(screen.getAllByText(/风险对话 · 人机双签/).length).toBeGreaterThan(0);
  });

  it('/risk/browse 数据工作台仍可达（撤出门面但保留路由）', async () => {
    window.history.pushState({}, '', '/risk/browse');
    render(<App />);
    // 左栏（DataExplorer）：对象侧栏分组标题出现
    await waitFor(() => {
      expect(screen.getByText('业务对象')).toBeTruthy();
    });
    // 右栏（RiskChatPanel）：对话面板标题出现 —— 双栏同屏
    expect(screen.getByText(/风险对话 · 人机双签/)).toBeTruthy();
    expect(screen.getByPlaceholderText(/输入风险问题或指令/)).toBeTruthy();
  });
});
