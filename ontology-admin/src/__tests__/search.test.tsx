// T301 search_direct_hit：顶栏全局搜索（数据=mock /api/ontology payload，前端过滤，不触真实后端）。
// 判据（门槛稿 §A2-US4/§A3/§C1-T301）：输入「授权」出数字/规则建议（纯注册项不入候选）；
// 选中触发路由跳转——数字/表 → #/object/{kind}/{id}，规则 → #/rules（规则页无路由参数，跳页即最小直达）。
// 附断言：US4 导航改名（首页 / 数字与口径）。
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type { Lineage, Ontology } from "../api";
import App from "../App";

// 夹具对齐 registry.py 真实 id/描述（auth_user_cnt/R8/R9/ads_chnl_auth_qty_df），非凭空造数
const ontologyFixture: Ontology = {
  measures: [
    {
      id: "reg_user_cnt",
      description: "注册用户数：窗口内完成注册的去重用户数",
      expression: "count(distinct user_id)",
      source_table: "dwd_cu_rgst_fin_di",
      source_alias: "t",
      time_field: "rgst_dt",
      filters: [],
    },
    {
      id: "auth_user_cnt",
      description: "授权用户数：窗口内完成授权（grant_fg=1 且 grant_dt 落窗）的去重用户数",
      expression: "count(distinct user_id)",
      source_table: "dwd_cu_auth_fin_di",
      source_alias: "t",
      time_field: "grant_dt",
      filters: [],
    },
    {
      id: "reg_to_auth_rate",
      description: "注册→授权转化率 = auth_user_cnt / reg_user_cnt",
      expression: "auth_user_cnt / reg_user_cnt",
      source_table: "dwd_cu_rgst_fin_di",
      source_alias: "t",
      time_field: "rgst_dt",
      filters: [],
    },
  ],
  dimensions: [],
  rules: [
    {
      id: "R1",
      description: "注册口径：注册明细按天去重",
      source_script: "数仓脚本/脚本dwd_cu_rgst_fin_di.sql",
      status: "confirmed",
      related_tables: ["dwd_cu_rgst_fin_di"],
      last_record: null,
    },
    {
      id: "R8",
      description: "授权计数口径分歧（未决）：按账户计还是按用户去重",
      source_script: "数仓脚本/脚本ads_chnl_auth_qty_df.sql",
      status: "unverified",
      related_tables: ["ads_chnl_auth_qty_df"],
      last_record: null,
    },
    {
      id: "R9",
      description: "授权渠道归属：经用户维注册渠道名归组",
      source_script: "数仓脚本/脚本ads_chnl_auth_qty_df.sql",
      status: "unverified",
      related_tables: ["ads_chnl_auth_qty_df"],
      last_record: null,
    },
  ],
  summary: { measures: 3, dimensions: 0, rules: 3, pending: 2, confirmed: 1 },
};

const lineageFixture: Lineage = {
  nodes: [],
  edges: [],
  layers: {},
  stats: { nodes: 0, edges: 0, unconfirmed_edges: 0 },
};

function stubFetch() {
  const fn = vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url.startsWith("/api/ontology")) {
      return new Response(JSON.stringify(ontologyFixture), { status: 200 });
    }
    if (url.startsWith("/api/lineage")) {
      return new Response(JSON.stringify(lineageFixture), { status: 200 });
    }
    return new Response("{}", { status: 404 });
  });
  vi.stubGlobal("fetch", fn);
  return fn;
}

// antd 部件在 jsdom 需要的宿主能力；测试起始路由避开 ReactFlow 首页，stub 兜底防测量报错
class ResizeObserverStub {
  observe() {}
  unobserve() {}
  disconnect() {}
}
const matchMediaStub = (query: string) => ({
  matches: false,
  media: query,
  onchange: null,
  addListener: () => {},
  removeListener: () => {},
  addEventListener: () => {},
  removeEventListener: () => {},
  dispatchEvent: () => false,
});

// antd v6 的下拉选项元素没有 role="option"（v5 有），按 .ant-select-item-option 类名查询；
// 搜索框用 header(role=banner) 作用域定位：页面内 Select（筛选器）也是 combobox role，全局查询会撞车。
function optionNodes() {
  return [...document.querySelectorAll(".ant-select-item-option")];
}

