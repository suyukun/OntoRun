/// <reference types="vitest/globals" />
// RiskLandingPage 冒烟测试 —— 价值主张 + 三张入口卡 + 单一 CTA + 真实数据统计（不写假数字）
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

// 异步快照加载的"安定点"：等待 useRiskSnapshot 的 fetch 完成后 setState 落在 act 内，
// 消除"not wrapped in act"告警（快照总计 8 万条预警信号，见 miniSnapshot.totals）。
const settle = () => screen.findByText('8万');

describe('RiskLandingPage', () => {
  it('渲染价值主张与品牌标识（hero 文案不动，单一 eyebrow 徽章）', async () => {
    const { container } = renderPage();
    await settle();
    expect(screen.getByText(/用自然语言问风险问题、执行真实处置，全程本体驱动、可审计/)).toBeTruthy();
    expect(screen.getAllByText(/风险预警系统/).length).toBeGreaterThan(0);
    expect(screen.getByText(/安平金控集团 · 风险管理部/)).toBeTruthy();
    // eyebrow 徽章 ≤1：仅 hero 一枚胶囊徽章
    expect(screen.getAllByText(/安平金控集团 · 风险管理部 · 风险预警系统/).length).toBe(1);
  });

  it('CTA 唯一意图：开始演示唯一且不再出现重复意图按钮；雷达 motif 已删除', async () => {
    const { container } = renderPage();
    await settle();
    expect(screen.getAllByRole('button', { name: /开始演示/ })).toHaveLength(1);
    // 四卡改三卡后的三张语义入口
    expect(screen.getByRole('button', { name: /数据工作台/ })).toBeTruthy();
    expect(screen.getByRole('button', { name: /价值统计锚点/ })).toBeTruthy();
    expect(screen.getByRole('button', { name: /企业模拟总览/ })).toBeTruthy();
    // 无重复意图 CTA（旧「浏览风险数据」二级 CTA 已删）
    expect(screen.queryByRole('button', { name: /浏览风险数据/ })).toBeNull();
    // 深色雷达扫描 motif 已移除
    expect(container.querySelector('.risk-radar')).toBeNull();
  });

  it('渲染真实数据统计带（大数字来自快照 totals，格子数=真实内容数）', async () => {
    renderPage();
    await waitFor(() => expect(screen.getByText('8万')).toBeTruthy());
    expect(screen.getByText('8,000')).toBeTruthy();
    expect(screen.getAllByText('预警信号').length).toBeGreaterThan(0);
    expect(screen.getAllByText('集团客户').length).toBeGreaterThan(0);
    // 统计带锚点存在（价值锚点卡回跳目标）
    expect(document.getElementById('risk-stats')).toBeTruthy();
  });

  it('展示语义接口价值锚定', async () => {
    renderPage();
    await settle();
    expect(screen.getByText(/语义接口层：LLM 经业务本体理解与操作，不直接碰库/)).toBeTruthy();
    expect(screen.getByText(/一条可追溯的处置链路/)).toBeTruthy();
  });
});
