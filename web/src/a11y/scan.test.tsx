/// <reference types="vitest/globals" />
// a11y 复核：三个关键页面以 mock 数据渲染后执行 axe-core 扫描。
// 门槛：critical/serious 违规 = 0（发现问题修根源，不以禁用规则掩盖）。
// moderate 及以下与 incomplete（jsdom 无法判定的项）以 console.log 汇总留档。
// 说明：jsdom 无真实布局引擎，axe color-contrast 只能判 incomplete；真实对比度
// 由 riskTheme 人工核验（textFaint 已从 #98a2b3 加深至 #636d80，AA 4.5:1 达标）。
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { act, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import axe from 'axe-core';
import type { ReactElement } from 'react';
import RiskLandingPage from '../risk/RiskLandingPage';
import WorkbenchPage from '../risk/WorkbenchPage';
import EnterpriseOverviewPage from '../pages/des/EnterpriseOverviewPage';
import { miniSnapshot } from '../risk/testFixtures';

type AxeResult = axe.AxeResults['violations'][number];

const mockFetch = vi.fn();
(globalThis as typeof globalThis & { fetch: typeof mockFetch }).fetch = mockFetch;

const desOverview = {
  enterprise: {
    directory: 'ap_demo', display_name: '安平演示金控', code_prefix: 'AP', seed: 20260827,
    data_version: 'M1b-2', config_sha256: 'abc', manifest_total_rows: 100, generated_at: null,
  },
  databases: [
    { file: 'approval.db', live_total_rows: 31, tables: [
      { table: 'ap_approve_task', rows: 11, manifest_rows: 10 },
      { table: 'ap_approve_node', rows: 20, manifest_rows: 20 },
    ] },
  ],
  totals: { databases: 1, tables: 2, live_rows: 31 },
  domains: null,
};

beforeEach(() => {
  mockFetch.mockReset();
  mockFetch.mockImplementation((input: RequestInfo | URL) => {
    const url = String(input);
    if (url === '/risk-demo/risk-snapshot.json') {
      return Promise.resolve({ ok: true, json: () => Promise.resolve(miniSnapshot) });
    }
    if (url.startsWith('/des/enterprises/')) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ request_id: '', outcome: 'ok', data: desOverview }) });
    }
    if (url === '/des/enterprises') {
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ request_id: '', outcome: 'ok', data: { items: [{ name: 'ap_demo', display_name: '安平演示金控' }] } }) });
    }
    return Promise.reject(new Error('unhandled url: ' + url));
  });
  localStorage.clear();
});

interface ScanOutcome {
  blockers: AxeResult[];
  others: AxeResult[];
  incomplete: AxeResult[];
}

// 渲染 + 等数据落定（findBy 包 act，避免本文件也产生 act 告警）+ axe 扫描容器子树。
// axe.run 是异步长任务：期间 rc-table 的测量/分页等异步更新会落到 act 外，
// 因此把整个扫描包进 act(async) 捕获，保持本文件 stderr 无 act 告警。
// 顺带把 act 环境钉在 true（扫描结束还原）：防御 RTL waitFor 恢复该标志的竞态，
// 避免全量并发时偶发 "The current testing environment is not configured to support act(...)"。
async function renderAndScan(ui: ReactElement, settle: () => Promise<unknown>): Promise<ScanOutcome> {
  const { container } = render(<MemoryRouter initialEntries={['/des']}>{ui}</MemoryRouter>);
  await settle();
  const actEnv = globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT?: boolean };
  const prev = actEnv.IS_REACT_ACT_ENVIRONMENT;
  actEnv.IS_REACT_ACT_ENVIRONMENT = true;
  let res: axe.AxeResults;
  try {
    res = await act(async (): Promise<axe.AxeResults> => axe.run(container, { resultTypes: ['violations', 'incomplete'] }));
  } finally {
    actEnv.IS_REACT_ACT_ENVIRONMENT = prev;
  }
  return {
    blockers: res.violations.filter((v) => v.impact === 'critical' || v.impact === 'serious'),
    others: res.violations.filter((v) => v.impact !== 'critical' && v.impact !== 'serious'),
    incomplete: res.incomplete,
  };
}

function summarize(list: AxeResult[]): unknown[] {
  return list.map((r) => ({
    id: r.id,
    impact: r.impact,
    nodes: r.nodes.length,
    help: r.help,
    targets: r.nodes.slice(0, 3).map((n) => n.target.join(' ')),
  }));
}

describe('axe 可达性复核（critical/serious = 0）', () => {
  it('RiskLandingPage（价值页）：0 critical/serious', async () => {
    const out = await renderAndScan(<RiskLandingPage />, () => screen.findByText('8万'));
    console.log('[a11y:landing] moderate/minor:', JSON.stringify(summarize(out.others)));
    console.log('[a11y:landing] incomplete:', JSON.stringify(summarize(out.incomplete)));
    expect(out.blockers).toEqual([]);
  });

  it('WorkbenchPage（数据工作台双栏）：0 critical/serious', async () => {
    const out = await renderAndScan(<WorkbenchPage />, () => screen.findByText('中科智造产业发展集团'));
    console.log('[a11y:workbench] moderate/minor:', JSON.stringify(summarize(out.others)));
    console.log('[a11y:workbench] incomplete:', JSON.stringify(summarize(out.incomplete)));
    expect(out.blockers).toEqual([]);
  });

  it('EnterpriseOverviewPage（DES 总览）：0 critical/serious', async () => {
    const out = await renderAndScan(<EnterpriseOverviewPage />, () => screen.findByText('安平演示金控'));
    console.log('[a11y:overview] moderate/minor:', JSON.stringify(summarize(out.others)));
    console.log('[a11y:overview] incomplete:', JSON.stringify(summarize(out.incomplete)));
    expect(out.blockers).toEqual([]);
  });
});
