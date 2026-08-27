/// <reference types="vitest/globals" />
// RiskBrowsePage 冒烟测试 —— 对象列表 → 详情 → 链接遍历（无孤岛）
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import RiskBrowsePage from './RiskBrowsePage';
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

describe('RiskBrowsePage', () => {
  it('渲染对象侧栏（业务域分组）与默认集团客户列表', async () => {
    render(<RiskBrowsePage />);
    await waitFor(() => {
      expect(screen.getAllByText('集团客户').length).toBeGreaterThan(0);
    });
    expect(screen.getByText('中科智造产业发展集团')).toBeTruthy();
    // 侧栏业务域
    expect(screen.getByText('客户域')).toBeTruthy();
    expect(screen.getByText('风险监测域')).toBeTruthy();
    // 真实总数
    expect(screen.getByText('8,000')).toBeTruthy();
  });

  it('搜索过滤列表', async () => {
    const user = userEvent.setup();
    render(<RiskBrowsePage />);
    await waitFor(() => expect(screen.getByText('中科智造产业发展集团')).toBeTruthy());
    await user.type(screen.getByPlaceholderText(/搜索/), '不存在的名称xyz');
    await waitFor(() => {
      expect(screen.queryByText('中科智造产业发展集团')).toBeNull();
    });
  });

  it('点击记录进入详情并沿链接遍历（客户→预警→处置 无孤岛）', async () => {
    const user = userEvent.setup();
    render(<RiskBrowsePage />);
    // 详情（集团）
    await waitFor(() => expect(screen.getByText('中科智造产业发展集团')).toBeTruthy());
    await user.click(screen.getByText('中科智造产业发展集团'));
    // 集团详情应显示入向链接：group_customer.warning_signals
    await waitFor(() => {
      expect(screen.getByText('group_customer.warning_signals')).toBeTruthy();
    });
    // 沿链接进入预警列表
    await user.click(screen.getByText('group_customer.warning_signals'));
    await waitFor(() => {
      expect(screen.getByText('信用风险-押品贬值预警信号')).toBeTruthy();
    });
    // 进入预警详情
    await user.click(screen.getByText('信用风险-押品贬值预警信号'));
    await waitFor(() => {
      expect(screen.getByText('warning_signal.disposals')).toBeTruthy();
    });
    // 进入处置
    await user.click(screen.getByText('warning_signal.disposals'));
    await waitFor(() => {
      expect(screen.getByText('WD-2026-00000095')).toBeTruthy();
    });
  });
});
