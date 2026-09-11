// T501 数字目录判据测试（fetch 全 mock，不触真实后端）：
// catalog_plain_names（卡片首行人话名，禁裸 ID/表名前缀打头）/ 可信度徽章（qc11：已确认绿、待确认橙）/
// 试算成功「2026-08 = 607 户」句式 + 失败灰条「试算暂不可用」/ 维度折叠默认收起（Tabs 退役）。
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeAll, describe, expect, it, vi } from "vitest";

import type { Measure, Ontology } from "../api";
import ObjectsPage from "../pages/ObjectsPage";

// 夹具对齐 registry.py 真实度量（id/描述/表达式/表），状态摘要为演示态示例值
const measureConfirmed: Measure = {
  id: "reg_user_cnt",
  description: "注册用户数：注册 KPI 明细去重用户数",
  expression: "COUNT(DISTINCT {src}.usr_id)",
  source_table: "cdm.dwd_cu_rgst_fin_di",
  source_alias: "dwd",
  time_field: "rgst_dt",
  filters: [],
  domain: "cu",
  domain_name: "用户域",
  caliber: {
    rule_id: "R1",
    status: "confirmed",
    code: "5835da",
    confirmer: "王工",
    time: "2026-09-10T17:13:06+08:00",
    commit: "4e77cc4",
    verdict: "confirmed",
  },
};

const measurePending: Measure = {
  id: "auth_user_cnt",
  description: "授权用户数：窗口内完成授权的去重用户数",
  expression: "COUNT(DISTINCT {src}.usr_id)",
  source_table: "cdm.dwd_ch_usr_rltv_df",
  source_alias: "rv",
  time_field: "grant_dt",
  filters: [],
  domain: null,
  domain_name: null,
  caliber: {
    rule_id: "R7",
    status: "unverified",
    code: "272c67",
    confirmer: "苏",
    time: "2026-09-11T16:04:30+08:00",
    commit: "16b85b4",
    verdict: "rejected",
  },
};

const ontologyFixture: Ontology = {
  measures: [measureConfirmed, measurePending],
  dimensions: [
    {
      id: "channel_l1",
      description: "一级渠道：JOIN 渠道维 fst_chnl_nm",
      expression: "{j}.fst_chnl_nm",
      join: null,
      grains: null,
    },
  ],
  rules: [],
  summary: { measures: 2, dimensions: 1, rules: 0, pending: 1, confirmed: 1 },
};

function stubFetch(ok: boolean) {
  const fn = vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (!url.includes("/api/trial/")) {
      return new Response("{}", { status: 404 });
    }
    return ok
      ? new Response(
          JSON.stringify({
            rule_id: "R1",
            month: "2026-08",
            value: 607,
            unit: "户",
            generated_at: "2026-09-11T10:00:00",
            source: "semantic_query",
          }),
          { status: 200 },
        )
      : new Response(JSON.stringify({ detail: "trial_unavailable" }), {
          status: 503,
        });
  });
  vi.stubGlobal("fetch", fn);
  return fn;
}

afterEach(() => {
  cleanup(); // vitest globals 关闭，RTL 自动清理不生效，显式卸载防 DOM 跨用例累积
  vi.unstubAllGlobals();
});

// 维度速查的 antd Table 挂载时注册响应式断点，jsdom 无 matchMedia，补最小桩（仅本文件）。
beforeAll(() => {
  window.matchMedia = ((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  })) as unknown as typeof window.matchMedia;
});

function renderPage() {
  return render(<ObjectsPage ontology={ontologyFixture} />);
}

describe("ObjectsPage 数字目录 (T501)", () => {
  it("catalog_plain_names: 卡片首行是人话名，不以裸 ID/表名前缀打头", () => {
    stubFetch(false);
    const { container } = renderPage();
    expect(screen.getByText("注册用户数")).toBeTruthy();
    expect(screen.getByText("授权用户数")).toBeTruthy();
    for (const el of container.querySelectorAll(".ant-card-head-title")) {
      const t = el.textContent ?? "";
      expect(t).toContain("用户数"); // 首行人话名在卡头
      expect(t).not.toContain("reg_user_cnt");
      expect(t).not.toContain("auth_user_cnt");
      expect(t).not.toContain("cdm.");
    }
    // 度量 ID 只作卡右上角技术元信息（专业对数路径保留）
    expect(screen.getByText("reg_user_cnt")).toBeTruthy();
  });

  it("qc11 可信度徽章: 已确认绿 / 待确认橙", () => {
    stubFetch(false);
    renderPage();
    const green = screen.getByText("已确认").closest(".ant-tag");
    const orange = screen.getByText("待确认").closest(".ant-tag");
    expect(green?.className).toContain("green");
    expect(orange?.className).toContain("orange");
  });

  it("版本行: 已确认给存档编号+确认人；待确认注明最近记录（驳回不冒充确认）", () => {
    stubFetch(false);
    renderPage();
    expect(screen.getByText(/已确认 · 存档编号 4e77cc4 · 王工/)).toBeTruthy();
    expect(
      screen.getByText(/待确认 · 最近记录：苏 2026-09-11 16:04（驳回）/),
    ).toBeTruthy();
  });

  it("试算成功: 点「试一下」显示「2026-08 = 607 户」句式", async () => {
    const fn = stubFetch(true);
    renderPage();
    const buttons = screen.getAllByRole("button", { name: "试一下" });
    expect(buttons.length).toBe(2); // 每个有关联规则的数字都有试算入口
    fireEvent.click(buttons[0]);
    expect(await screen.findByText("📊 试算：2026-08 = 607 户")).toBeTruthy();
    expect(
      fn.mock.calls.some((c) => String(c[0]).includes("/api/trial/R1?month=")),
    ).toBe(true);
  });

  it("试算失败: 灰条「试算暂不可用」且不阻塞页面（T205 同款容错）", async () => {
    stubFetch(false);
    renderPage();
    fireEvent.click(screen.getAllByRole("button", { name: "试一下" })[0]);
    expect(await screen.findByText("试算暂不可用")).toBeTruthy();
    expect(screen.getByText("注册用户数")).toBeTruthy(); // 数字卡仍在
  });

  it("维度降折叠速查: 默认收起，展开可见维度表；Tabs 退役", async () => {
    stubFetch(false);
    renderPage();
    expect(screen.queryByRole("tab")).toBeNull();
    expect(screen.queryByText("一级渠道：JOIN 渠道维 fst_chnl_nm")).toBeNull();
    fireEvent.click(screen.getByText("维度速查（1）"));
    expect(await screen.findByText("一级渠道：JOIN 渠道维 fst_chnl_nm")).toBeTruthy();
  });

  it("所属域: 登记表显示人话域徽标，无域不显示", () => {
    stubFetch(false);
    renderPage();
    expect(screen.getAllByText("用户域").length).toBe(1); // 只在有域的卡上出现
  });

  it("无关联规则的数字: 待确认标记、无试算入口（不造数据）", () => {
    stubFetch(false);
    const noCaliber: Ontology = {
      ...ontologyFixture,
      measures: [{ ...measurePending, caliber: null, domain: null, domain_name: null }],
    };
    render(<ObjectsPage ontology={noCaliber} />);
    expect(screen.queryByRole("button", { name: "试一下" })).toBeNull();
    expect(screen.getByText(/待确认 · 该数字暂无登记的口径规则/)).toBeTruthy();
    expect(screen.queryByText("用户域")).toBeNull();
  });
});