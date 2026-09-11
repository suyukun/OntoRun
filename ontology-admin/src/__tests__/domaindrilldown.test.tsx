// T404 域内图判据测试（fetch 全 mock，构造 T401 lineage payload，不触真实后端）：
// - 层分列：本域登记表按 lineage layer 现有四值分列（ODS/CDM/DIM/ADS），列头带该层表数
// - 相关指标折叠区（裁决 7 延伸）：ADS(domain=null) 直接上游落本域 → 相关，
//   默认收起标「N 张指标表」，一跳不递归口径锁定
// - 跨域摘要行：domain_edges 过滤本域，三色边样式 + ×N，无关域边不出现
// - 表节点点击 → 既有表详情路由 #/object/table/{id}（T301）
// - qc6_node_cap：域内 >30 截断提示（复用 T403 capNodes/NODE_CAP），列头计数不失真
// - 面包屑：全域图 / 当前域名（最小两级），点全域图回域图；跨域点击优先回调
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import DomainDrilldown from "../components/DomainDrilldown";
import { NODE_CAP } from "../components/DomainGraph";

// 夹具拟真实盘 id 形状（ods.ods_* / cdm.dwd_* / cdm.dim_* / rec.ads_*）：
// cu=用户域 5 张登记表（ODS1/CDM3/DIM1）；ADS 均不登记（裁决 4，domain=null）。
const payload = {
  nodes: [
    { id: "ods.ods_usms_lm_user_t_df", label: "ods.ods_usms_lm_user_t_df", layer: "ODS", domain: "cu", unconfirmed: true },
    { id: "cdm.dwd_cu_rgst_fin_di", label: "cdm.dwd_cu_rgst_fin_di", layer: "CDM", domain: "cu", unconfirmed: false },
    { id: "cdm.dwd_cu_rgst_nonfin_di", label: "cdm.dwd_cu_rgst_nonfin_di", layer: "CDM", domain: "cu", unconfirmed: false },
    { id: "cdm.dwd_cu_actv_df", label: "cdm.dwd_cu_actv_df", layer: "CDM", domain: "cu", unconfirmed: false },
    { id: "cdm.dim_cu_usr_info_df", label: "cdm.dim_cu_usr_info_df", layer: "DIM", domain: "cu", unconfirmed: false },
    // ADS 指标表（裁决 4 不登记）：前两张直接上游落 cu → 相关
    { id: "rec.ads_rgst_chnl_cnt_df", label: "rec.ads_rgst_chnl_cnt_df", layer: "ADS", domain: null, unconfirmed: false },
    { id: "rec.ads_rgst_act_chnl_cnt_df", label: "rec.ads_rgst_act_chnl_cnt_df", layer: "ADS", domain: null, unconfirmed: false },
    // 反例 1：直接上游在 ch 域 → 不相关
    { id: "rec.ads_other_df", label: "rec.ads_other_df", layer: "ADS", domain: null, unconfirmed: false },
    // 反例 2：直接上游是 ADS 中间表（一跳口径，爷爷辈在 cu 也不算）
    { id: "rec.ads_chain_df", label: "rec.ads_chain_df", layer: "ADS", domain: null, unconfirmed: false },
    // 他域登记表：不入本域列
    { id: "cdm.dwd_ch_usr_rltv_df", label: "cdm.dwd_ch_usr_rltv_df", layer: "CDM", domain: "ch", unconfirmed: false },
    { id: "ods.ods_usms_lml_account_t_df", label: "ods.ods_usms_lml_account_t_df", layer: "ODS", domain: "ac", unconfirmed: false },
  ],
  edges: [
    { source: "ods.ods_usms_lm_user_t_df", target: "cdm.dwd_cu_rgst_fin_di" },
    { source: "cdm.dwd_cu_rgst_fin_di", target: "rec.ads_rgst_chnl_cnt_df" },
    { source: "cdm.dwd_cu_actv_df", target: "rec.ads_rgst_act_chnl_cnt_df" },
    { source: "cdm.dwd_ch_usr_rltv_df", target: "rec.ads_other_df" },
    { source: "rec.ads_rgst_chnl_cnt_df", target: "rec.ads_chain_df" },
    { source: "ods.ods_usms_lml_account_t_df", target: "cdm.dwd_cu_actv_df" },
  ],
  domains: [
    { key: "cu", name: "用户域", table_count: 5, replicas: 5, pending: 1, divergent: 0, ads_metric_count: 2 },
    { key: "ch", name: "渠道域", table_count: 1, replicas: 1, pending: 0, divergent: 0, ads_metric_count: 0 },
    { key: "pb", name: "公共域", table_count: 0, replicas: 0, pending: 0, divergent: 0, ads_metric_count: 0 },
    { key: "lm", name: "日志域", table_count: 0, replicas: 0, pending: 0, divergent: 0, ads_metric_count: 0 },
    { key: "ac", name: "账务域", table_count: 1, replicas: 1, pending: 0, divergent: 0, ads_metric_count: 0 },
  ],
  // 与表级血缘自洽的聚合边：cu→ch ×2 / pb→cu ×3 / ac→cu ×1，lm→ac 与 cu 无关
  domain_edges: [
    { source: "cu", target: "ch", weight: 2, severity: "pending" },
    { source: "pb", target: "cu", weight: 3, severity: "settled" },
    { source: "ac", target: "cu", weight: 1, severity: "divergent" },
    { source: "lm", target: "ac", weight: 1, severity: "divergent" },
  ],
  layers: {
    ODS: { color: "#1677ff", label: "ODS 贴源" },
    CDM: { color: "#52c41a", label: "CDM 明细/维表" },
    ADS: { color: "#fa8c16", label: "ADS 应用" },
    DIM: { color: "#722ed1", label: "DIM 外部维表" },
  },
};

