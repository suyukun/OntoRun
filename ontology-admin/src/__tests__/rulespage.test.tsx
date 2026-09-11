// T101 判据测试（fetch 全 mock，不触真实后端——卡片内试算请求 503 降级，不阻塞渲染）：
// rules_page_sort_and_count（未确认置顶+组内排队时长降序+页头计数随筛选/确认状态）/
// 筛选出处脚本、所属对象（选项从 payload 去重）/ 单列纵排结构断言 / qc11 术语统一。
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { CaliberRule, ConfirmRecord, Ontology } from "../api";
import RulesPage from "../pages/RulesPage";

// AntD Select 的 rc-resize-observer 依赖 ResizeObserver，jsdom 未实现——模块级补最小桩（空实现即可）。
class ResizeObserverStub {
  observe(): void {}
  unobserve(): void {}
  disconnect(): void {}
}
(globalThis as unknown as Record<string, unknown>).ResizeObserver ??= ResizeObserverStub;

function rec(partial: Partial<ConfirmRecord> & { time: string }): ConfirmRecord {
  return {
    rule_id: "",
    verdict: "rejected",
    confirmer: "王工",
    code: "c1",
    commit: "abc1234",
    mode: "reject",
    ...partial,
  };
}

function rule(
  partial: Partial<CaliberRule> & { id: string; description: string },
): CaliberRule {
  return {
    source_script: "scripts/auth.sql",
    status: "unverified",
    related_tables: ["ads_chnl_auth_qty_df"],
    last_record: null,
    ...partial,
  };
}

// 传入顺序故意打乱。期望序（rules_page_sort_and_count）：
// R1 无记录（=最早排队）→ R5 无记录（同档按 id）→ R2 记录 09-05（等更久）→
// R3 记录 09-10（等更短）→ 已确认 R4/R6 沉底按 id。
const payload: Ontology = {
  measures: [],
  dimensions: [],
  // summary.pending=99 是干扰值：页头计数必须来自 rules 本身，不取全量 summary
  summary: { measures: 0, dimensions: 0, rules: 6, pending: 99, confirmed: 0 },
  rules: [
    rule({
      id: "R4",
      description: "R4 已确认的口径",
      status: "confirmed",
      last_record: rec({ rule_id: "R4", verdict: "confirmed", time: "2026-09-01T08:00:00" }),
    }),
    rule({
      id: "R3",
      description: "R3 昨天驳回回队",
      last_record: rec({ rule_id: "R3", time: "2026-09-10T09:00:00" }),
    }),
    rule({
      id: "R2",
      description: "R2 一周前驳回回队",
      last_record: rec({ rule_id: "R2", time: "2026-09-05T09:00:00" }),
    }),
    rule({ id: "R1", description: "R1 从未处理过" }),
    rule({
      id: "R5",
      description: "R5 另一脚本的口径",
      source_script: "scripts/refund.sql",
      related_tables: ["dwd_refund"],
    }),
    rule({ id: "R6", description: "R6 已确认的另一条", status: "confirmed" }),
  ],
};

function stubFetch() {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => new Response("{}", { status: 503 })),
  );
}

// 页面上恰有两个 Select，渲染顺序 = [出处脚本, 所属对象]
function openSelect(index: number) {
  const selects = document.querySelectorAll(".ant-select");
  fireEvent.mouseDown(selects[index]!);
}

function clickOption(label: string) {
  // 选项经 portal 挂 body，且卡内折叠区可能含同文案文本，故限定未隐藏下拉里的 option 节点
  const option = document.querySelector(
    '.ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option[title="' +
      label +
      '"]',
  );
  expect(option).toBeTruthy();
  fireEvent.click(option!);
}

