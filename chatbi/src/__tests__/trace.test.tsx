import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen, within } from '@testing-library/react';
import App from '../App';

/**
 * T-U1 test_trace_penetration（UX v0.2 · US1 溯源穿透·汇总级）：
 * ① 点答案中任一数字 → 口径卡（这句数怎么算的人话＋规则状态）＋确认历史（谁何时确认）。
 * ② 用户可见层零 SQL 文本、零来源明细行（Jack 2026-09-11 裁决：SQL 仅留审计层内部）。
 * 断言口径：SQL 文本 = SQL 语句特征词（SELECT/FROM/GROUP BY/ORDER BY/WHERE）；
 * 口径人话中的表达式（如 SUM(去重 usr_id)）与步骤名「SQL 编译」不是 SQL 文本。
 */

beforeEach(() => {
  // /api/profile 拉取失败 → mock 降级模式（与其余 vitest 一致）
  vi.stubGlobal('fetch', vi.fn(() => Promise.reject(new Error('backend down'))));
});

afterEach(() => cleanup());

/** mock 全流程 ≈1.2s+，统一放宽查询超时 */
const FLOW = { timeout: 8000 };

async function ask(q: string) {
  const input = await screen.findByPlaceholderText('输入问题…');
  fireEvent.change(input, { target: { value: q } });
  fireEvent.click(screen.getByRole('button', { name: '发送' }));
}

const SQL_TEXT = /\bSELECT\b|\bFROM\b|\bGROUP\s+BY\b|\bORDER\s+BY\b|\bWHERE\b/i;

describe('test_trace_penetration（US1 溯源穿透·汇总级）', () => {
  it('①点击答案中任一数字 → 口径卡＋确认历史渲染（汇总级）', async () => {
    render(<App />);
    await ask('8月注册用户数是多少？');
    // 回答区数字可点击（2,893 = KPI 数；图表/表格中的同值数字不是按钮，选择器不歧义）
    fireEvent.click(await screen.findByRole('button', { name: '2,893' }, FLOW));
    const panel = screen.getByRole('dialog', { name: '口径溯源' });
    // 口径卡：这句数怎么算的人话（来自「口径声明」步骤的口径字段）
    expect(within(panel).getByText('口径说明：')).toBeTruthy();
    expect(within(panel).getByText(/去重 usr_id/)).toBeTruthy();
    expect(within(panel).getByText(/口径裁决号/)).toBeTruthy();
    // 规则状态：mock 服务返回未携带 → 显式空态（宁缺毋滥，不编造）
    expect(within(panel).getByText('暂无规则状态记录')).toBeTruthy();
    // 确认历史（谁何时确认）：现有服务返回无确认记录 → 显式空态
    expect(within(panel).getByText('确认历史')).toBeTruthy();
    expect(within(panel).getByText(/暂无确认记录/)).toBeTruthy();
    // 任一数字：换个数字同样可穿透（汇总级 = 同一口径卡，不按数字出明细行）
    fireEvent.click(within(panel).getByRole('button', { name: '关闭' }));
    fireEvent.click(screen.getByRole('button', { name: '08' }));
    expect(screen.getByRole('dialog', { name: '口径溯源' })).toBeTruthy();
  }, 15000);

  it('②用户可见层零 SQL 文本、零来源明细行（默认渲染 / 详情抽屉 / 口径面板三态）', async () => {
    const { container } = render(<App />);
    await ask('8月按渠道的注册用户数？'); // cold 路径：既有实现抽屉含「执行 SQL」，口径人话含 JOIN 字样
    await screen.findByText('明细即席计算', {}, FLOW);
    // 详情抽屉：既有「执行 SQL」一次性可查已按 Jack 2026-09-11 裁决移出用户可见层
    fireEvent.click(screen.getByRole('button', { name: '详情' }));
    const drawer = screen.getByRole('dialog');
    expect(within(drawer).queryByText(/执行 SQL/)).toBeNull();
    expect((drawer.textContent ?? '').match(SQL_TEXT)).toBeNull();
    expect(within(drawer).queryByText('暂无确认记录')).toBeNull(); // 确认历史在口径面板，不在审计抽屉
    fireEvent.click(within(drawer).getByRole('button', { name: '关闭' }));
    // 口径面板：汇总级穿透不带 SQL、不带来源明细行（无表格无行）
    fireEvent.click(screen.getByRole('button', { name: '2,893' }));
    const panel = screen.getByRole('dialog', { name: '口径溯源' });
    expect((panel.textContent ?? '').match(SQL_TEXT)).toBeNull();
    expect(panel.querySelectorAll('table, tbody tr').length).toBe(0);
    // 全渲染树兜底：SQL 语句零文本、SQL 代码块零节点
    expect((container.textContent ?? '').match(SQL_TEXT)).toBeNull();
    expect(container.querySelectorAll('pre.sql, .basis-sql').length).toBe(0);
  }, 15000);
});
