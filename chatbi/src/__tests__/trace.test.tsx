import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen, within } from '@testing-library/react';
import App from '../App';

/**
 * T-U1 test_trace_penetration（UX v0.2 · US1 溯源穿透·汇总级）＋ T-N7 本体级溯源改版：
 * ① 点答案中任一数字 → 口径卡（这句数怎么算的人话＋规则状态）。
 * ② 用户可见层零 SQL 文本、零来源明细行（Jack 2026-09-11 裁决：SQL 仅留审计层内部）。
 * ③ Jack 2026-09-11 裁决：表名移出用户层＋确认历史设计砍除（规格变更非凑绿）——
 *    详情抽屉与口径面板渲染树零表名/零层名（dwd_tr_rgst_df 等字面量反例）、零「确认历史」区块。
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
/** 存储层表名字面量（mock result.tables 携带，用户层渲染必须零出现） */
const STORAGE_NAMES = /dwd_tr_rgst_df|dim_ch_chl_df|dws_reg_daily_df|dim_cu_usr_info_df/;
/** 存储层层名（独立词，含旧的「层 · 表名」展示形态） */
const LAYER_NAMES = /\b(DWD|DWS|DIM|ADS|CDM|ODS)\b/;

describe('test_trace_penetration（US1 溯源穿透·汇总级）', () => {
  it('①点击答案中任一数字 → 口径卡（口径说明＋规则状态），零确认历史区块', async () => {
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
    // 确认历史区块整个砍除（Jack 2026-09-11 裁决）：连空态在内不得出现
    expect(within(panel).queryByText('确认历史')).toBeNull();
    expect(within(panel).queryByText(/暂无确认记录/)).toBeNull();
    // 任一数字：换个数字同样可穿透（汇总级 = 同一口径卡，不按数字出明细行）
    fireEvent.click(within(panel).getByRole('button', { name: '关闭' }));
    fireEvent.click(screen.getByRole('button', { name: '08' }));
    expect(screen.getByRole('dialog', { name: '口径溯源' })).toBeTruthy();
  }, 15000);

  it('②用户可见层零 SQL、零来源明细行、零表名/层名（默认渲染 / 详情抽屉 / 口径面板三态）', async () => {
    const { container } = render(<App />);
    await ask('8月按渠道的注册用户数？'); // cold 路径：mock result.tables 携带 dwd_tr_rgst_df 等存储层名，渲染层必须零出现
    await screen.findByText('明细即席计算', {}, FLOW);
    // 详情抽屉：既有「执行 SQL」一次性可查已按 Jack 2026-09-11 裁决移出用户可见层
    fireEvent.click(screen.getByRole('button', { name: '详情' }));
    const drawer = screen.getByRole('dialog');
    expect(within(drawer).queryByText(/执行 SQL/)).toBeNull();
    expect((drawer.textContent ?? '').match(SQL_TEXT)).toBeNull();
    // 本体级溯源（Jack 2026-09-11 裁决：表名移出用户层）：零表名/零层名，规则信息仍可见
    expect((drawer.textContent ?? '').match(STORAGE_NAMES)).toBeNull();
    expect((drawer.textContent ?? '').match(LAYER_NAMES)).toBeNull();
    expect(within(drawer).getByText('命中规则：')).toBeTruthy();
    expect(/REG_BY_CHANNEL/.test(drawer.textContent ?? '')).toBe(true);
    // 确认历史设计整个砍除（Jack 2026-09-11 裁决）：审计抽屉同样不得出现
    expect(within(drawer).queryByText('确认历史')).toBeNull();
    expect(within(drawer).queryByText('暂无确认记录')).toBeNull();
    fireEvent.click(within(drawer).getByRole('button', { name: '关闭' }));
    // 口径面板：汇总级穿透不带 SQL、不带来源明细行（无表格无行）、零表名/层名、零确认历史
    fireEvent.click(screen.getByRole('button', { name: '2,893' }));
    const panel = screen.getByRole('dialog', { name: '口径溯源' });
    expect((panel.textContent ?? '').match(SQL_TEXT)).toBeNull();
    expect(panel.querySelectorAll('table, tbody tr').length).toBe(0);
    expect((panel.textContent ?? '').match(STORAGE_NAMES)).toBeNull();
    expect((panel.textContent ?? '').match(LAYER_NAMES)).toBeNull();
    expect(within(panel).queryByText('确认历史')).toBeNull();
    // 全渲染树兜底：SQL 语句零文本、SQL 代码块零节点
    expect((container.textContent ?? '').match(SQL_TEXT)).toBeNull();
    expect(container.querySelectorAll('pre.sql, .basis-sql').length).toBe(0);
  }, 15000);
});
