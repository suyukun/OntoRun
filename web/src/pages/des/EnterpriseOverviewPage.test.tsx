/// <reference types="vitest/globals" />
// EnterpriseOverviewPage 冒烟：mock /des/enterprises* 端点渲染，断言关键文案与对照列。
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import EnterpriseOverviewPage from './EnterpriseOverviewPage';
// 确定性加固：异步快照用例在高负载机器上会超过默认 5s（CI 稳定性），放宽到 20s
vi.setConfig({ testTimeout: 20_000 });

const overviewFixture = {
  enterprise: {
    directory: 'ap_demo',
    display_name: '安平演示金控',
    code_prefix: 'AP',
    seed: 20260827,
    data_version: 'M1b-2',
    config_sha256: 'abc123',
    manifest_total_rows: 100,
    generated_at: null,
  },
  databases: [
    {
      file: 'approval.db',
      live_total_rows: 31,
      tables: [
        { table: 'ap_approve_node', rows: 20, manifest_rows: 20 },
        { table: 'ap_approve_task', rows: 11, manifest_rows: 10 },
      ],
    },
    {
      file: 'customer.db',
      live_total_rows: 50,
      tables: [{ table: 'ap_customer', rows: 50, manifest_rows: 50 }],
    },
  ],
  totals: { databases: 2, tables: 3, live_rows: 81 },
  domains: null,
};

const mockFetch = vi.fn();
(globalThis as typeof globalThis & { fetch: typeof mockFetch }).fetch = mockFetch;

beforeEach(() => {
  mockFetch.mockReset();
  mockFetch.mockImplementation((input: RequestInfo | URL) => {
    const url = String(input);
    if (url.startsWith('/des/enterprises/')) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ request_id: '', outcome: 'ok', data: overviewFixture }) });
    }
    if (url === '/des/enterprises') {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ request_id: '', outcome: 'ok', data: { items: [{ name: 'ap_demo', display_name: '安平演示金控' }] } }),
      });
    }
    return Promise.reject(new Error('unexpected url: ' + url));
  });
});

function renderPage() {
  return render(
    <MemoryRouter initialEntries={['/des']}>
      <EnterpriseOverviewPage />
    </MemoryRouter>,
  );
}

describe('EnterpriseOverviewPage', () => {
  it('渲染入口说明、概览卡与表清单（实时 vs 清单对照）', async () => {
    renderPage();
    // 入口说明一行
    expect(screen.getByText(/确定性流水线生成/)).toBeTruthy();
    // 企业名来自端点 display_name
    expect(await screen.findByText('安平演示金控')).toBeTruthy();
    // 概览卡：seed 来自端点（formatter 原样整数）
    await waitFor(() => expect(screen.getByText('20260827')).toBeTruthy());
    // 表清单：已知表名 + 库名列
    await waitFor(() => expect(screen.getByText('ap_approve_task')).toBeTruthy());
    expect(screen.getAllByText('customer.db').length).toBeGreaterThan(0);
    // 实时行数漂移对照（11 行 vs 清单 10 -> 标注漂移量）
    expect(screen.getByText('清单差 +1')).toBeTruthy();
  });

  it('yaml 无 domains 时如实展示缺口文案（不编造业务域）', async () => {
    renderPage();
    expect(await screen.findByText('安平演示金控')).toBeTruthy();
    await waitFor(() => {
      const desc = document.querySelector('.ant-empty-description');
      expect(desc?.textContent).toContain('暂无结构化业务域数据');
    });
    const desc = document.querySelector('.ant-empty-description');
    expect(desc?.textContent).toContain('domains 定义');
  });
});
