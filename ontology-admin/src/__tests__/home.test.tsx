// T503 首页版式收口判据测试（fetch 全 mock，App 级渲染，不触真实后端）：
// - qc1_first_screen_blocks：首屏 1080p 信息区块 ≤3（横条+画布+图例行）；
//   0 待办不渲染横条（区块=2），有待确认出横条（区块=3）
// - qc11_terminology_consistency：「钉死」口号仅出现在待办横条一处
// - drilldown_breadcrumb 端到端：点域 → 域内图 → 点表 → 表详情；面包屑「全域图」可回域图
// 数据契约 = T401 lineage payload（DomainGraph 消费 domains/domain_edges，
// DomainDrilldown 消费 nodes/edges/layers，夹具为两者并集形状）。
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "../App";

function ontologyFixture(pending: number) {
  return {
    measures: [],
    dimensions: [],
    rules: [],
    summary: {
      measures: 0,
      dimensions: 0,
      rules: 3,
      pending,
      confirmed: 3 - pending,
    },
  };
}

function lineageFixture(cuPending: number) {
  return {
    domains: [
      {
        key: "cu",
        name: "用户域",
        table_count: 2,
        replicas: 2,
        pending: cuPending,
        divergent: 0,
        ads_metric_count: 1,
      },
      {
        key: "ch",
        name: "渠道域",
        table_count: 1,
        replicas: 1,
        pending: 0,
        divergent: 0,
        ads_metric_count: 0,
      },
    ],
    domain_edges: [{ source: "cu", target: "ch", weight: 2, severity: "pending" }],
    nodes: [
      {
        id: "dwd_cu_rgst_fin_di",
        label: "dwd_cu_rgst_fin_di",
        layer: "CDM",
        domain: "cu",
        unconfirmed: cuPending > 0,
      },
      {
        id: "dwd_cu_auth_fin_di",
        label: "dwd_cu_auth_fin_di",
        layer: "CDM",
        domain: "cu",
        unconfirmed: false,
      },
      {
        id: "ads_chnl_auth_qty_df",
        label: "ads_chnl_auth_qty_df",
        layer: "ADS",
        domain: "ch",
        unconfirmed: false,
      },
    ],
    edges: [
      { source: "dwd_cu_rgst_fin_di", target: "ads_chnl_auth_qty_df" },
      { source: "dwd_cu_auth_fin_di", target: "ads_chnl_auth_qty_df" },
    ],
    layers: {
      CDM: { color: "#2f54eb", label: "CDM 明细/维表" },
      ADS: { color: "#fa8c16", label: "ADS 应用" },
    },
    stats: { nodes: 3, edges: 2, unconfirmed_edges: cuPending > 0 ? 1 : 0 },
  };
}

const tableDetailFixture = {
  kind: "table",
  id: "dwd_cu_auth_fin_di",
  description: "授权明细（夹具）",
  layer: "CDM",
  unconfirmed: false,
  definition: {},
  rules: [],
  upstream: [],
  downstream: [],
};

function stubHomeFetch(pending: number) {
  const fn = vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url.startsWith("/api/ontology")) {
      return new Response(JSON.stringify(ontologyFixture(pending)), { status: 200 });
    }
    if (url.startsWith("/api/lineage")) {
      return new Response(JSON.stringify(lineageFixture(pending)), { status: 200 });
    }
    if (url.startsWith("/api/objects/table/dwd_cu_auth_fin_di")) {
      return new Response(JSON.stringify(tableDetailFixture), { status: 200 });
    }
    return new Response("{}", { status: 404 });
  });
  vi.stubGlobal("fetch", fn);
  return fn;
}

// antd 部件在 jsdom 需要的宿主能力（同 search.test 惯例）
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

// qc1 信息区块口径：横条 + 域图画布 + 图例/健康度行（Layout 容器不算信息区块）
function countHomeBlocks(): number {
  return ["home-todo-bar", "domain-graph-canvas", "domain-graph-legend"].filter(
    (id) => screen.queryByTestId(id) !== null
  ).length;
}

