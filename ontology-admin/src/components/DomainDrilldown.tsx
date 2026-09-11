// T404 域内图（三层下钻第二层，§A2-US3）：域图下钻后的域内表级视图。
// 依据 docs/design/管理台重设计-域级总览图专项_v0.1.md §3（域内图=分层左→右分列、
// 跨域边默认不画只留底部摘要行）+ §1.1（存储层=副轴：分列是它的主场）。
// 数据契约 = T401 /api/lineage payload（src/fortune_admin/lineage.py）：
//   nodes[].{id,label,layer,domain} / edges[].{source,target}
//   domains[].{key,name,...} / domain_edges[].{source,target,weight,severity}
// 复用 T403 DomainGraph 导出：capNodes/NODE_CAP（qc6_node_cap）+ EDGE_STYLES
// （三色边样式）+ DomainInfo/DomainAggEdge/EdgeSeverity 类型。
// 相关指标推导口径（裁决 7 延伸，前端自述）：ADS 表（domain=null 且 layer=ADS，
// 裁决 4 ADS 不按数据域登记）其**任一直接上游**源表登记在本域 → 相关；
// 一跳不递归（与 lineage.py ads_metric_count 同口径）。后端域汇总只有数字、
// 不透出指标表清单，故清单由前端从 edges 推导。
// 本任务判据内明确不做（专项设计 §3 有提，留后续收口）：域内表级边连线、
// 层筛选 chips、域内搜表；本组件先做到「分列 + 点击跳表详情 + 摘要行」最小版。
import { useEffect, useMemo, useState } from "react";
import { Alert, Breadcrumb, Collapse, Empty, Typography } from "antd";
import {
  capNodes,
  EDGE_STYLES,
  NODE_CAP,
  type DomainAggEdge,
  type DomainInfo,
  type EdgeSeverity,
} from "./DomainGraph";

const { Text } = Typography;

// payload 子集类型（lineage.py 契约；api.ts 的 LineageNode 未含 domain 字段，
// 域装配后的完整形状以本组件自述为准，与 DomainGraph 自带子集类型同惯例）。
export interface DrilldownTableNode {
  id: string;
  label: string;
  layer: string;
  domain: string | null;
  unconfirmed: boolean;
}

export interface DrilldownLineageEdge {
  source: string;
  target: string;
}

export interface DrilldownPayload {
  nodes: DrilldownTableNode[];
  edges: DrilldownLineageEdge[];
  domains: DomainInfo[];
  domain_edges: DomainAggEdge[];
  layers: Record<string, { color: string; label: string }>;
}

// 分列列序 = 加工流向左→右（§1.1 副轴主场）：ODS 贴源 → CDM 明细/维表 →
// DIM 外部维表 → ADS 应用汇总（指标出口最右）。值域跟随 lineage.py classify()
// 现有四值（实盘 cdm.dwd_* 也归 CDM 层），不发明新层。
const LAYER_ORDER: readonly string[] = ["ODS", "CDM", "DIM", "ADS"];

function shortName(id: string): string {
  return id.split(".")[1] ?? id;
}

function layerRank(layer: string): number {
  const i = LAYER_ORDER.indexOf(layer);
  return i < 0 ? LAYER_ORDER.length : i; // 未识别层排最后（防御，见下）
}

function TableNodeCard({ node, color }: { node: DrilldownTableNode; color: string }) {
  return (
    <div
      data-testid={`table-node-${node.id}`}
      title={node.id}
      onClick={() => {
        // 既有表详情路由（T301）：#/object/table/{id}
        window.location.hash = `#/object/table/${encodeURIComponent(node.id)}`;
      }}
      style={{
        cursor: "pointer",
        background: "#fff",
        border: "1px solid #d9d9d9",
        borderLeft: `4px solid ${color}`, // 层色条（§3 节点内容）
        borderRadius: 6,
        padding: "6px 10px",
        marginBottom: 8,
        boxShadow: "0 1px 2px rgba(0,0,0,0.06)",
        display: "flex",
        alignItems: "center",
        gap: 6,
      }}
    >
      <Text style={{ fontSize: 12 }}>{shortName(node.id)}</Text>
      {node.unconfirmed && (
        <span title="关联未确认口径" style={{ fontSize: 11, color: "#ff4d4f" }}>
          ⚠
        </span>
      )}
    </div>
  );
}

