/// <reference types="vitest/globals" />
// RiskLandingPage 冒烟测试 —— 价值主张 + 三大入口 + 真实数据统计
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import RiskLandingPage from './RiskLandingPage';
import { miniSnapshot } from './testFixtures';

const mockFetch = vi.fn();
(globalThis as typeof globalThis & { fetch: typeof mockFetch }).fetch = mockFetch;

beforeEach(() => {
  mockFetch.mockReset();
  mockFetch.mockResolvedValue({
    ok: true,
    json: () => Promise.resolve(miniSnapshot),
  });
  localStorage.clear();
});

const renderPage = () =>
  render(
    <MemoryRouter>
      <RiskLandingPage />
    </MemoryRouter>,
  );

describe('RiskLandingPage', () => {
  it('渲染价值主张与品牌标识', () => {
    renderPage();
    expect(screen.getByText(/用自然语言问风险问题、执行真实处置，全程本体驱动、可审计/)).toBeTruthy();
    expect(screen.getAllByText(/风险预警系统/).length).toBeGreaterThan(0);
    expect(screen.getByText(/安平金控集团 · 风险管理部/)).toBeTruthy();
  });

  it('展示三大入口（看数据/问问题/执行操作）与演示 CTA', () => {
    renderPage();
    expect(screen.getByRole('button', { name: /问问题/ })).toBeTruthy();
    expect(screen.getByRole('button', { name: /看数据/ })).toBeTruthy();
    expect(screen.getByRole('button', { name: /执行操作/ })).toBeTruthy();
    expect(screen.getByRole('button', { name: /开始演示/ })).toBeTruthy();
    expect(screen.getByRole('button', { name: /浏览风险数据/ })).toBeTruthy();
  });

  it('渲染真实数据统计（来自快照 totals，不写假数字）', async () => {
    renderPage();
    await waitFor(() => expect(screen.getByText('8万')).toBeTruthy());
    expect(screen.getByText('8,000')).toBeTruthy();
    expect(screen.getAllByText('预警信号').length).toBeGreaterThan(0);
    expect(screen.getAllByText('集团客户').length).toBeGreaterThan(0);
  });

  it('展示语义接口价值锚定', () => {
    renderPage();
    expect(screen.getByText(/语义接口层：LLM 经业务本体理解与操作，不直接碰库/)).toBeTruthy();
    expect(screen.getByText(/一条可追溯的处置链路/)).toBeTruthy();
  });
});