async function renderHome(pending: number) {
  window.location.hash = "#/graph";
  stubHomeFetch(pending);
  render(<App />);
  // 首用例吃 React/antd 渲染预热，显式放宽 findBy 轮询窗
  await screen.findByTestId("domain-graph-canvas", {}, { timeout: 8000 });
}

beforeEach(() => {
  vi.stubGlobal("ResizeObserver", ResizeObserverStub);
  vi.stubGlobal("matchMedia", matchMediaStub);
});

afterEach(() => {
  cleanup(); // vitest globals 关闭，显式卸载防 DOM 跨用例累积
  vi.unstubAllGlobals();
  window.location.hash = "";
});

describe("GraphHome T503 首页版式收口", () => {
  it("qc1_first_screen_blocks：0 待办无横条，信息区块=画布+图例行=2 ≤3", async () => {
    await renderHome(0);
    expect(screen.queryByTestId("home-todo-bar")).toBeNull();
    expect(screen.getByTestId("domain-graph-legend")).toBeTruthy();
    expect(countHomeBlocks()).toBe(2);
    expect(countHomeBlocks()).toBeLessThanOrEqual(3);
  });

  it("qc1 + qc11：有待确认出横条（区块=3 ≤3），「钉死」仅横条一处；去确认链到 #/rules", async () => {
    await renderHome(1);
    const bar = screen.getByTestId("home-todo-bar");
    // <b>N</b> 拆行：计数与文案分别在 <b> 和其兄弟文本节点，分开断言
    expect(within(bar).getByText("1")).toBeTruthy();
    expect(within(bar).getByText(/条口径待确认.*数不准/)).toBeTruthy();
    // qc11：「钉死」口号仅限横条——全页恰好一处
    const nailCount = (document.body.textContent ?? "").split("钉死").length - 1;
    expect(nailCount).toBe(1);
    // 区块=横条+画布+图例行=3，首屏不超
    expect(countHomeBlocks()).toBe(3);
    expect(countHomeBlocks()).toBeLessThanOrEqual(3);
    fireEvent.click(within(bar).getByRole("button", { name: /去确认/ }));
    await waitFor(() => expect(window.location.hash).toBe("#/rules"));
  });

  it("drilldown 端到端：点域 → 域内图（面包屑+层分列）→ 点表 → 表详情路由", async () => {
    await renderHome(1);
    fireEvent.click(screen.getByTestId("domain-node-cu"));
    await waitFor(() => expect(window.location.hash).toBe("#/graph/cu"));
    // 域内图：面包屑两级（全域图可回 + 当前域）+ 层分列 + 域内表节点
    const crumb = await screen.findByTestId("drilldown-breadcrumb", {}, { timeout: 8000 });
    expect(within(crumb).getByText("全域图")).toBeTruthy();
    expect(within(crumb).getByText("用户域")).toBeTruthy();
    await screen.findByTestId("layer-col-CDM", {}, { timeout: 8000 });
    expect(screen.getByTestId("table-node-dwd_cu_auth_fin_di")).toBeTruthy();
    // 第三级：点表 → 表详情路由 + 详情页真身渲染
    fireEvent.click(screen.getByTestId("table-node-dwd_cu_auth_fin_di"));
    await waitFor(() =>
      expect(window.location.hash).toBe("#/object/table/dwd_cu_auth_fin_di")
    );
    expect(await screen.findByText("表档案", {}, { timeout: 8000 })).toBeTruthy();
  });

  it("drilldown_breadcrumb 逐级可达（回程）：域内图点「全域图」回域图", async () => {
    await renderHome(0);
    fireEvent.click(screen.getByTestId("domain-node-cu"));
    await waitFor(() => expect(window.location.hash).toBe("#/graph/cu"));
    const crumb = await screen.findByTestId("drilldown-breadcrumb", {}, { timeout: 8000 });
    fireEvent.click(within(crumb).getByText("全域图"));
    await waitFor(() => expect(window.location.hash).toBe("#/graph"));
    // 回程逐级可达：域图画布重新在位
    await screen.findByTestId("domain-graph-canvas", {}, { timeout: 8000 });
  });
});