function stubLineageFetch(data: unknown) {
  // 非 /api/lineage 一律 404：组件打错端点会在用例里显式暴露
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL) => {
      if (String(input) !== "/api/lineage") {
        return new Response("{}", { status: 404 });
      }
      return new Response(JSON.stringify(data), { status: 200 });
    })
  );
}

async function renderDrilldown(data: unknown = payload, domainKey = "cu") {
  stubLineageFetch(data);
  const { container } = render(<DomainDrilldown domainKey={domainKey} />);
  // 首个用例吃 React 渲染预热，findBy 默认 1s 超时会偶发抢跑（同 T403 惯例）
  await screen.findByTestId("drilldown-canvas", {}, { timeout: 5000 });
  return container;
}

afterEach(() => {
  cleanup(); // vitest globals 关闭，显式卸载防 DOM 跨用例累积
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
  window.location.hash = "";
});

describe("DomainDrilldown (T404)", () => {
  it("层分列：登记表按 lineage layer 四值分列，列头带该层表数；他域表/未登记 ADS 不入列", async () => {
    await renderDrilldown();
    expect(screen.getByTestId("layer-col-ODS")).toBeTruthy();
    expect(screen.getByTestId("layer-col-CDM")).toBeTruthy();
    expect(screen.getByTestId("layer-col-DIM")).toBeTruthy();
    // 该域无登记 ADS（裁决 4）→ ADS 列不渲染
    expect(screen.queryByTestId("layer-col-ADS")).toBeNull();
    // 列头：人话名 + 截断前口径表数
    const ods = screen.getByTestId("layer-col-ODS");
    expect(within(ods).getByText("ODS 贴源")).toBeTruthy();
    expect(within(ods).getByText("（1）")).toBeTruthy();
    const cdm = screen.getByTestId("layer-col-CDM");
    expect(within(cdm).getByText("CDM 明细/维表")).toBeTruthy();
    expect(within(cdm).getByText("（3）")).toBeTruthy();
    expect(within(screen.getByTestId("layer-col-DIM")).getByText("（1）")).toBeTruthy();
    // 本域表落在对应列
    expect(within(ods).getByTestId("table-node-ods.ods_usms_lm_user_t_df")).toBeTruthy();
    expect(within(cdm).getByTestId("table-node-cdm.dwd_cu_rgst_fin_di")).toBeTruthy();
    expect(within(screen.getByTestId("layer-col-DIM")).getByTestId("table-node-cdm.dim_cu_usr_info_df")).toBeTruthy();
    // 他域登记表 / 未登记 ADS 表不入画布
    expect(screen.queryByTestId("table-node-cdm.dwd_ch_usr_rltv_df")).toBeNull();
    expect(screen.queryByTestId("table-node-rec.ads_rgst_chnl_cnt_df")).toBeNull();
  });

  it("相关指标折叠区：默认收起标「2 张指标表」，展开列清单；一跳不递归口径", async () => {
    await renderDrilldown();
    const block = screen.getByTestId("related-metrics");
    expect(within(block).getByText("相关指标表 2 张")).toBeTruthy();
    // 默认收起：清单不渲染
    expect(screen.queryByText("rec.ads_rgst_chnl_cnt_df")).toBeNull();
    fireEvent.click(within(block).getByText("相关指标表 2 张"));
    expect(await screen.findByText("rec.ads_rgst_chnl_cnt_df")).toBeTruthy();
    expect(screen.getByText("rec.ads_rgst_act_chnl_cnt_df")).toBeTruthy();
    // 上游在 ch 域的 ADS、ADS→ADS 中间链表不入清单（推导口径 = 一跳直连本域）
    expect(screen.queryByText("rec.ads_other_df")).toBeNull();
    expect(screen.queryByText("rec.ads_chain_df")).toBeNull();
  });

  it("跨域摘要行：domain_edges 过滤本域，三色边样式 + ×N；无关域边不出现", async () => {
    await renderDrilldown();
    const row = screen.getByTestId("cross-domain-summary");
    expect(within(row).getByTestId("cross-edge-ch")).toBeTruthy();
    expect(within(row).getByTestId("cross-edge-pb")).toBeTruthy();
    expect(within(row).getByTestId("cross-edge-ac")).toBeTruthy();
    expect(within(row).queryByTestId("cross-edge-lm")).toBeNull(); // 与本域无关
    expect(within(row).getByText("渠道域")).toBeTruthy();
    expect(within(row).getByText("公共域")).toBeTruthy();
    expect(within(row).getByText("账务域")).toBeTruthy();
    expect(within(row).getByText("×2")).toBeTruthy();
    expect(within(row).getByText("×3")).toBeTruthy();
    expect(within(row).getByText("×1")).toBeTruthy();
    // 三色：settled 灰实线 / pending 橙虚线 / divergent 红虚线（复用 T403 EDGE_STYLES）
    const settled = row.querySelector('line[data-severity="settled"]');
    const pending = row.querySelector('line[data-severity="pending"]');
    const divergent = row.querySelector('line[data-severity="divergent"]');
    expect(settled).toBeTruthy();
    expect(pending).toBeTruthy();
    expect(divergent).toBeTruthy();
    expect(settled!.getAttribute("stroke")).toBe("#bfbfbf");
    expect(settled!.getAttribute("stroke-dasharray")).toBeNull();
    expect(pending!.getAttribute("stroke")).toBe("#fa8c16");
    expect(pending!.getAttribute("stroke-dasharray")).toBeTruthy();
    expect(divergent!.getAttribute("stroke")).toBe("#ff4d4f");
    expect(divergent!.getAttribute("stroke-dasharray")).toBeTruthy();
  });

  it("表节点点击 → 既有表详情路由 #/object/table/{id}（T301）", async () => {
    await renderDrilldown();
    fireEvent.click(screen.getByTestId("table-node-cdm.dwd_cu_rgst_fin_di"));
    expect(window.location.hash).toBe("#/object/table/cdm.dwd_cu_rgst_fin_di");
    fireEvent.click(screen.getByTestId("table-node-ods.ods_usms_lm_user_t_df"));
    expect(window.location.hash).toBe("#/object/table/ods.ods_usms_lm_user_t_df");
  });

  it("qc6_node_cap：域内 35 张截断为 30 并提示，列头计数仍为截断前口径", async () => {
    const many = {
      nodes: [
        ...Array.from({ length: 15 }, (_, i) => ({
          id: "ods.ods_big_" + String(i).padStart(2, "0"),
          label: "ods.ods_big_" + String(i).padStart(2, "0"),
          layer: "ODS",
          domain: "big",
          unconfirmed: false,
        })),
        ...Array.from({ length: 20 }, (_, i) => ({
          id: "cdm.dwd_big_" + String(i).padStart(2, "0"),
          label: "cdm.dwd_big_" + String(i).padStart(2, "0"),
          layer: "CDM",
          domain: "big",
          unconfirmed: false,
        })),
      ],
      edges: [],
      domains: [
        { key: "big", name: "压测域", table_count: 35, replicas: 35, pending: 0, divergent: 0, ads_metric_count: 0 },
      ],
      domain_edges: [],
      layers: payload.layers,
    };
    await renderDrilldown(many, "big");
    expect(screen.getByTestId("drilldown-truncated")).toBeTruthy();
    expect(screen.getByText("已截断：显示 " + NODE_CAP + "/35 张（节点上限 " + NODE_CAP + "）")).toBeTruthy();
    // 层序+表名字典序取前 30：ODS 15 张全保留，CDM 保留前 15
    expect(within(screen.getByTestId("layer-col-ODS")).getAllByTestId(/^table-node-/)).toHaveLength(15);
    const cdm = screen.getByTestId("layer-col-CDM");
    expect(within(cdm).getAllByTestId(/^table-node-/)).toHaveLength(15);
    expect(screen.queryByTestId("table-node-cdm.dwd_big_15")).toBeNull();
    // 列头计数 = 截断前真实口径（20），不失真
    expect(within(cdm).getByText("（20）")).toBeTruthy();
  });

  it("面包屑：全域图 / 当前域名 最小两级；点全域图回域图（缺省 hash 路由）", async () => {
    await renderDrilldown();
    const bc = screen.getByTestId("drilldown-breadcrumb");
    expect(within(bc).getByText("全域图")).toBeTruthy();
    expect(within(bc).getByText("用户域")).toBeTruthy();
    fireEvent.click(within(bc).getByText("全域图"));
    expect(window.location.hash).toBe("#/graph");
  });

  it("跨域摘要点其他域：优先触发 onOpenDomain 回调（缺省才回退 #/graph），T503 可预选", async () => {
    const onOpenDomain = vi.fn();
    stubLineageFetch(payload);
    render(<DomainDrilldown domainKey="cu" onOpenDomain={onOpenDomain} />);
    await screen.findByTestId("drilldown-canvas", {}, { timeout: 5000 });
    fireEvent.click(screen.getByTestId("cross-edge-ch"));
    expect(onOpenDomain).toHaveBeenCalledWith("ch");
    expect(window.location.hash).not.toBe("#/graph");
  });

  it("空态出路：域无登记表（或域不在 payload）→ Empty 而非空白", async () => {
    stubLineageFetch(payload);
    render(<DomainDrilldown domainKey="or" />);
    expect(
      await screen.findByText(/该域暂无登记表/, {}, { timeout: 5000 })
    ).toBeTruthy();
    expect(screen.queryByTestId("drilldown-canvas")).toBeNull();
  });
});
