// T403 域图组件（§A2-US3）：业务域全景图——域节点 + 域间聚合边 + 域详情 Drawer。
// 数据契约 = T401 lineage payload（src/fortune_admin/lineage.py domain_view）：
//   domains[].{key,name,table_count,replicas,pending,divergent,ads_metric_count}
//   domain_edges[].{source,target,weight,severity: settled|pending|divergent}
// Jack 裁决落点（调研文档 §9）：裁决2 只渲染有表域（payload 含金控 10 域全集，
// 0 表域 = 扩展位，隐藏是前端渲染责任）；裁决7 ADS 指标位（ads_metric_count>0
// 显示「N 张指标」小徽标，不占表登记）。
// 挂载进首页（横条 + 画布 + 顶部常驻「图例与健康度」行）由 T503 收口；本组件
// 先自带图例行最小版（三色边例 + 全站待确认/分歧计数）。
import { useEffect, useMemo, useState } from "react";
import { Alert, Drawer, Typography } from "antd";
import { forceLayout, type Pt } from "../forceLayout";
import type { Lineage } from "../api";

const { Text } = Typography;

export type EdgeSeverity = "settled" | "pending" | "divergent";

export interface DomainInfo {
  key: string;
  name: string;
  /** 一句话简介（registry Domain 契约含；lineage payload 暂未透出，可选） */
  description?: string;
  /** 逻辑表数（同表名多 schema 副本算 1 张，裁决 5） */
  table_count: number;
  /** 物理登记表数（Drawer 附注用） */
  replicas: number;
  pending: number;
  divergent: number;
  ads_metric_count: number;
}

export interface DomainAggEdge {
  source: string;
  target: string;
  /** 聚合的表级血缘边数 N（×N 角标） */
  weight: number;
  severity: EdgeSeverity;
}

export interface DomainLineagePayload {
  domains: DomainInfo[];
  domain_edges: DomainAggEdge[];
}

// qc6_node_cap：任一图视图节点 ≤30，超出截断并提示（域层 ≤10 用不到，防御性；
// T404 域内图复用本 cap 逻辑）。
export const NODE_CAP = 30;

export function capNodes<T>(
  nodes: T[],
  cap: number = NODE_CAP
): { kept: T[]; total: number; truncated: boolean } {
  return {
    kept: nodes.slice(0, cap),
    total: nodes.length,
    truncated: nodes.length > cap,
  };
}

// 三级边样式（§A2-US3 / edge_aggregation_severity）：settled 灰实线 /
// pending 橙虚线 / divergent 红虚线。色板跟随 GraphHome 既有红/灰 + antd 橙。
export const EDGE_STYLES: Record<
  EdgeSeverity,
  { stroke: string; dasharray?: string; width: number; label: string }
> = {
  settled: { stroke: "#bfbfbf", width: 1.5, label: "已确认" },
  pending: { stroke: "#fa8c16", dasharray: "6 4", width: 1.5, label: "待确认" },
  divergent: { stroke: "#ff4d4f", dasharray: "6 4", width: 2, label: "分歧" },
};

// 布局接线点：对「接收节点+边、返回 id->坐标」的布局函数编程。现接 T402 升级
// 前的 forceLayout 旧签名（Lineage 形状适配；域层节点 ≤10 假设成立）。T402
// （固定种子+碰撞）合入后只需改本函数，不动组件渲染。
function layoutDomains(
  domains: DomainInfo[],
  edges: DomainAggEdge[],
  width: number,
  height: number
): Record<string, Pt> {
  const pseudo: Lineage = {
    nodes: domains.map((d) => ({
      id: d.key,
      label: d.name,
      layer: "DOMAIN",
      unconfirmed: false,
    })),
    edges: edges.map((e) => ({
      source: e.source,
      target: e.target,
      via_script: "",
      unconfirmed: false,
    })),
    layers: {},
    stats: { nodes: domains.length, edges: edges.length, unconfirmed_edges: 0 },
  };
  return forceLayout(pseudo, width, height);
}

function DomainBadges({ domain }: { domain: DomainInfo }) {
  return (
    <>
      {domain.pending > 0 && (
        <span
          aria-label={`待确认 ${domain.pending} 条`}
          title={`待确认口径 ${domain.pending} 条`}
          style={{
            background: "#ff4d4f",
            color: "#fff",
            borderRadius: 9,
            minWidth: 18,
            height: 18,
            fontSize: 11,
            fontWeight: 700,
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "0 5px",
          }}
        >
          {domain.pending}
        </span>
      )}
      {domain.divergent > 0 && (
        <span
          aria-label={`分歧 ${domain.divergent} 条`}
          title={`未裁分歧 ${domain.divergent} 条——红虚线，待 R8 裁决`}
          style={{ fontSize: 13 }}
        >
          ⚡
        </span>
      )}
    </>
  );
}

