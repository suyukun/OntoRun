// T502 判据测试（fetch 全 mock，不触真实后端）：
// history_degraded_marker（git 降级诚实标记，正常 git 记录照常显示存档编号短码）/
// 作者筛选（作者=确认人/裁决人口径，从 message 抽取而非 git author）/
// 类型筛选（口径确认/分歧裁决/上报老板人话标签）/ rule_id+object 透传 T102 后端参数。
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { CaliberRule, ConfirmRecord, HistoryCommit, HistoryPayload, Ontology } from "../api";
import HistoryPage from "../pages/HistoryPage";

// 并发负载下 jsdom+antd 渲染可超默认 5s（本文件 solo 全部 <2s）——放宽到 20s。
vi.setConfig({ testTimeout: 20_000 });

// AntD Select 依赖 ResizeObserver，jsdom 未实现——模块级补最小桩。
class ResizeObserverStub {
  observe(): void {}
  unobserve(): void {}
  disconnect(): void {}
}
(globalThis as unknown as Record<string, unknown>).ResizeObserver ??= ResizeObserverStub;

// antd v6 Segmented（内部 Steps/Grid.useBreakpoint）依赖 window.matchMedia，jsdom
// 未实现（真浏览器有）——补最小桩，matches 恒 false 即可。
Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => {},
  }),
});

function rec(partial: Partial<ConfirmRecord> & { time: string }): ConfirmRecord {
  return {
    rule_id: "",
    verdict: "confirmed",
    confirmer: "王工",
    code: "c1",
    commit: "abc1234",
    mode: "git",
    ...partial,
  };
}

function rule(
  partial: Partial<CaliberRule> & { id: string; description: string },
): CaliberRule {
  return {
    source_script: "scripts/auth.sql",
    status: "confirmed",
    related_tables: [],
    last_record: null,
    ...partial,
  };
}

function commit(partial: Partial<HistoryCommit> & { subject: string }): HistoryCommit {
  return {
    short: "0000000",
    author: "苏玉坤",
    time: "2026-09-11T10:00:00+08:00",
    human: "配置/杂项（fortune-admin）：" + partial.subject,
    ...partial,
  };
}

// 降级（json）与正常（git）最近记录各一条
const DEGRADED_ONTOLOGY: Ontology = {
  measures: [],
  dimensions: [],
  summary: { measures: 0, dimensions: 0, rules: 2, pending: 0, confirmed: 2 },
  rules: [
    rule({
      id: "R2",
      description: "退货口径",
      related_tables: ["dwd_refund"],
      last_record: rec({
        rule_id: "R2",
        time: "2026-09-10T09:00:00+08:00",
        code: "f0f0f0",
        commit: null,
        mode: "json",
      }),
    }),
    rule({
      id: "R8",
      description: "授权用户数",
      related_tables: ["dwd_cu_auth"],
      last_record: rec({ rule_id: "R8", time: "2026-09-11T16:04:28+08:00" }),
    }),
  ],
};

const CLEAN_ONTOLOGY: Ontology = {
  ...DEGRADED_ONTOLOGY,
  rules: DEGRADED_ONTOLOGY.rules.map((r) =>
    r.id === "R2" && r.last_record
      ? { ...r, last_record: { ...r.last_record, commit: "5ad97cd", mode: "git" } }
      : r,
  ),
};

// 四类记录齐活：确认 / 裁决（verdict 后缀）/ 上报老板（ESCALATED）/ 开发提交
const PAYLOAD: HistoryPayload = {
  commits: [
    commit({
      short: "a1b2c3d",
      time: "2026-09-11T10:00:00+08:00",
      subject: "chore(fortune-admin): rule R2 confirmed by 王工 [code:111111]",
    }),
    commit({
      short: "b2c3d4e",
      time: "2026-09-11T11:00:00+08:00",
      subject:
        "chore(fortune-admin): rule R8 confirmed by 王工 [code:222222] | R8 verdict: both (decided by 王工)",
    }),
    commit({
      short: "c3d4e5f",
      time: "2026-09-11T12:00:00+08:00",
      subject: "chore(fortune-admin): rule R8 ESCALATED (undecided) by 王工 [code:333333]",
    }),
    commit({
      short: "d4e5f6a",
      author: "李四",
      time: "2026-09-11T13:00:00+08:00",
      subject: "feat(admin): add domain graph view (T403)",
    }),
  ],
  count: 4,
};

function stubFetch(ontology: Ontology) {
  const calls: string[] = [];
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      calls.push(url);
      if (url.startsWith("/api/history")) {
        return new Response(JSON.stringify(PAYLOAD), { status: 200 });
      }
      if (url.startsWith("/api/ontology")) {
        return new Response(JSON.stringify(ontology), { status: 200 });
      }
      return new Response("{}", { status: 404 });
    }),
  );
  return calls;
}

// 页面上恰有三个 Select，渲染顺序 = [作者, 规则, 关联表]
function openSelect(index: number) {
  const selects = document.querySelectorAll(".ant-select");
  fireEvent.mouseDown(selects[index]!);
}

