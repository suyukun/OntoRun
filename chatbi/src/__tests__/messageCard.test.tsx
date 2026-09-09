import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import App from '../App';
import { REQ_ID_HINT } from '../components/labels';

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

describe('L1 摘要条（§3.2 #1）', () => {
  it('完成后：业务化徽章 + 校验摘要 + 证据编号 hover 提示与点击复制', async () => {
    Object.defineProperty(window.navigator, 'clipboard', {
      value: { writeText: vi.fn().mockResolvedValue(undefined) },
      configurable: true,
    });
    render(<App />);
    await ask('8月按渠道的注册用户数？');
    await screen.findByText('明细即席计算', {}, FLOW); // 热路径→月报口径（预聚合）、冷路径→明细即席计算
    expect(screen.getByText(/项校验全过/)).toBeTruthy();
    const req = screen.getByText(/REQ-2026-09-09-MOCK01/);
    expect(req.getAttribute('title')).toBe(REQ_ID_HINT);
    fireEvent.click(req);
    await waitFor(() => expect(navigator.clipboard.writeText).toHaveBeenCalledWith('REQ-2026-09-09-MOCK01'));
    expect(await screen.findByText(/已复制/, {}, FLOW)).toBeTruthy();
  });

  it('生成期：动态「第 n 步 · 当前步骤名」，不硬编码步数（D6 动态追加校验步，总数未知）', async () => {
    render(<App />);
    await ask('8月按渠道的注册用户数？');
    const live = await screen.findByText(/第 \d+ 步 · /, {}, { timeout: 3000 });
    expect(live.textContent).toMatch(/⏳ 第 \d+ 步 · .+/);
    expect(live.textContent).not.toMatch(/\/ \d+ 步/); // 分母在 final 前不可知，不得伪造
    await screen.findByText('明细即席计算', {}, { timeout: 15000 });
  });
});

describe('L2 决策过程区（§3.2 #4，默认收起）', () => {
  it('默认收起；点击 L1 展开后步骤按展示序连续编号（步数动态）', async () => {
    const { container } = render(<App />);
    await ask('8月按渠道的注册用户数？');
    await screen.findByText('明细即席计算', {}, { timeout: 15000 });
    expect(container.querySelector('.steps')).toBeNull(); // 默认收起
    fireEvent.click(screen.getByText('明细即席计算'));
    const nos = Array.from(container.querySelectorAll('.stp-no')).map((el) => Number(el.textContent));
    expect(nos.length).toBeGreaterThanOrEqual(7); // 真实步数由事件流决定
    expect(nos).toEqual(Array.from({ length: nos.length }, (_, i) => i + 1)); // 1..N 无跳号
    expect(container.querySelector('pre.sql')).toBeTruthy(); // SQL 步内嵌代码块
  });
});

describe('L3 详情抽屉（§3.2 #5）', () => {
  it('结论依据 Tab：口径说明 + 命中规则 + 数据路径 + 校验记录', async () => {
    render(<App />);
    await ask('8月按渠道的注册用户数？');
    await screen.findByText('明细即席计算', {}, { timeout: 15000 });
    fireEvent.click(screen.getByRole('button', { name: '详情' }));
    const drawer = screen.getByRole('dialog');
    fireEvent.click(withinDrawer(drawer, '结论依据'));
    expect(withinDrawerText(drawer, /口径说明/)).toBeTruthy();
    expect(withinDrawerText(drawer, /REG_BY_CHANNEL/)).toBeTruthy();
    expect(withinDrawerText(drawer, /DWD · dwd_tr_rgst_df/)).toBeTruthy();
    expect(withinDrawerText(drawer, /同源交叉/)).toBeTruthy();
  });
});

function withinDrawer(drawer: Element, name: string): HTMLElement {
  const btn = Array.from(drawer.querySelectorAll('button')).find((b) => b.textContent === name);
  if (!btn) throw new Error('tab not found: ' + name);
  return btn as HTMLElement;
}
function withinDrawerText(drawer: Element, re: RegExp): boolean {
  return re.test(drawer.textContent ?? '');
}

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

  it('参数追问：追问句 + chips 可点续查', async () => {
    render(<App />);
    await ask('注册用户数是多少？');
    expect(await screen.findByText('请问您要查询哪个月份？', {}, FLOW)).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: '8月' }));
    await screen.findByText('月报口径（预聚合）', {}, { timeout: 15000 }); // 选中即续查 → hot_success
  });

  it('拒答·口径缺失：无对应口径 + 规则候选引导', async () => {
    render(<App />);
    await ask('客户满意度怎么样？');
    expect(await screen.findByText(/尚未注册口径/, {}, FLOW)).toBeTruthy();
    expect(screen.getByText(/纳入口径治理流程/)).toBeTruthy(); // 提示文案（回答含「派生规则候选」，避免多匹配）
  });

  it('拒答·范围超限：如实说明数据边界', async () => {
    render(<App />);
    await ask('9月注册用户数是多少？');
    expect(await screen.findByText(/2026-07-01 ~ 2026-08-31/, {}, FLOW)).toBeTruthy();
    expect(screen.getByText(/数据边界来自语义层元数据/)).toBeTruthy();
  });

  it('拒答·范围外：域说明', async () => {
    render(<App />);
    await ask('日活情况如何？');
    expect(await screen.findByText(/仅注册域/, {}, FLOW)).toBeTruthy();
  });

  it('校验失败：数值对照展示（宁可不答，不出假数）', async () => {
    render(<App />);
    await ask('8月注册数据校验');
    expect(await screen.findByText(/校验未通过，拒绝返回/, {}, FLOW)).toBeTruthy();
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