function DomainNodeCard({
  domain,
  x,
  y,
  onOpen,
}: {
  domain: DomainInfo;
  x: number;
  y: number;
  onOpen: () => void;
}) {
  return (
    <div
      data-testid={`domain-node-${domain.key}`}
      onClick={onOpen}
      style={{
        position: "absolute",
        left: x,
        top: y,
        transform: "translate(-50%,-50%)",
        zIndex: 1,
        cursor: "pointer",
        background: "#fff",
        border: "1px solid #d9d9d9",
        borderRadius: 8,
        padding: "8px 12px",
        minWidth: 132,
        boxShadow: "0 1px 2px rgba(0,0,0,0.06)",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
        <span style={{ fontWeight: 600, fontSize: 13 }}>{domain.name}</span>
        <DomainBadges domain={domain} />
      </div>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 6,
          marginTop: 2,
        }}
      >
        <Text type="secondary" style={{ fontSize: 11 }}>
          {domain.table_count} 表
        </Text>
        {domain.ads_metric_count > 0 && (
          <span
            title="ADS 应用层指标产出（不占表登记，裁决 7）"
            style={{
              fontSize: 11,
              color: "#fa8c16",
              border: "1px solid #ffd591",
              borderRadius: 4,
              padding: "0 4px",
            }}
          >
            {domain.ads_metric_count} 张指标
          </span>
        )}
      </div>
    </div>
  );
}

// 图例行最小版：三色边例 + 全站待确认/分歧计数（同源 payload 汇总，不手填）。
// 顶部常驻「图例与健康度」行的版式由 T503 收口。
function LegendRow({
  totalPending,
  totalDivergent,
  nodeCount,
}: {
  totalPending: number;
  totalDivergent: number;
  nodeCount: number;
}) {
  return (
    <div
      data-testid="domain-graph-legend"
      style={{
        display: "flex",
        gap: 16,
        alignItems: "center",
        flexWrap: "wrap",
        padding: "6px 4px",
        borderTop: "1px solid #f0f0f0",
      }}
    >
      {(Object.entries(EDGE_STYLES) as [EdgeSeverity, (typeof EDGE_STYLES)[EdgeSeverity]][]).map(
        ([sev, st]) => (
          <span
            key={sev}
            style={{ display: "inline-flex", alignItems: "center", gap: 4 }}
          >
            <svg width={28} height={10} aria-hidden>
              <line
                data-testid={`legend-edge-${sev}`}
                x1={0}
                y1={5}
                x2={28}
                y2={5}
                stroke={st.stroke}
                strokeWidth={st.width}
                strokeDasharray={st.dasharray}
              />
            </svg>
            <Text style={{ fontSize: 12 }}>{st.label}</Text>
          </span>
        )
      )}
      <Text type="secondary" style={{ fontSize: 12 }}>
        全站待确认 {totalPending} · 分歧 {totalDivergent} ·{" "}
        {nodeCount} 个有表域 · 点域节点看详情
      </Text>
    </div>
  );
}

function DomainDrawer({
  domain,
  onClose,
}: {
  domain: DomainInfo | null;
  onClose: () => void;
}) {
  return (
    <Drawer open={!!domain} onClose={onClose} title={domain?.name}>
      {domain && (
        // 登记来源行（王工走查修订 2）：登记制走 git，谁/哪个版本划入见变更历史
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {domain.description && <Text>{domain.description}</Text>}
          <div>
            <Text type="secondary">表数：</Text>
            <Text>
              {domain.table_count} 张（逻辑口径；物理登记 {domain.replicas} 张）
            </Text>
          </div>
          <div>
            <Text type="secondary">待确认：</Text>
            <Text>{domain.pending} 条</Text>
          </div>
          <div>
            <Text type="secondary">分歧：</Text>
            <Text>{domain.divergent} 条未裁</Text>
          </div>
          <div>
            <Text type="secondary">ADS 指标：</Text>
            <Text>{domain.ads_metric_count} 张指标</Text>
          </div>
          <div
            style={{
              background: "#fafafa",
              border: "1px solid #f0f0f0",
              borderRadius: 6,
              padding: "8px 10px",
            }}
          >
            <Text type="secondary" style={{ fontSize: 12 }}>
              域与表的登记：git 管理，谁在哪个版本划入——见变更历史
            </Text>
          </div>
        </div>
      )}
    </Drawer>
  );
}