function queueText(): string {
  return (screen.getByTestId("rules-queue").textContent ?? "").replace(/\s+/g, "");
}

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("RulesPage 确认队列 (T101)", () => {
  it("rules_page_sort_and_count: 未确认置顶、组内排队时长降序（无记录=最早排队）、已确认沉底", () => {
    stubFetch();
    render(<RulesPage ontology={payload} reload={() => {}} />);
    const text = queueText();
    const order = [
      "R1从未处理过",
      "R5另一脚本的口径",
      "R2一周前驳回回队",
      "R3昨天驳回回队",
      "R4已确认的口径",
      "R6已确认的另一条",
    ];
    const positions = order.map((d) => text.indexOf(d));
    positions.forEach((p) => expect(p).toBeGreaterThanOrEqual(0));
    expect(positions).toEqual([...positions].sort((a, b) => a - b));
  });

  it("页头计数随确认状态：待确认 4 条 / 共 6 条，取 rules 不取 summary（干扰值 99 不出现）", () => {
    stubFetch();
    render(<RulesPage ontology={payload} reload={() => {}} />);
    expect(screen.getByText(/当前待确认 4 条 \/ 列表共 6 条/)).toBeTruthy();
    expect(screen.queryByText(/99/)).toBeNull();
  });

  it("筛选出处脚本：选项 payload 去重，选中后只剩匹配项，计数同步", () => {
    stubFetch();
    render(<RulesPage ontology={payload} reload={() => {}} />);
    openSelect(0);
    const options = document.querySelectorAll(
      ".ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option",
    );
    expect(options).toHaveLength(2); // 5 条待确认共享 auth.sql + R5 独用 refund.sql
    clickOption("scripts/refund.sql");
    expect(screen.getByText("R5 另一脚本的口径")).toBeTruthy();
    expect(screen.queryByText("R1 从未处理过")).toBeNull();
    expect(screen.queryByText("R4 已确认的口径")).toBeNull();
    expect(screen.getByText(/当前待确认 1 条 \/ 列表共 1 条/)).toBeTruthy();
  });

  it("筛选所属对象：只剩关联该表的规则，计数同步", () => {
    stubFetch();
    render(<RulesPage ontology={payload} reload={() => {}} />);
    openSelect(1);
    clickOption("dwd_refund");
    expect(screen.getByText("R5 另一脚本的口径")).toBeTruthy();
    expect(screen.queryByText("R2 一周前驳回回队")).toBeNull();
    expect(screen.getByText(/当前待确认 1 条 \/ 列表共 1 条/)).toBeTruthy();
  });

  it("筛选无结果：Empty 有说明与出路，清除筛选恢复全列", () => {
    stubFetch();
    render(<RulesPage ontology={payload} reload={() => {}} />);
    openSelect(0);
    clickOption("scripts/refund.sql");
    openSelect(1);
    clickOption("ads_chnl_auth_qty_df"); // 与 refund.sql 无交集
    expect(screen.getByText(/当前筛选下没有匹配的计算规则/)).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: /清除筛选/ }));
    expect(screen.getByText("R1 从未处理过")).toBeTruthy();
    expect(screen.getByText(/当前待确认 4 条 \/ 列表共 6 条/)).toBeTruthy();
  });

  it("单列纵排：队列容器纵向 flex、卡间距 16px，无多列网格", () => {
    stubFetch();
    render(<RulesPage ontology={payload} reload={() => {}} />);
    const queue = screen.getByTestId("rules-queue");
    const style = getComputedStyle(queue);
    expect(style.display).toBe("flex");
    expect(style.flexDirection).toBe("column");
    expect(["", "none"]).toContain(style.gridTemplateColumns);
    expect(queue.children).toHaveLength(6); // 每规则一张卡，直接子节点=卡（无额外包裹层）
  });

  it("qc11 术语：页面用「待确认/已确认」，不出现「钉死/未确认」", () => {
    stubFetch();
    render(<RulesPage ontology={payload} reload={() => {}} />);
    const text = document.body.textContent ?? "";
    expect(text).toContain("待确认");
    expect(text).toContain("已确认");
    expect(text).not.toContain("钉死");
    expect(text).not.toContain("未确认");
  });

  it("T-U1 页头引导语自解释：这页列什么、先看什么、拿不准怎么办", () => {
    stubFetch();
    render(<RulesPage ontology={payload} reload={() => {}} />);
    expect(screen.getByText(/这里列出系统里所有数字的计算规则/)).toBeTruthy();
    expect(screen.getByText(/没核对过的排前面/)).toBeTruthy();
    expect(screen.getByText(/上报老板/)).toBeTruthy();
  });
});