/// <reference types="vitest/globals" />
// App 集成冒烟 —— 风险演示壳在 / 渲染（深色 Landing），S1 路由仍可用
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import App from '../App';
import { miniSnapshot } from './testFixtures';

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
  it('/ 渲染风险价值 Landing（深色壳）', async () => {
    render(<App />);
    await waitFor(() => {
      expect(screen.getAllByText(/风险预警系统/).length).toBeGreaterThan(0);
    });
    expect(screen.getAllByText(/用自然语言问风险问题/).length).toBeGreaterThan(0);
  });
});
