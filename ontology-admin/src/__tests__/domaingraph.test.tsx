// T403 域图组件判据测试（fetch 全 mock，构造 T401 lineage payload，不触真实后端）：
// - 裁决2 只渲染有表域：payload 含金控 10 域全集，5 有表域渲染、5 空域不渲染
// - 节点徽章编码：pending>0 红徽章数字 / divergent>0 ⚡ / ads_metric_count>0 「N 张指标」
// - edge_aggregation_severity：settled 灰实线 / pending 橙虚线 / divergent 红虚线 + ×N 角标
// - 图例行最小版：三色边例 + 全站待确认/分歧计数（T503 收口顶部常驻版式）
// - Drawer 开合 + 登记来源行（王工走查修订 2）+ 表数逻辑口径/物理副本附注
// - qc6_node_cap：节点 >30 截断提示（防御性，域层 ≤10 用不到；T404 复用 capNodes）
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import DomainGraph, {
  capNodes,
  NODE_CAP,
  type DomainInfo,
  type DomainLineagePayload,
} from "../components/DomainGraph";

// 夹具对齐改判后实盘：5 有表域 CU11/CH3/PB5物理·3逻辑/LM2/AC1（§附域框架改判
// 记录），pb 的 dim_pb_date_yf 三副本 -> 5 物理/3 逻辑；description 为 registry
// Domain 契约字段（lineage payload 暂未透出，组件按可选渲染）。
const payload: DomainLineagePayload = {
  domains: [
    {
      key: "cu",
      name: "用户域",
      description:
        "用户信息，以及与用户相关联的各类实体对象，例如设备信息、卡信息等（Customer Domain）",
      table_count: 11,
      replicas: 11,
      pending: 2,
      divergent: 0,
      ads_metric_count: 4,
    },
    {
      key: "ch",
      name: "渠道域",
      description: "渠道主数据与层级（Channel Domain）",
      table_count: 3,
      replicas: 3,
      pending: 0,
      divergent: 1,
      ads_metric_count: 2,
    },
    {
      key: "pb",
      name: "公共域",
      description: "共用信息及暂时无法分类的数据（Public Domain）",
      table_count: 3,
      replicas: 5,
      pending: 0,
      divergent: 0,
      ads_metric_count: 8,
    },
    {
      key: "lm",
      name: "日志域",
      description: "埋点与行为日志（Log Domain）",
      table_count: 2,
      replicas: 2,
      pending: 0,
      divergent: 0,
      ads_metric_count: 0,
    },
    {
      key: "ac",
      name: "账务域",
      description: "记录各类金融账户（Accounting Domain）",
      table_count: 1,
      replicas: 1,
      pending: 1,
      divergent: 0,
      ads_metric_count: 0,
    },
    // 5 个 0 表域（裁决 2 隐藏）：bs 全 ADS、or/rc/ps/tr 未登记
    { key: "bs", name: "经营域", table_count: 0, replicas: 0, pending: 0, divergent: 0, ads_metric_count: 0 },
    { key: "or", name: "运营域", table_count: 0, replicas: 0, pending: 0, divergent: 0, ads_metric_count: 0 },
    { key: "rc", name: "风控域", table_count: 0, replicas: 0, pending: 0, divergent: 0, ads_metric_count: 0 },
    { key: "ps", name: "产品域", table_count: 0, replicas: 0, pending: 0, divergent: 0, ads_metric_count: 0 },
    { key: "tr", name: "交易域", table_count: 0, replicas: 0, pending: 0, divergent: 0, ads_metric_count: 0 },
  ],
  domain_edges: [
    { source: "pb", target: "cu", weight: 3, severity: "settled" },
    { source: "cu", target: "ch", weight: 2, severity: "pending" },
    { source: "lm", target: "ac", weight: 1, severity: "divergent" },
  ],
};

