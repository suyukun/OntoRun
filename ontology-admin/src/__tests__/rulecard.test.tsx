// T205 RuleCard 三问卡 v2 判据测试（组件 fetch 全 mock，不触真实后端）：
// qc3_default_collapsed / qc4_plain_first_line / trial 成功+失败不阻塞 /
// expression_expandable / confirm_requires_name / 确认流回归。
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { CaliberRule } from "../api";
import RuleCard from "../components/RuleCard";

const rule: CaliberRule = {
  id: "R7",
  description: "只有已授权的记录才算授权用户，对吗？",
  source_script: "ads_chnl_auth_qty_df.sql",
  status: "unverified",
  related_tables: ["ads_chnl_auth_qty_df"],
  last_record: null,
};

const trialOk = {
  rule_id: "R7",
  month: "2026-08",
  value: 552,
  unit: " 人",
  generated_at: "2026-09-11T10:00:00",
  source: "semantic_query",
};

type Stub = {
  trial?: { ok: boolean; body?: unknown };
  confirm?: { ok: boolean; body?: unknown };
};

function stubFetch(stub: Stub) {
  const fn = vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url.includes("/api/trial/")) {
      const t = stub.trial ?? { ok: false };
      return new Response(JSON.stringify(t.body ?? {}), {
        status: t.ok ? 200 : 503,
      });
    }
    if (url.includes("/confirm")) {
      const c = stub.confirm ?? { ok: false };
      return new Response(JSON.stringify(c.body ?? {}), {
        status: c.ok ? 200 : 500,
      });
    }
    return new Response("{}", { status: 404 });
  });
  vi.stubGlobal("fetch", fn);
  return fn;
}

afterEach(() => {
  cleanup(); // vitest globals 关闭，RTL 自动清理不生效，显式卸载防 DOM 跨用例累积
  vi.unstubAllGlobals();
});

function renderCard(overrides?: { confirmer?: string; expression?: string }) {
  return render(
    <RuleCard
      rule={rule}
      confirmer={overrides?.confirmer ?? "王工"}
      onDone={() => {}}
      expression={overrides?.expression}
    />
  );
}

