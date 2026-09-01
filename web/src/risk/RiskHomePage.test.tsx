/// <reference types="vitest/globals" />
// RiskHomePage 测试 —— 唯一一级入口：Agent 对话 + 七幕剧本 stepper（默认第 0 幕，逐幕可切换）。
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import RiskHomePage from './RiskHomePage';
import { miniSnapshot } from './testFixtures';
import { dashboardFixture, reportingDraftFixture, okJson } from './apiFixtures';
// 异步快照/看板用例放宽到 20s（既有范式）
vi.setConfig({ testTimeout: 20_000 });

const mockFetch = vi.fn();
(globalThis as typeof globalThis & { fetch: typeof mockFetch }).fetch = mockFetch;

beforeEach(() => {
  mockFetch.mockReset();
  mockFetch.mockImplementation((url: string) => {
    if (url === '/risk-demo/risk-snapshot.json') return okJson(miniSnapshot);
    if (url.startsWith('/api/risk/dashboard')) return okJson({ outcome: 'ok', data: dashboardFixture, error: null });
    if (url.startsWith('/api/risk/reporting/draft')) return okJson({ outcome: 'ok', data: reportingDraftFixture, error: null });
    return Promise.reject(new Error('unhandled ' + url));
  });
  localStorage.clear();
});

const renderHome = () =>
  render(
    <MemoryRouter>
      <RiskHomePage />
    </MemoryRouter>,
  );

describe('RiskHomePage（唯一一级入口）', () => {
  it('hero + Agent 对话面板 + 七幕 stepper 同屏，默认第 0 幕', async () => {
    renderHome();
    expect(screen.getByText(/用一句话，做一周的归集/)).toBeTruthy();
    await waitFor(() => expect(screen.getAllByText(/风险对话 · 人机双签/).length).toBeGreaterThan(0));
    expect(screen.getByPlaceholderText(/输入风险问题或指令/)).toBeTruthy();
    // 七幕 stepper
    for (const no of ['0', '1', '2', '3', '4', '5', '6']) {
      expect(screen.getByTestId('act-tab-' + no)).toBeTruthy();
    }
    expect(screen.getByTestId('act-frame-第 0 幕')).toBeTruthy();
  });

  it('切到第 1 幕 → 揭示帧', async () => {
    const user = userEvent.setup();
    renderHome();
    await user.click(screen.getByTestId('act-tab-1'));
    expect(screen.getByTestId('act-frame-第 1 幕')).toBeTruthy();
    expect(screen.getByText(/天晟集团有限公司/)).toBeTruthy();
  });

  it('切到第 2 幕 → 三线索证据卡（不发起网络请求也能渲染静态部分）', async () => {
    const user = userEvent.setup();
    renderHome();
    await user.click(screen.getByTestId('act-tab-2'));
    expect(screen.getByTestId('act-frame-第 2 幕')).toBeTruthy();
    expect(screen.getByTestId('clue-card-equity')).toBeTruthy();
    expect(screen.getByText('12.8%')).toBeTruthy();
  });

  it('切到第 6 幕 → 督办看板真数据渲染', async () => {
    const user = userEvent.setup();
    renderHome();
    await user.click(screen.getByTestId('act-tab-6'));
    await waitFor(() => expect(screen.getByTestId('act6-board')).toBeTruthy());
    expect(screen.getByText('10.8%')).toBeTruthy();
  });
});
