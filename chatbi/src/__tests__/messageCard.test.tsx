import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import App from '../App';

/** T3 消息卡与三级披露：八状态 UI / L1-L3 / IME / 停止（mock 模式，关键字→场景见 mock/stream.ts）。 */

beforeEach(() => {
  // /api/profile 拉取失败 → mock 降级模式（与 mockFlow.test 一致）
  vi.stubGlobal('fetch', vi.fn(() => Promise.reject(new Error('backend down'))));
});

// vitest globals 关闭时 testing-library 不自动 cleanup，DOM 会跨用例堆叠
afterEach(() => cleanup());

/** mock 全流程 ≈1.2s+，统一放宽查询超时 */
const FLOW = { timeout: 8000 };

async function ask(q: string) {
  const input = await screen.findByPlaceholderText('输入问题…');
  fireEvent.change(input, { target: { value: q } });
  fireEvent.click(screen.getByRole('button', { name: '发送' }));
}

describe('思考区（§3.2 #1，Agent 惯例交互）', () => {
  it('完成后：已思考摘要（N 步 · 耗时）+ 业务化徽章 + 校验摘要；证据编号收进详情抽屉并可复制', async () => {
    Object.defineProperty(window.navigator, 'clipboard', {
      value: { writeText: vi.fn().mockResolvedValue(undefined) },
      configurable: true,
    });
    render(<App />);
    await ask('8月按渠道的注册用户数？');
    await screen.findByText('明细即席计算', {}, FLOW); // 热路径→月报口径（预聚合）、冷路径→明细即席计算
    expect(screen.getByText(/项校验全过/)).toBeTruthy();
    expect(screen.getByText(/已思考 \d+ 步 · 1\.3s/)).toBeTruthy(); // mock total_ms=1320
    expect(screen.queryByText(/REQ-2026-09-09-MOCK01/)).toBeNull(); // req id 不再常驻卡面
    fireEvent.click(screen.getByRole('button', { name: '详情' }));
    const drawer = screen.getByRole('dialog');
    expect(within(drawer).getByText(/REQ-2026-09-09-MOCK01/)).toBeTruthy();
    fireEvent.click(within(drawer).getByTitle(/复现过程/));
    await waitFor(() => expect(navigator.clipboard.writeText).toHaveBeenCalledWith('REQ-2026-09-09-MOCK01'));
    expect(await within(drawer).findByText(/已复制/)).toBeTruthy();
  });

  it('生成期：动态「第 n 步 · 当前步骤名」+ 等待期彩蛋行（星芒脉冲小字），不硬编码步数', async () => {
    const { container } = render(<App />);
    await ask('8月按渠道的注册用户数？');
    const live = await screen.findByText(/第 \d+ 步 · /, {}, { timeout: 3000 });
    expect(live.textContent).toMatch(/第 \d+ 步 · .+/);
    expect(live.querySelector('svg')).toBeTruthy(); // 进度图标为内联 SVG（去 emoji 本质防御）
    expect(live.textContent).not.toMatch(/\p{Extended_Pictographic}/u); // 不回潮 emoji
    expect(live.textContent).not.toMatch(/\/ \d+ 步/); // 分母在 final 前不可知，不得伪造
    const egg = container.querySelector('.eggrow'); // 彩蛋行（等待期渲染，回答开始即消失）
    expect(egg).toBeTruthy();
    expect(egg?.querySelector('.egg-spark')).toBeTruthy();
    expect(egg?.textContent?.length ?? 0).toBeGreaterThan(3);
    await screen.findByText('明细即席计算', {}, { timeout: 15000 });
    expect(container.querySelector('.eggrow')).toBeNull(); // 完成后不留痕
  });
});

describe('思考过程区（§3.2 #4，默认收起）', () => {
  it('回答输出后自动折叠；点击「已思考」展开，步骤按展示序连续编号（步数动态）', async () => {
    const { container } = render(<App />);
    await ask('8月按渠道的注册用户数？');
    await screen.findByText('明细即席计算', {}, { timeout: 15000 });
    expect(container.querySelector('.steps')).toBeNull(); // 首 token 即自动折叠
    fireEvent.click(screen.getByText(/已思考 \d+ 步/));
    const nos = Array.from(container.querySelectorAll('.stp-no')).map((el) => Number(el.textContent));
    expect(nos.length).toBeGreaterThanOrEqual(7); // 真实步数由事件流决定
    expect(nos).toEqual(Array.from({ length: nos.length }, (_, i) => i + 1)); // 1..N 无跳号
    expect(container.querySelector('pre.sql')).toBeNull(); // 用户可见层零 SQL（Jack 2026-09-11 裁决：SQL 仅留审计层）
  });
});

describe('详情抽屉（§3.2 #5，审计视图重定位）', () => {
  it('口径说明 + 命中规则 + 数据路径 + 校验记录（无重复 tab；用户可见层零 SQL，Jack 2026-09-11 裁决）', async () => {
    render(<App />);
    await ask('8月按渠道的注册用户数？');
    await screen.findByText('明细即席计算', {}, { timeout: 15000 });
    fireEvent.click(screen.getByRole('button', { name: '详情' }));
    const drawer = screen.getByRole('dialog');
    const text = drawer.textContent ?? '';
    expect(/口径说明/.test(text)).toBeTruthy();
    expect(/REG_BY_CHANNEL/.test(text)).toBeTruthy();
    expect(/DWD · dwd_tr_rgst_df/.test(text)).toBeTruthy();
    expect(/同源交叉/.test(text)).toBeTruthy();
    expect(/执行 SQL/.test(text)).toBeFalsy(); // 用户可见层零 SQL（Jack 2026-09-11 裁决：SQL 仅留审计层）
    expect(drawer.querySelectorAll('.tabs button').length).toBe(0); // 双 tab 已移除
  });
});