function clickOption(label: string) {
  // 选项经 portal 挂 body，限定未隐藏下拉里的 option 节点
  const option = document.querySelector(
    ".ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option[title=\"" +
      label +
      "\"]",
  );
  expect(option).toBeTruthy();
  fireEvent.click(option!);
}

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("HistoryPage git 降级诚实标记 (T502)", () => {
  it("history_degraded_marker: 降级记录明示「未产生存档编号（降级记录）」，正常 git 记录照常显示短码", async () => {
    stubFetch(DEGRADED_ONTOLOGY);
    render(<HistoryPage />);
    await screen.findByText("a1b2c3d");
    expect(screen.getByText(/未产生存档编号（降级记录）/)).toBeTruthy();
    const body = document.body.textContent ?? "";
    expect(body).toContain("R2");
    expect(body).toContain("王工");
    expect(body).toContain("2026-09-10 09:00");
    expect(body).toContain("未产生存档编号");
    // 正常 git 记录不受影响：短码照常显示
    expect(screen.getByText("a1b2c3d")).toBeTruthy();
    expect(screen.getByText("c3d4e5f")).toBeTruthy();
  });

  it("无降级记录时不出现降级横幅", async () => {
    stubFetch(CLEAN_ONTOLOGY);
    render(<HistoryPage />);
    await screen.findByText("a1b2c3d");
    expect(screen.queryByText(/未产生存档编号/)).toBeNull();
  });
});

describe("HistoryPage 作者/类型筛选 (T502)", () => {
  it("作者筛选：作者=确认人/裁决人（王工），不是 git author（苏玉坤）；选中后只剩该作者记录", async () => {
    stubFetch(CLEAN_ONTOLOGY);
    render(<HistoryPage />);
    await screen.findByText("a1b2c3d");
    // 行内作者 Tag 显示确认人口径，git author 不上墙
    expect(screen.getAllByText("王工").length).toBeGreaterThan(0);
    expect(screen.queryByText("苏玉坤")).toBeNull();
    openSelect(0);
    clickOption("李四");
    expect(screen.getByText("d4e5f6a")).toBeTruthy();
    expect(screen.queryByText("a1b2c3d")).toBeNull();
    expect(screen.queryByText("c3d4e5f")).toBeNull();
    expect(screen.getByText(/筛选出 1 \/ 4 条/)).toBeTruthy();
  });

  it("类型筛选含「上报老板」人话标签：选中后只剩 ESCALATED 记录", async () => {
    stubFetch(CLEAN_ONTOLOGY);
    render(<HistoryPage />);
    await screen.findByText("a1b2c3d");
    // Segmented 是 DOM 里第一个「上报老板」文本（行内 Tag 在其后）
    fireEvent.click(screen.getAllByText("上报老板")[0]!);
    expect(screen.getByText("c3d4e5f")).toBeTruthy();
    expect(screen.queryByText("a1b2c3d")).toBeNull();
    expect(screen.queryByText("b2c3d4e")).toBeNull();
    expect(screen.queryByText("d4e5f6a")).toBeNull();
    expect(screen.getByText(/筛选出 1 \/ 4 条/)).toBeTruthy();
  });

  it("类型=口径确认：confirmed 记录保留、驳回归口径确认类", async () => {
    stubFetch(CLEAN_ONTOLOGY);
    render(<HistoryPage />);
    await screen.findByText("a1b2c3d");
    // Segmented 是 DOM 里第一个「口径确认」文本（行内 Tag 在其后）
    fireEvent.click(screen.getAllByText("口径确认")[0]!);
    expect(screen.getByText("a1b2c3d")).toBeTruthy();
    expect(screen.queryByText("b2c3d4e")).toBeNull();
    expect(screen.queryByText("c3d4e5f")).toBeNull();
    expect(screen.queryByText("d4e5f6a")).toBeNull();
  });

  it("筛选无结果：Empty 有出路，清除筛选恢复全列", async () => {
    stubFetch(CLEAN_ONTOLOGY);
    render(<HistoryPage />);
    await screen.findByText("a1b2c3d");
    fireEvent.click(screen.getAllByText("上报老板")[0]!);
    openSelect(0);
    clickOption("李四");
    expect(screen.getByText(/当前筛选下没有匹配记录/)).toBeTruthy();
    // 筛选行与 Empty 里各有一个清除筛选按钮，动作相同，点第一个
    fireEvent.click(screen.getAllByRole("button", { name: /清除筛选/ })[0]!);
    expect(await screen.findByText("a1b2c3d")).toBeTruthy();
    expect(screen.getByText("d4e5f6a")).toBeTruthy();
  });
});

describe("HistoryPage T102 后端参数透传", () => {
  it("选规则/关联表后请求带 rule_id 与 object 参数，首载不带", async () => {
    const calls = stubFetch(CLEAN_ONTOLOGY);
    render(<HistoryPage />);
    await screen.findByText("a1b2c3d");
    expect(calls[0]).not.toContain("rule_id=");
    openSelect(1);
    clickOption("R2　退货口径");
    await screen.findByText(/筛选出/);
    expect(calls.some((u) => u.includes("rule_id=R2"))).toBe(true);
    openSelect(2);
    clickOption("dwd_refund");
    await screen.findByText(/筛选出/);
    expect(
      calls.some((u) => u.includes("rule_id=R2") && u.includes("object=dwd_refund")),
    ).toBe(true);
  });
});