describe("RuleCard v2 (T205)", () => {
  it("qc4_plain_first_line: 首行是人话标题，规则号不做标题前缀", () => {
    stubFetch({ trial: { ok: false } });
    const { container } = renderCard();
    expect(screen.getByText(rule.description)).toBeTruthy();
    const title = container.querySelector(".ant-card-head-title");
    expect(title?.textContent).toContain(rule.description);
    expect(title?.textContent?.trim().startsWith("R7")).toBe(false);
    // 规则号退居右侧元信息
    expect(screen.getByText("R7")).toBeTruthy();
  });

  it("qc11: 状态词用「待确认」", () => {
    stubFetch({ trial: { ok: false } });
    renderCard();
    expect(screen.getByText("待确认")).toBeTruthy();
  });

  it("qc3_default_collapsed: 技术细节默认折叠，展开可见出处脚本", async () => {
    stubFetch({ trial: { ok: false } });
    renderCard();
    // 默认收起：出处脚本不在 DOM
    expect(screen.queryByText("ads_chnl_auth_qty_df.sql")).toBeNull();
    fireEvent.click(screen.getByText("技术细节（给工程师看的）"));
    expect(await screen.findByText("ads_chnl_auth_qty_df.sql")).toBeTruthy();
  });

  it("expression_expandable: 展开技术细节可见 registry 表达式原文", async () => {
    stubFetch({ trial: { ok: false } });
    const expr = "COUNT(DISTINCT user_id) WHERE auth_flag = 'Y'";
    renderCard({ expression: expr });
    expect(screen.queryByText(expr)).toBeNull();
    fireEvent.click(screen.getByText("技术细节（给工程师看的）"));
    expect(await screen.findByText(expr)).toBeTruthy();
  });

  it("trial success: 试算行显示「按此口径跑 2026 年 8 月 = 552 人」", async () => {
    stubFetch({ trial: { ok: true, body: trialOk } });
    renderCard();
    expect(
      await screen.findByText(/按这条计算规则跑 2026 年 8 月 = 552 人/)
    ).toBeTruthy();
  });

  it("trial_failure_nonblocking: 失败灰条「试算暂不可用」且不阻塞确认", async () => {
    const fetchFn = stubFetch({
      trial: { ok: false },
      confirm: {
        ok: true,
        body: {
          record: { commit: "a1b2c3d", confirmer: "王工", verdict: "confirmed" },
          message: "已确认",
        },
      },
    });
    const onDone = vi.fn();
    render(<RuleCard rule={rule} confirmer="王工" onDone={onDone} />);
    expect(await screen.findByText("试算暂不可用")).toBeTruthy();
    // 主流程不被试算失败阻塞：确认按钮可用，点击后发出 confirm 请求
    const confirmBtn = screen.getByRole("button", { name: "✓ 对，就这样算" });
    expect((confirmBtn as HTMLButtonElement).disabled).toBe(false);
    fireEvent.click(confirmBtn);
    await waitFor(() => expect(onDone).toHaveBeenCalled());
    const confirmCall = fetchFn.mock.calls.find((c) =>
      String(c[0]).includes("/confirm")
    );
    expect(confirmCall).toBeTruthy();
    expect(String(confirmCall?.[0])).toContain("/api/rules/R7/confirm");
  });

  it("confirm_requires_name: 确认人为空禁用按钮并提示「身份是确认的一部分」", async () => {
    const fetchFn = stubFetch({ trial: { ok: false } });
    renderCard({ confirmer: "  " });
    const confirmBtn = screen.getByRole("button", { name: "✓ 对，就这样算" });
    expect((confirmBtn as HTMLButtonElement).disabled).toBe(true);
    expect(screen.getByText(/身份是确认的一部分/)).toBeTruthy();
    fireEvent.click(confirmBtn);
    await new Promise((r) => setTimeout(r, 0));
    expect(fetchFn.mock.calls.some((c) => String(c[0]).includes("/confirm"))).toBe(
      false
    );
  });

  it("confirm flow: 沿用 confirmRule，POST body 带身份（既有拼写 confirmeer 双 e）且 verdict=confirmed", async () => {
    const fetchFn = stubFetch({
      trial: { ok: false },
      confirm: {
        ok: true,
        body: {
          record: { commit: null, confirmer: "王工", verdict: "confirmed" },
          message: "已记录：王工 确认",
        },
      },
    });
    const onDone = vi.fn();
    render(<RuleCard rule={rule} confirmer="王工" onDone={onDone} />);
    fireEvent.click(screen.getByRole("button", { name: "✓ 对，就这样算" }));
    await waitFor(() => expect(onDone).toHaveBeenCalled());
    const call = fetchFn.mock.calls.find((c) =>
      String(c[0]).includes("/confirm")
    );
    expect(call).toBeTruthy();
    const [url, init] = call as unknown as [string, RequestInit];
    expect(url).toContain("/api/rules/R7/confirm");
    expect(JSON.parse(String(init.body))).toEqual({
      verdict: "confirmed",
      confirmeer: "王工",
    });
  });

  it("readOnly: 只展示并引导去确认页，不渲染行动区", () => {
    stubFetch({ trial: { ok: false } });
    render(
      <RuleCard rule={rule} confirmer="" onDone={() => {}} readOnly />
    );
    expect(screen.getByText("去口径确认页处理 →")).toBeTruthy();
    expect(
      screen.queryByRole("button", { name: "✓ 对，就这样算" })
    ).toBeNull();
  });

  it("T-U1 三问人话分区：①是什么数/②怎么算的/③影响哪些表，技术细节标注给工程师", () => {
    stubFetch({ trial: { ok: false } });
    renderCard();
    expect(screen.getByText(/① 是什么数？/)).toBeTruthy();
    expect(screen.getByText(/② 怎么算的？/)).toBeTruthy();
    expect(screen.getByText(/③ 影响哪些表？/)).toBeTruthy();
    expect(screen.getByText("技术细节（给工程师看的）")).toBeTruthy();
  });
});