// 列头带该层表数（§3）；count = 本域该层登记表总数（截断前口径，数字不失真）
function LayerColumn({
  layer,
  meta,
  tables,
  count,
}: {
  layer: string;
  meta?: { color: string; label: string };
  tables: DrilldownTableNode[];
  count: number;
}) {
  const color = meta?.color ?? "#8c8c8c";
  return (
    <div data-testid={`layer-col-${layer}`} style={{ minWidth: 170 }}>
      <div
        style={{
          borderBottom: `2px solid ${color}`,
          paddingBottom: 4,
          marginBottom: 8,
        }}
      >
        <Text strong style={{ fontSize: 13 }}>
          {meta?.label ?? layer}
        </Text>
        <Text type="secondary" style={{ fontSize: 12 }}>
          （{count}）
        </Text>
      </div>
      {tables.map((n) => (
        <TableNodeCard key={n.id} node={n} color={color} />
      ))}
    </div>
  );
}

export default function DomainDrilldown({
  domainKey,
  onBackToGraph,
  onOpenDomain,
}: {
  /** 当前域 key（App 暂无域下钻路由参，宿主接线后可改自取——按现状最小实现） */
  domainKey: string;
  /** 面包屑回域图；缺省 = 既有 hash 路由 #/graph */
  onBackToGraph?: () => void;
  /** 跨域摘要点其他域；缺省 = 回域图（域图暂无「按域选中」路由参，T503 接线时预选） */
  onOpenDomain?: (key: string) => void;
}) {
  const [payload, setPayload] = useState<DrilldownPayload | null>(null);
  const [loadError, setLoadError] = useState(false);

  useEffect(() => {
    let alive = true;
    fetch("/api/lineage")
      .then((res) => {
        if (!res.ok) throw new Error(`/api/lineage -> HTTP ${res.status}`);
        return res.json();
      })
      .then((data: DrilldownPayload) => {
        if (alive) setPayload(data);
      })
      .catch(() => {
        if (alive) setLoadError(true);
      });
    return () => {
      alive = false;
    };
  }, []);

  const domain = useMemo(
    () => payload?.domains.find((d) => d.key === domainKey) ?? null,
    [payload, domainKey]
  );

  // 本域登记表（含防御性 registered ADS——现实里裁决 4 ADS 不登记，契约不禁止）
  const domainTables = useMemo(
    () => (payload ? payload.nodes.filter((n) => n.domain === domainKey) : []),
    [payload, domainKey]
  );

  // qc6_node_cap：>30 截断。截断是 UI 行为不是数据行为（payload 不截，前端截）；
  // 排序按（层序，表名字典序）取前 30（§3 截断策略 2），保证截断结果稳定可复现。
  const sortedTables = useMemo(
    () =>
      [...domainTables].sort(
        (a, b) => layerRank(a.layer) - layerRank(b.layer) || (a.id < b.id ? -1 : 1)
      ),
    [domainTables]
  );
  const cap = useMemo(() => capNodes(sortedTables), [sortedTables]);

  // 分列：byLayer=截断前按层计数（列头数字不失真），keptByLayer=截断后列体
  const byLayer = useMemo(() => {
    const m = new Map<string, DrilldownTableNode[]>();
    for (const n of domainTables) {
      const list = m.get(n.layer) ?? [];
      list.push(n);
      m.set(n.layer, list);
    }
    return m;
  }, [domainTables]);
  const keptByLayer = useMemo(() => {
    const m = new Map<string, DrilldownTableNode[]>();
    for (const n of cap.kept) {
      const list = m.get(n.layer) ?? [];
      list.push(n);
      m.set(n.layer, list);
    }
    return m;
  }, [cap]);
  // 列 = 出现过的层（空层不渲染）；未识别层按字典序垫底（lineage.classify 只出
  // 四值，出现即契约外数据，防御性照渲染不静默丢表）
  const shownLayers = useMemo(() => {
    const present = [...byLayer.keys()];
    return present.sort((a, b) => layerRank(a) - layerRank(b) || (a < b ? -1 : 1));
  }, [byLayer]);

  // 相关指标表（裁决 7 延伸）：口径见文件头注释——ADS 表 domain=null 且
  // layer=ADS，其任一直接上游（edges 一跳）源表 domain=本域 → 相关；一跳不
  // 递归（ADS 中间表不算上游通路），与 lineage.py ads_metric_count 同口径。
  const relatedAds = useMemo(() => {
    if (!payload) return [];
    const domainOf = new Map(payload.nodes.map((n) => [n.id, n.domain]));
    return payload.nodes
      .filter((n) => n.layer === "ADS" && n.domain === null)
      .filter((n) =>
        payload.edges.some(
          (e) => e.target === n.id && domainOf.get(e.source) === domainKey
        )
      )
      .map((n) => n.id)
      .sort();
  }, [payload, domainKey]);

  // 跨域摘要：domain_edges 过滤本域（backend 已排除同域内部边，此处不重复滤）
  const crossEdges = useMemo(
    () =>
      payload
        ? payload.domain_edges.filter(
            (e) => e.source === domainKey || e.target === domainKey
          )
        : [],
    [payload, domainKey]
  );
  const domainName = (key: string) =>
    payload?.domains.find((d) => d.key === key)?.name ?? key;

  const backToGraph = () => {
    if (onBackToGraph) onBackToGraph();
    else window.location.hash = "#/graph";
  };
  const openDomain = (key: string) => {
    if (onOpenDomain) onOpenDomain(key);
    else window.location.hash = "#/graph";
  };

  if (loadError)
    return <Alert type="error" showIcon title="血缘加载失败，请刷新重试" />;
  if (!payload) return <Text>加载中…</Text>;

  const crossSeverity = (sev: EdgeSeverity) => EDGE_STYLES[sev];

  return (
    <div style={{ padding: "8px 12px" }}>
      {/* 面包屑（drilldown_breadcrumb）：全域图 / 当前域名，最小两级（T503 收口统一） */}
      <Breadcrumb
        data-testid="drilldown-breadcrumb"
        items={[
          { title: "全域图", onClick: backToGraph },
          { title: domain?.name ?? domainKey },
        ]}
      />
      {domainTables.length === 0 ? (
        // 空态出路（§4.1）：域=登记出来的，没登记不是 bug 是欠账
        <Empty
          style={{ marginTop: 48 }}
          description="该域暂无登记表（域=登记出来的）——先在语义层 registry 把表登记进域"
        />
      ) : (
        <>
          {cap.truncated && (
            <Alert
              type="warning"
              showIcon
              data-testid="drilldown-truncated"
              style={{ marginTop: 8 }}
              title={`已截断：显示 ${NODE_CAP}/${cap.total} 张（节点上限 ${NODE_CAP}）`}
            />
          )}
          <div
            data-testid="drilldown-canvas"
            style={{
              display: "flex",
              gap: 24,
              alignItems: "flex-start",
              marginTop: 12,
              overflowX: "auto",
            }}
          >
            {shownLayers.map((layer) => (
              <LayerColumn
                key={layer}
                layer={layer}
                meta={payload.layers[layer]}
                count={byLayer.get(layer)?.length ?? 0}
                tables={keptByLayer.get(layer) ?? []}
              />
            ))}
          </div>
        </>
      )}
      {relatedAds.length > 0 && (
        // 相关指标折叠区（裁决 7 延伸）：默认收起，标「N 张指标表」；0 张不渲染
        <Collapse
          data-testid="related-metrics"
          style={{ marginTop: 12 }}
          items={[
            {
              key: "related-ads",
              label: `相关指标表 ${relatedAds.length} 张`,
              children: relatedAds.map((id) => (
                <div key={id}>
                  <Text style={{ fontSize: 12 }}>{id}</Text>
                </div>
              )),
            },
          ]}
        />
      )}
      {crossEdges.length > 0 && (
        // 跨域摘要行（§3）：跨域边默认不画进画布，底部一行三色+×N 摘要防挤坨
        <div
          data-testid="cross-domain-summary"
          style={{
            display: "flex",
            gap: 16,
            alignItems: "center",
            flexWrap: "wrap",
            borderTop: "1px solid #f0f0f0",
            marginTop: 12,
            padding: "8px 4px",
          }}
        >
          <Text type="secondary" style={{ fontSize: 12 }}>
            ⌁ 跨域链路：
          </Text>
          {crossEdges.map((e) => {
            const other = e.source === domainKey ? e.target : e.source;
            const st = crossSeverity(e.severity);
            return (
              <span
                key={`${e.source}->${e.target}`}
                data-testid={`cross-edge-${other}`}
                title={`跳回域图：${domainName(other)}`}
                onClick={() => openDomain(other)}
                style={{
                  cursor: "pointer",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 4,
                }}
              >
                <svg width={28} height={10} aria-hidden>
                  <line
                    data-severity={e.severity}
                    x1={0}
                    y1={5}
                    x2={28}
                    y2={5}
                    stroke={st.stroke}
                    strokeWidth={st.width}
                    strokeDasharray={st.dasharray}
                  />
                </svg>
                <Text style={{ fontSize: 12 }}>{domainName(other)}</Text>
                <Text strong style={{ fontSize: 12, color: st.stroke }}>
                  ×{e.weight}
                </Text>
              </span>
            );
          })}
        </div>
      )}
    </div>
  );
}