export default function DomainGraph({
  width = 1200,
  height = 620,
}: {
  width?: number;
  height?: number;
}) {
  const [payload, setPayload] = useState<DomainLineagePayload | null>(null);
  const [loadError, setLoadError] = useState(false);
  const [selected, setSelected] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    fetch("/api/lineage")
      .then((res) => {
        if (!res.ok) throw new Error(`/api/lineage -> HTTP ${res.status}`);
        return res.json();
      })
      .then((data: DomainLineagePayload) => {
        if (alive) setPayload(data);
      })
      .catch(() => {
        if (alive) setLoadError(true);
      });
    return () => {
      alive = false;
    };
  }, []);

  // Jack 裁决 2：0 表域隐藏（payload 保留 10 域开放框架全集，过滤是前端责任）
  const visibleDomains = useMemo(
    () => (payload ? payload.domains.filter((d) => d.table_count > 0) : []),
    [payload]
  );
  const cap = useMemo(() => capNodes(visibleDomains), [visibleDomains]);
  const keptKeys = useMemo(
    () => new Set(cap.kept.map((d) => d.key)),
    [cap]
  );
  const visibleEdges = useMemo(
    () =>
      payload
        ? payload.domain_edges.filter(
            (e) => keptKeys.has(e.source) && keptKeys.has(e.target)
          )
        : [],
    [payload, keptKeys]
  );
  const positions = useMemo(
    () => layoutDomains(cap.kept, visibleEdges, width, height),
    [cap, visibleEdges, width, height]
  );

  const selectedDomain =
    selected && payload
      ? (payload.domains.find((d) => d.key === selected) ?? null)
      : null;
  // 全站计数 = payload 全域汇总（含隐藏扩展位；与后端同源，不手填）
  const totalPending =
    payload?.domains.reduce((sum, d) => sum + d.pending, 0) ?? 0;
  const totalDivergent =
    payload?.domains.reduce((sum, d) => sum + d.divergent, 0) ?? 0;

  if (loadError)
    return <Alert type="error" showIcon title="血缘加载失败，请刷新重试" />;
  if (!payload) return <Text>加载中…</Text>;
  if (cap.total === 0)
    return <Text>暂无有表业务域——先在语义层把表登记到域</Text>;

  return (
    <div>
      <div
        data-testid="domain-graph-canvas"
        style={{ position: "relative", width, height, overflow: "hidden" }}
      >
        <svg
          width={width}
          height={height}
          style={{ position: "absolute", inset: 0 }}
        >
          {visibleEdges.map((e) => {
            const s = positions[e.source];
            const t = positions[e.target];
            if (!s || !t) return null;
            const st = EDGE_STYLES[e.severity];
            return (
              <g key={`${e.source}->${e.target}`}>
                <line
                  data-severity={e.severity}
                  x1={s.x}
                  y1={s.y}
                  x2={t.x}
                  y2={t.y}
                  stroke={st.stroke}
                  strokeWidth={st.width}
                  strokeDasharray={st.dasharray}
                />
                <text
                  data-testid={`edge-weight-${e.source}-${e.target}`}
                  x={(s.x + t.x) / 2}
                  y={(s.y + t.y) / 2}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fontSize={10}
                  fontWeight={700}
                  fill={st.stroke}
                  stroke="#fff"
                  strokeWidth={3}
                  paintOrder="stroke"
                >
                  ×{e.weight}
                </text>
              </g>
            );
          })}
        </svg>
        {cap.truncated && (
          <Alert
            type="warning"
            showIcon
            style={{
              position: "absolute",
              top: 8,
              left: 8,
              zIndex: 2,
              maxWidth: 460,
            }}
            data-testid="domain-graph-truncated"
            title={`节点超过 ${NODE_CAP} 个，已截断显示前 ${NODE_CAP} 个（共 ${cap.total} 个）`}
          />
        )}
        {cap.kept.map((d) => (
          <DomainNodeCard
            key={d.key}
            domain={d}
            x={positions[d.key].x}
            y={positions[d.key].y}
            onOpen={() => setSelected(d.key)}
          />
        ))}
      </div>
      <LegendRow
        totalPending={totalPending}
        totalDivergent={totalDivergent}
        nodeCount={cap.total}
      />
      <DomainDrawer
        domain={selectedDomain}
        onClose={() => setSelected(null)}
      />
    </div>
  );
}
