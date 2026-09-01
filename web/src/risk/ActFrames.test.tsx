/// <reference types="vitest/globals" />
// 七幕剧本交互帧测试 —— 逐帧渲染 + 关键交互（揭示递进 / 证据链展开 / 双签驳回 / 报送初稿 / 督办看板）。
// 异步快照类用例（ActReporting/ActBoard 挂载即拉取）按既有范式放宽到 20s。
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ActComparison from './ActComparison';
import ActReveal from './ActReveal';
import ActEscalation from './ActEscalation';
import ActConsequence from './ActConsequence';
import ActRejection from './ActRejection';
import ActReporting from './ActReporting';
import ActBoard from './ActBoard';
import { dashboardFixture, reportingDraftFixture, okJson } from './apiFixtures';

vi.setConfig({ testTimeout: 20_000 });

const mockFetch = vi.fn();
(globalThis as typeof globalThis & { fetch: typeof mockFetch }).fetch = mockFetch;

function defaultFetch() {
  mockFetch.mockImplementation((url: string) => {
    if (url.startsWith('/api/risk/dashboard')) {
      return okJson({ outcome: 'ok', data: dashboardFixture, error: null });
    }
    if (url.startsWith('/api/risk/reporting/draft')) {
      return okJson({ outcome: 'ok', data: reportingDraftFixture, error: null });
    }
    return Promise.reject(new Error('unhandled ' + url));
  });
}

beforeEach(() => {
  mockFetch.mockReset();
  defaultFetch();
});

describe('第 0 幕 · 现状对照帧', () => {
  it('手工归集一周 vs 现在一句话（先痛后甜）', () => {
    render(<ActComparison />);
    expect(screen.getByTestId('act0-before')).toBeTruthy();
    expect(screen.getByTestId('act0-after')).toBeTruthy();
    expect(screen.getByText(/一轮下来，一周/)).toBeTruthy();
    // 「现在，一句话」在帧头副标题与 after 面板各出现一次，锁定 after 面板断言
    expect(screen.getAllByText(/现在，一句话/).length).toBeGreaterThan(0);
    expect(screen.getByText(/天晟集团风险有多大/)).toBeTruthy();
  });
});

describe('第 1 幕 · 揭示帧', () => {
  it('逐家亮出（银行/证券/资管）→ 汇总 86.4 亿 → 10.8% 橙色预警', async () => {
    const user = userEvent.setup();
    render(<ActReveal />);
    // 初始三家待揭示
    expect(screen.getAllByText(/待揭示/).length).toBe(3);
    await user.click(screen.getByRole('button', { name: /揭示下一家/ }));
    expect(screen.getByText('48 亿')).toBeTruthy();
    await user.click(screen.getByRole('button', { name: /揭示下一家/ }));
    expect(screen.getByText('22 亿')).toBeTruthy();
    await user.click(screen.getByRole('button', { name: /揭示下一家/ }));
    expect(screen.getByText('16.4 亿')).toBeTruthy();
    // 三家齐 → 合计 86.4 亿 ÷ 800 亿 = 10.8%
    expect(screen.getByText('86.4 亿')).toBeTruthy();
    expect(screen.getByText('10.8%')).toBeTruthy();
    // 汇总归集对限额 → 橙色徽标 + 自动生成文案
    await user.click(screen.getByRole('button', { name: /汇总归集/ }));
    expect(screen.getByTestId('level-badge-橙')).toBeTruthy();
    expect(screen.getByText(/橙色预警已自动生成/)).toBeTruthy();
    expect(screen.getByText(/预警线 10%/)).toBeTruthy();
  });

  it('重置可重新演示', async () => {
    const user = userEvent.setup();
    render(<ActReveal />);
    await user.click(screen.getByRole('button', { name: /揭示下一家/ }));
    await user.click(screen.getByRole('button', { name: /重置/ }));
    expect(screen.getAllByText(/待揭示/).length).toBe(3);
  });
});

describe('第 2 幕 · 升级识别帧', () => {
  it('三线索证据卡 + 纳入归集 12.8% 红 + AI 起草上调建议', () => {
    render(<ActEscalation />);
    expect(screen.getByTestId('clue-card-equity')).toBeTruthy();
    expect(screen.getByTestId('clue-card-guarantee')).toBeTruthy();
    expect(screen.getByTestId('clue-card-capital')).toBeTruthy();
    expect(screen.getByText('股权代持线索')).toBeTruthy();
    expect(screen.getByText('交叉担保链')).toBeTruthy();
    expect(screen.getByText('资金往来异动')).toBeTruthy();
    expect(screen.getByText('102.4 亿')).toBeTruthy();
    expect(screen.getByText('12.8%')).toBeTruthy();
    expect(screen.getByTestId('level-badge-红')).toBeTruthy();
    expect(screen.getByText(/AI 起草 · 上调红色建议/)).toBeTruthy();
  });

  it('点开证据链 → 真数据联动展示关系树线索与规则', async () => {
    const user = userEvent.setup();
    render(<ActEscalation />);
    await user.click(screen.getByTestId('open-evidence-chain'));
    await waitFor(() => expect(screen.getByTestId('evidence-chain')).toBeTruthy());
    expect(screen.getByText(/股权代持线索：恒昌贸易大股东张伟/)).toBeTruthy();
    expect(screen.getByText(/交叉担保链：恒昌贸易与天晟系企业互为担保人/)).toBeTruthy();
    // R1a/R2 在证据链规则区与升级汇总文案各出现一次，锁证据链面板断言
    expect(screen.getAllByText(/R1a/).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/R2/).length).toBeGreaterThan(0);
    // 「16 亿」在升级汇总（+16 亿（恒昌））与证据链归集余额各一次
    expect(screen.getAllByText(/16 亿/).length).toBeGreaterThan(0);
  });

  it('证据链后端不可用 → 明确错误态（不编数据）', async () => {
    const user = userEvent.setup();
    mockFetch.mockImplementation(() => Promise.reject(new Error('backend down')));
    render(<ActEscalation />);
    await user.click(screen.getByTestId('open-evidence-chain'));
    await waitFor(() => expect(screen.getByTestId('evidence-chain-error')).toBeTruthy());
  });
});