describe('八状态 UI（§4.2 逐状态）', () => {
  it('成功·空结果：空态文案 + 数据区空态（禁崩句）', async () => {
    render(<App />);
    await ask('8月凌晨的注册数据');
    // 先等 final 后的数据区空态（流式期间 token 分片可能恰好拼出「该范围无数据」，须以 final 为准）
    expect(await screen.findByText(/空结果集/, {}, FLOW)).toBeTruthy();
    expect(screen.getByText('该范围无数据')).toBeTruthy();
    expect(screen.getByText(/建议调整时间范围/)).toBeTruthy();
  });

  it('成功·含告警：黄标「本次由简化路由回答」', async () => {
    render(<App />);
    await ask('8月注册用户数（降级）');
    expect(await screen.findByText('本次由简化路由回答', {}, FLOW)).toBeTruthy();
    expect(screen.getByText('月报口径（预聚合）')).toBeTruthy();
  });

  // US3 节拍地板导致的双流程超时预算：本用例串跑两次 mock 流程（ask_param + chip 续查），
  // 演示补间将单流程展示拉至 2.5s、合计超 vitest 默认 5s 级 → 测试级放宽，断言语义不动
  it('参数追问：追问句 + chips 可点续查', { timeout: 15000 }, async () => {
    render(<App />);
    await ask('注册用户数是多少？');
    await screen.findByText(/已思考 \d+ 步/, {}, FLOW); // 思考完成折叠后再断言（追问路径无 token 流）
    expect(screen.getByText('请问您要查询哪个月份？')).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: '8月' }));
    await screen.findByText('月报口径（预聚合）', {}, { timeout: 15000 }); // 选中即续查 → hot_success
  });

  it('拒答·口径缺失：无对应口径 + 规则候选引导', async () => {
    render(<App />);
    await ask('客户满意度怎么样？');
    await screen.findByText(/已思考 \d+ 步/, {}, FLOW);
    expect(screen.getByText(/尚未注册口径/)).toBeTruthy();
    expect(screen.getByText(/纳入口径治理流程/)).toBeTruthy(); // 提示文案（回答含「派生规则候选」，避免多匹配）
  });

  it('拒答·范围超限：如实说明数据边界', async () => {
    render(<App />);
    await ask('9月注册用户数是多少？');
    await screen.findByText(/已思考 \d+ 步/, {}, FLOW);
    expect(screen.getByText(/2026-07-01 ~ 2026-08-31/)).toBeTruthy();
    expect(screen.getByText(/数据边界来自语义层元数据/)).toBeTruthy();
  });

  it('拒答·范围外：动态话术（命中词+可问清单）+ 可点示例引导', async () => {
    render(<App />);
    await ask('日活情况如何？');
    await screen.findByText(/已思考 \d+ 步/, {}, FLOW);
    expect(screen.getByText(/不猜数/)).toBeTruthy(); // 话术含命中词与可问清单
    expect(screen.getByRole('button', { name: '8月注册用户数是多少？' })).toBeTruthy(); // 换问 chips
  });

  it('校验失败：数值对照展示（宁可不答，不出假数）', async () => {
    render(<App />);
    await ask('8月注册数据校验');
    await screen.findByText(/已思考 \d+ 步/, {}, FLOW);
    expect(screen.getByText(/校验未通过，拒绝返回/)).toBeTruthy();
    expect(screen.getByText(/数值对照/)).toBeTruthy();
    expect(screen.getByText(/分渠道合计 3,000 ≠ 热路径总数 2,893/)).toBeTruthy();
  });

  it('服务异常：脱敏文案 + 重试按钮；L1 徽章「服务异常」', async () => {
    render(<App />);
    await ask('模拟服务异常');
    expect(await screen.findByText('查询失败：服务未响应', {}, FLOW)).toBeTruthy();
    expect(screen.getByText('服务异常')).toBeTruthy();
    expect(screen.getByRole('button', { name: '重试' })).toBeTruthy();
  });
});

describe('输入区（§3.6）', () => {
  it('IME 组合期间 Enter 不误发；组合结束后可发送', async () => {
    render(<App />);
    const input = await screen.findByPlaceholderText('输入问题…');
    fireEvent.compositionStart(input);
    fireEvent.change(input, { target: { value: '8月注册用户数' } });
    fireEvent.keyDown(input, { key: 'Enter' });
    expect(screen.queryByText('8月注册用户数')).toBeNull(); // 组合中不发送
    fireEvent.compositionEnd(input);
    fireEvent.keyDown(input, { key: 'Enter' });
    expect(screen.getByText('8月注册用户数', { selector: '.bub' })).toBeTruthy(); // 发出（限定气泡，避免命中会话标题）
    await screen.findByText('月报口径（预聚合）', {}, { timeout: 15000 }); // 流放完，避免悬挂更新
  });

  it('生成中点停止 → 消息标记「已取消」', async () => {
    render(<App />);
    await ask('8月按渠道的注册用户数？');
    fireEvent.click(await screen.findByRole('button', { name: /停止/ }));
    expect(await screen.findByText('已取消', {}, FLOW)).toBeTruthy();
    expect(screen.getByRole('button', { name: '重试' })).toBeTruthy();
  });

  it('断流（无 final 帧）→ 「已中断」+ 重试', async () => {
    render(<App />);
    await ask('模拟断流');
    expect(await screen.findByText('已中断', {}, FLOW)).toBeTruthy();
    expect(screen.getByRole('button', { name: '重试' })).toBeTruthy();
  });
});