function stubLineageFetch(data: unknown) {
  // 非 /api/lineage 一律 404：组件打错端点会在用例里显式暴露
  const fn = vi.fn(async (input: RequestInfo | URL) => {
    if (String(input) !== "/api/lineage") {
      return new Response("{}", { status: 404 });
    }
    return new Response(JSON.stringify(data), { status: 200 });
  });
  vi.stubGlobal("fetch", fn);
  return fn;
}

async function renderWithPayload(data: unknown = payload, waitKey = "cu") {
  const fetchFn = stubLineageFetch(data);
  const { container } = render(<DomainGraph />);
  // 首个用例吃 React 渲染预热（~1.3s），findBy 默认 1s 超时会偶发抢跑
  await screen.findByTestId(`domain-node-${waitKey}`, {}, { timeout: 5000 });
  return { fetchFn, container };
}

afterEach(() => {
  cleanup(); // vitest globals 关闭，显式卸载防 DOM 跨用例累积
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("DomainGraph (T403)", () => {
  it("裁决2 有表域才渲染：10 域 payload 只出 5 个节点，空域不渲染；fetch /api/lineage", async () => {
    const { fetchFn } = await renderWithPayload();
    expect(fetchFn.mock.calls[0][0]).toBe("/api/lineage");
    for (const key of ["cu", "ch", "pb", "lm", "ac"]) {
      expect(screen.getByTestId(`domain-node-${key}`)).toBeTruthy();
    }
    for (const key of ["bs", "or", "rc", "ps", "tr"]) {
      expect(screen.queryByTestId(`domain-node-${key}`)).toBeNull();
    }
  });

  it("节点徽章编码：pending 红徽章数字 / divergent ⚡ / ADS 「N 张指标」；0 值不渲染", async () => {
    await renderWithPayload();
    const cu = screen.getByTestId("domain-node-cu");
    expect(within(cu).getByLabelText("待确认 2 条")).toBeTruthy();
    expect(within(cu).getByText("4 张指标")).toBeTruthy();
    expect(within(cu).queryByText("⚡")).toBeNull();

    const ch = screen.getByTestId("domain-node-ch");
    expect(within(ch).getByText("⚡")).toBeTruthy();
    expect(within(ch).queryByLabelText(/待确认/)).toBeNull();

    const pb = screen.getByTestId("domain-node-pb");
    expect(within(pb).getByText("8 张指标")).toBeTruthy();

    // lm / ac：无 ⚡ 无指标徽标
    for (const key of ["lm", "ac"]) {
      const node = screen.getByTestId(`domain-node-${key}`);
      expect(within(node).queryByText("⚡")).toBeNull();
      expect(within(node).queryByText(/张指标/)).toBeNull();
    }
  });

  it("三色边样式：settled 灰实线 / pending 橙虚线 / divergent 红虚线 + ×N 角标", async () => {
    const { container } = await renderWithPayload();

    const settled = container.querySelector('line[data-severity="settled"]');
    const pending = container.querySelector('line[data-severity="pending"]');
    const divergent = container.querySelector(
      'line[data-severity="divergent"]'
    );
    expect(settled).toBeTruthy();
    expect(pending).toBeTruthy();
    expect(divergent).toBeTruthy();
    expect(settled!.getAttribute("stroke")).toBe("#bfbfbf");
    expect(settled!.getAttribute("stroke-dasharray")).toBeNull(); // 实线
    expect(pending!.getAttribute("stroke")).toBe("#fa8c16");
    expect(pending!.getAttribute("stroke-dasharray")).toBeTruthy(); // 虚线
    expect(divergent!.getAttribute("stroke")).toBe("#ff4d4f");
    expect(divergent!.getAttribute("stroke-dasharray")).toBeTruthy(); // 虚线

    // ×N 角标（聚合边中点）：3 条边 weight 3/2/1
    expect(screen.getByText("×3")).toBeTruthy();
    expect(screen.getByText("×2")).toBeTruthy();
    expect(screen.getByText("×1")).toBeTruthy();
    expect(screen.getByTestId("edge-weight-pb-cu")).toBeTruthy();
  });

  it("图例行最小版：三色边例 + 全站待确认/分歧计数（同源 payload 汇总）", async () => {
    const { container } = await renderWithPayload();
    const legend = screen.getByTestId("domain-graph-legend");
    expect(
      within(legend).getByText(/全站待确认 3 · 分歧 1/)
    ).toBeTruthy(); // 2(cu) + 1(ac)；分歧 1(ch)
    expect(container.querySelector('line[data-testid="legend-edge-settled"]')).toBeTruthy();
    const legendPending = container.querySelector(
      'line[data-testid="legend-edge-pending"]'
    );
    expect(legendPending!.getAttribute("stroke")).toBe("#fa8c16");
    expect(legendPending!.getAttribute("stroke-dasharray")).toBeTruthy();
    const legendDivergent = container.querySelector(
      'line[data-testid="legend-edge-divergent"]'
    );
    expect(legendDivergent!.getAttribute("stroke")).toBe("#ff4d4f");
    expect(legendDivergent!.getAttribute("stroke-dasharray")).toBeTruthy();
  });

  it("Drawer 开合：点域节点开详情（人话名/简介/表数逻辑口径+物理附注/待确认/分歧/ADS 指标），关得回去", async () => {
    await renderWithPayload();
    // 开：Drawer 是 portal，描述/表数附注仅存在于 Drawer 内
    fireEvent.click(screen.getByTestId("domain-node-cu"));
    expect(
      await screen.findByText(/用户信息，以及与用户相关联的各类实体对象/)
    ).toBeTruthy();
    expect(
      screen.getByText("11 张（逻辑口径；物理登记 11 张）")
    ).toBeTruthy();
    expect(screen.getByText(/待确认：/)).toBeTruthy();
    expect(screen.getByText(/分歧：/)).toBeTruthy();
    expect(screen.getByText(/ADS 指标：/)).toBeTruthy();
    // 登记来源行（王工走查修订 2）：谁/哪个版本划入——见变更历史
    expect(
      screen.getByText(
        "域与表的登记：git 管理，谁在哪个版本划入——见变更历史"
      )
    ).toBeTruthy();
    // 关：jsdom 不触发 antd 退场动画完成事件，dialog 可能滞留为 aria-hidden
    fireEvent.click(screen.getByRole("button", { name: /close/i }));
    await waitFor(() => {
      const dialog = screen.queryByRole("dialog");
      expect(
        dialog === null || dialog.getAttribute("aria-hidden") === "true"
      ).toBe(true);
    });
  });

  it("qc6_node_cap：节点 >30 截断为 30 并提示（共 35 个）", async () => {
    const many: DomainLineagePayload = {
      domains: Array.from({ length: 35 }, (_, i) => ({
        key: `k${i}`,
        name: `压测域 ${i}`,
        table_count: 1,
        replicas: 1,
        pending: 0,
        divergent: 0,
        ads_metric_count: 0,
      })) satisfies DomainInfo[],
      domain_edges: [],
    };
    await renderWithPayload(many, "k0");
    expect(screen.getByTestId("domain-node-k0")).toBeTruthy();
    expect(screen.getByTestId("domain-node-k29")).toBeTruthy();
    expect(screen.queryByTestId("domain-node-k30")).toBeNull();
    expect(screen.getByText(/已截断显示前 30 个（共 35 个）/)).toBeTruthy();
  });

  it("capNodes 纯函数（T404 复用）：≤cap 不截断，>cap 截断", () => {
    const items = Array.from({ length: 35 }, (_, i) => i);
    expect(capNodes(items)).toEqual({
      kept: items.slice(0, NODE_CAP),
      total: 35,
      truncated: true,
    });
    expect(capNodes(items, 10).kept).toHaveLength(10);
    expect(capNodes([1, 2, 3])).toEqual({
      kept: [1, 2, 3],
      total: 3,
      truncated: false,
    });
  });
});