async function openSearch(keyword: string) {
  const input = within(screen.getByRole("banner")).getByRole("combobox");
  fireEvent.mouseDown(input); // rc-select 以 mousedown 开下拉
  fireEvent.change(input, { target: { value: keyword } });
  await waitFor(() => expect(optionNodes().length).toBeGreaterThan(0));
}

function optionTexts() {
  return optionNodes().map((o) => o.textContent ?? "");
}

beforeEach(() => {
  vi.stubGlobal("ResizeObserver", ResizeObserverStub);
  vi.stubGlobal("matchMedia", matchMediaStub);
  stubFetch();
});

afterEach(() => {
  cleanup(); // vitest globals 关闭，显式卸载防 DOM 跨用例累积
  vi.unstubAllGlobals();
  window.location.hash = "";
});

describe("T301 顶栏全局搜索 search_direct_hit", () => {
  it("输入「授权」出数字/规则分组建议，纯注册项不入候选；导航改名就位", async () => {
    window.location.hash = "#/rules";
    render(<App />);
    // US4 导航文案：首页 / 数字与口径 / 口径确认 / 变更历史
    expect(screen.getByText("首页")).toBeTruthy();
    expect(screen.getByText("数字与口径")).toBeTruthy();

    await openSearch("授权");
    const texts = optionTexts();
    expect(texts.some((t) => t.startsWith("auth_user_cnt"))).toBe(true);
    expect(texts.some((t) => t.startsWith("R8"))).toBe(true);
    expect(texts.some((t) => t.startsWith("R9"))).toBe(true);
    expect(texts.every((t) => !t.includes("注册用户数"))).toBe(true);
    // 分组头：数字 / 规则；表 id 不含中文「授权」，表组不出现
    expect(screen.getByText("数字")).toBeTruthy();
    expect(screen.getByText("规则")).toBeTruthy();
    expect(screen.queryByText("表")).toBeNull();
  });

  it("选中数字建议 → 直达对象详情 #/object/measure/auth_user_cnt", async () => {
    window.location.hash = "#/rules";
    render(<App />);
    await openSearch("授权");
    const target = optionNodes().find((o) =>
      (o.textContent ?? "").startsWith("auth_user_cnt"),
    );
    expect(target).toBeTruthy();
    fireEvent.click(target!);
    await waitFor(() =>
      expect(window.location.hash).toBe("#/object/measure/auth_user_cnt"),
    );
  });

  it("选中规则建议 → 直达口径确认页 #/rules", async () => {
    window.location.hash = "#/objects";
    render(<App />);
    await openSearch("授权");
    const target = optionNodes().find((o) =>
      (o.textContent ?? "").startsWith("R8"),
    );
    expect(target).toBeTruthy();
    fireEvent.click(target!);
    await waitFor(() => expect(window.location.hash).toBe("#/rules"));
  });

  it("选中表建议 → 直达该表对象详情 #/object/table/ads_chnl_auth_qty_df", async () => {
    window.location.hash = "#/rules";
    render(<App />);
    await openSearch("ads_chnl_auth");
    // 不能 getByText：RulesPage 卡片上的 related_tables 标签是同文本节点，撞车
    const target = optionNodes().find(
      (o) => o.textContent === "ads_chnl_auth_qty_df",
    );
    expect(target).toBeTruthy();
    fireEvent.click(target!);
    await waitFor(() =>
      expect(window.location.hash).toBe("#/object/table/ads_chnl_auth_qty_df"),
    );
  });

  it("T-U1 搜索引导：placeholder 白话 + 无结果时有出路提示", async () => {
    window.location.hash = "#/rules";
    render(<App />);
    const input = within(screen.getByRole("banner")).getByRole(
      "combobox"
    ) as HTMLInputElement;
    // antd v6 占位符渲染为独立节点 .ant-select-placeholder（不在 input 属性上）
    const phText = document.querySelector(".ant-select-placeholder")?.textContent;
    expect(phText).toBe("搜数字、规则或表名");
    fireEvent.mouseDown(input);
    fireEvent.change(input, { target: { value: "绝对不存在的关键词xyzq" } });
    expect(await screen.findByText(/没找到？换个词试试/)).toBeTruthy();
  });
});
