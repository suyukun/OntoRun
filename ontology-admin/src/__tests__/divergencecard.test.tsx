// T203 R8 分歧裁决卡判据测试（组件 fetch 全 mock，不触真实后端——T202 并行开发中）：
// r8_divergence_card（双口径对照，595/552/55 名数字+适用场景可见）/
// 四选项存在且 both 推荐预选 / 提交 body 含 decision.option_key /
// r8_escalate_recorded_without_flip（toast 文案精确匹配+卡仍待确认可再次裁决）/
// 无 divergence 不渲染对照卡 / 禁用态。
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { message } from "antd";

import type { CaliberRule, DivergenceOption } from "../api";
import DivergenceCard from "../components/DivergenceCard";
import RuleCard from "../components/RuleCard";

// 对照数据 = T201 装配的 R8 实证（ontology.py _DIVERGENCES），数字非手填
const divergence: DivergenceOption[] = [
  {
    key: "account",
    label: "按账户计数（授权账户数）",
    value_evidence:
      "595（2026-08 镜像实证：ADS 脚本按行计数，一人多渠道授权重复计入）",
    applies_to: "与 ADS 报表/脚本逐格对账场景：逐格相等仅在账户口径下成立",
  },
  {
    key: "user",
    label: "按用户去重（授权用户数）",
    value_evidence:
      "552（2026-08 镜像实证：语义层 auth_user_cnt 按用户去重；另 55 名无金融注册授权用户被内联注册表丢弃）",
    applies_to: "业务统计授权用户数场景：一人多渠道授权不重复计",
  },
];

const rule: CaliberRule = {
  id: "R8",
  description: "授权用户数：按账户计还是按用户去重？",
  source_script: "ads_chnl_auth_qty_df.sql",
  status: "unverified",
  related_tables: ["ads_chnl_auth_qty_df"],
  last_record: null,
  divergence,
  decision: null,
};

const confirmOk = {
  record: { commit: "f47ac10", confirmer: "王工", verdict: "confirmed" },
  message: "已记录：王工 确认 R8",
};

type Stub = {
  confirm?: { ok: boolean; body?: unknown };
};