describe('第 3 幕 · 后果链帧', () => {
  it('处置 / 督办 / 立项三动作卡', () => {
    render(<ActConsequence />);
    expect(screen.getByTestId('consequence-submit_disposal')).toBeTruthy();
    expect(screen.getByTestId('consequence-warning_push')).toBeTruthy();
    expect(screen.getByTestId('consequence-risk_project')).toBeTruthy();
    expect(screen.getByText(/冻结未用额度/)).toBeTruthy();
    expect(screen.getAllByText(/向附属机构督办/).length).toBeGreaterThan(0);
  });
});

describe('第 4 幕 · 双签驳回帧', () => {
  it('AI 提议卡 → 审批人驳回 → 展示 2023 办法第二十三条', async () => {
    const user = userEvent.setup();
    render(<ActRejection />);
    expect(screen.getByTestId('ai-proposal')).toBeTruthy();
    expect(screen.getByText(/将天晟部分授信拆分至非关联第三方通道主体/)).toBeTruthy();
    expect(screen.queryByTestId('rejection-reason')).toBeNull();
    await user.click(screen.getByTestId('reject-button'));
    expect(screen.getByTestId('rejection-reason')).toBeTruthy();
    expect(screen.getByText(/2023 金融控股公司关联交易办法 第二十三条/)).toBeTruthy();
    expect(screen.getByText(/隐匿关联关系、拆分交易/)).toBeTruthy();
    expect(screen.getByTestId('rejected-tag')).toBeTruthy();
  });
});

describe('第 5 幕 · 监管动作帧', () => {
  it('报送初稿真数据：12.8% / 恒昌 / 银团压降 / 依据条款', async () => {
    render(<ActReporting />);
    await waitFor(() => expect(screen.getByTestId('act5-report')).toBeTruthy());
    expect(screen.getAllByText(/大额风险暴露口径监管报送初稿/).length).toBeGreaterThan(0);
    expect(screen.getByText('12.8%')).toBeTruthy();
    expect(screen.getByText(/隐性关联方（恒昌贸易）/)).toBeTruthy();
    expect(screen.getByText(/第三十七条/)).toBeTruthy();
    expect(screen.getByTestId('act5-actions')).toBeTruthy();
    expect(screen.getAllByText(/银团/).length).toBeGreaterThan(0);
    expect(screen.getByText(/现实压降周期通常数月/)).toBeTruthy();
  });

  it('报送初稿后端不可用 → 错误态 + 重试', async () => {
    mockFetch.mockImplementation((url: string) =>
      url.startsWith('/api/risk/reporting/draft')
        ? Promise.reject(new Error('backend down'))
        : Promise.reject(new Error('unhandled ' + url)),
    );
    render(<ActReporting />);
    await waitFor(() => expect(screen.getByTestId('act5-error')).toBeTruthy());
    expect(screen.getByRole('button', { name: /重试/ })).toBeTruthy();
  });
});

describe('第 6 幕 · 全局督办看板帧', () => {
  it('前十大排名（天晟 10.8% 橙 / 瑞华 9.4% 黄）+ 七态分布 + 超期数 + 结尾句', async () => {
    render(<ActBoard />);
    await waitFor(() => expect(screen.getByTestId('act6-board')).toBeTruthy());
    // 前十大排名：天晟 10.8% 橙
    expect(screen.getByTestId('rank-row-1')).toBeTruthy();
    expect(screen.getByText('10.8%')).toBeTruthy();
    expect(screen.getAllByTestId('level-badge-橙').length).toBeGreaterThan(0);
    expect(screen.getAllByText('瑞华能源集团有限公司').length).toBeGreaterThan(0);
    expect(screen.getByText('9.4%')).toBeTruthy();
    expect(screen.getAllByTestId('level-badge-黄').length).toBeGreaterThan(0);
    // 七态分布
    expect(screen.getByText('待确认')).toBeTruthy();
    expect(screen.getByText('5,934')).toBeTruthy();
    // 超期督办数
    expect(screen.getByText('128')).toBeTruthy();
    // 结尾「一键调档」
    expect(screen.getByTestId('act6-closing')).toBeTruthy();
    expect(screen.getByText(/一键调档/)).toBeTruthy();
  });

  it('看板后端不可用 → 错误态', async () => {
    mockFetch.mockImplementation(() => Promise.reject(new Error('backend down')));
    render(<ActBoard />);
    await waitFor(() => expect(screen.getByTestId('act6-error')).toBeTruthy());
  });
});