function stubFetch(stub: Stub = {}) {
  const fn = vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url.includes("/api/trial/")) {
      return new Response("{}", { status: 503 });
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
  cleanup(); // vitest globals 关闭，显式卸载防 DOM 跨用例累积
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

function confirmCalls(fn: ReturnType<typeof stubFetch>) {
  return fn.mock.calls.filter((c) => String(c[0]).includes("/confirm"));
}

// 拦截 toast（组件内 antd message 静态调用），便于精确断言文案
function spyMessageSuccess() {
  return vi
    .spyOn(message, "success")
    .mockImplementation(
      () =>
        Promise.resolve() as unknown as ReturnType<typeof message.success>
    );
}

describe("DivergenceCard (T203)", () => {
  it("r8_divergence_card: 两口径并列对照，595/552/55 名数字与适用场景可见", () => {
    stubFetch();
    render(<DivergenceCard rule={rule} confirmer="王工" onDone={() => {}} />);
    expect(screen.getByText(/按账户计数（授权账户数）/)).toBeTruthy();
    expect(screen.getByText(/按用户去重（授权用户数）/)).toBeTruthy();
    expect(screen.getByText(/595（2026-08 镜像实证/)).toBeTruthy();
    expect(screen.getByText(/552（2026-08 镜像实证/)).toBeTruthy();
    expect(screen.getByText(/55 名无金融注册授权用户/)).toBeTruthy();
    // 适用场景（人话）：账户口径=对账，用户口径=业务统计
    expect(screen.getByText(/适用场景：与 ADS 报表\/脚本逐格对账场景/)).toBeTruthy();
    expect(screen.getByText(/适用场景：业务统计授权用户数场景/)).toBeTruthy();
  });

  it("裁决四选项存在，both 标注推荐且默认预选", () => {
    stubFetch();
    render(<DivergenceCard rule={rule} confirmer="王工" onDone={() => {}} />);
    const account = screen.getByRole("radio", { name: /按账户计数/ }) as HTMLInputElement;
    const user = screen.getByRole("radio", { name: /按用户去重/ }) as HTMLInputElement;
    const both = screen.getByRole("radio", { name: /双口径并存/ }) as HTMLInputElement;
    const escalate = screen.getByRole("radio", { name: /升级老板裁决/ }) as HTMLInputElement;
    expect(both.checked).toBe(true); // NC-Q2 双口径并存默认预选
    expect(account.checked).toBe(false);
    expect(user.checked).toBe(false);
    expect(escalate.checked).toBe(false);
    expect(screen.getByText("推荐")).toBeTruthy();
  });

  it("三选一提交：body 含 decision.option_key=both，toast 含版本短码，走正常确认流", async () => {
    const spy = spyMessageSuccess();
    const fetchFn = stubFetch({ confirm: { ok: true, body: confirmOk } });
    const onDone = vi.fn();
    render(<DivergenceCard rule={rule} confirmer="王工" onDone={onDone} />);
    fireEvent.click(screen.getByRole("button", { name: /✓ 提交裁决/ }));
    await waitFor(() => expect(onDone).toHaveBeenCalled());
    const calls = confirmCalls(fetchFn);
    expect(calls).toHaveLength(1);
    const [url, init] = calls[0] as unknown as [string, RequestInit];
    expect(url).toContain("/api/rules/R8/confirm");
    expect(JSON.parse(String(init.body))).toEqual({
      verdict: "confirmed",
      confirmeer: "王工",
      decision: { option_key: "both" },
    });
    // toast 含版本短码（来自后端响应）
    expect(spy).toHaveBeenCalledWith(
      expect.stringContaining("f47ac10"),
      5
    );
  });

  it("禁用态：确认人为空禁用提交按钮并提示「身份是确认的一部分」", () => {
    const fetchFn = stubFetch();
    render(<DivergenceCard rule={rule} confirmer="  " onDone={() => {}} />);
    const btn = screen.getByRole("button", { name: /✓ 提交裁决/ }) as HTMLButtonElement;
    expect(btn.disabled).toBe(true);
    expect(screen.getByText(/身份是确认的一部分/)).toBeTruthy();
    fireEvent.click(btn);
    expect(confirmCalls(fetchFn)).toHaveLength(0);
  });
});

describe("RuleCard 接线（T203）", () => {
  it("r8_escalate_recorded_without_flip: escalate 提交后 toast 文案精确匹配，卡仍待确认且可再次裁决", async () => {
    const spy = spyMessageSuccess();
    const fetchFn = stubFetch({ confirm: { ok: true, body: confirmOk } });
    const onDone = vi.fn();
    render(<RuleCard rule={rule} confirmer="王工" onDone={onDone} />);
    fireEvent.click(screen.getByRole("radio", { name: /升级老板裁决/ }));
    fireEvent.click(screen.getByRole("button", { name: /✓ 提交裁决/ }));
    // toast 文案精确匹配（王工走查修订第 5 条）
    await waitFor(() =>
      expect(spy).toHaveBeenCalledWith("已留痕并通知负责人（线下）", 5)
    );
    // 状态不翻转：仍待确认，裁决卡留在原位（onDone 未触发刷新）
    expect(screen.getByText("待确认")).toBeTruthy();
    expect(screen.getByRole("radio", { name: /双口径并存/ })).toBeTruthy();
    expect(onDone).not.toHaveBeenCalled();
    const calls = confirmCalls(fetchFn);
    expect(calls).toHaveLength(1);
    expect(JSON.parse(String((calls[0] as unknown as [string, RequestInit])[1].body))).toEqual({
      verdict: "confirmed",
      confirmeer: "王工",
      decision: { option_key: "escalate" },
    });
    // 可再次裁决：等一轮微任务（loading 布尔态清除；jsdom 不触发 antd 退场动画
    // end 事件，残留的 loading 图标 aria-label 会拼进按钮可访问名，故用正则匹配），
    // 改选账户口径再提交，正常确认流走通
    await screen.findByRole("button", { name: /✓ 提交裁决/ });
    fireEvent.click(screen.getByRole("radio", { name: /按账户计数/ }));
    fireEvent.click(screen.getByRole("button", { name: /✓ 提交裁决/ }));
    await waitFor(() => expect(onDone).toHaveBeenCalled());
    expect(confirmCalls(fetchFn)).toHaveLength(2);
    expect(
      JSON.parse(String((confirmCalls(fetchFn)[1] as unknown as [string, RequestInit])[1].body))
    ).toEqual({
      verdict: "confirmed",
      confirmeer: "王工",
      decision: { option_key: "account" },
    });
  });

  it("接线：divergence 非空渲染对照卡（三问确认按钮退位）", () => {
    stubFetch();
    render(<RuleCard rule={rule} confirmer="王工" onDone={() => {}} />);
    expect(screen.getByText(/两口径对照/)).toBeTruthy();
    expect(screen.queryByRole("button", { name: "✓ 对，就这样算" })).toBeNull();
    expect(screen.getAllByRole("radio")).toHaveLength(4);
  });

  it("无 divergence 规则不渲染对照卡，保持 T205 原三问卡确认按钮", () => {
    stubFetch();
    const plain: CaliberRule = { ...rule, id: "R7", divergence: null, decision: null };
    render(<RuleCard rule={plain} confirmer="王工" onDone={() => {}} />);
    expect(screen.queryByText(/两口径对照/)).toBeNull();
    expect(screen.queryByText(/按账户计数（授权账户数）/)).toBeNull();
    expect(screen.queryAllByRole("radio")).toHaveLength(0);
    expect(
      screen.getByRole("button", { name: "✓ 对，就这样算" })
    ).toBeTruthy();
  });
});
