// 混合首页：React Flow 血缘图谱主体 + 顶部待确认横条（ADR-0012）。
import { useEffect, useMemo, useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Handle,
  Position,
  type Node,
  type Edge,
} from "@xyflow/react";
import { Alert, Button, Drawer, Space, Tag, Typography } from "antd";
import { api, type Lineage, type Ontology } from "../api";
import { forceLayout } from "../forceLayout";
import "@xyflow/react/dist/style.css";

const { Text } = Typography;

interface TableNodeData {
  label: string;
  layer: string;
  color: string;
  unconfirmed: boolean;
  [key: string]: unknown;
}

function TableNode({ data }: { data: TableNodeData }) {
  return (
    <div
      style={{
        background: "#fff",
        border: `1px solid ${data.unconfirmed ? "#ff4d4f" : "#d9d9d9"}`,
        borderLeft: `4px solid ${data.color}`,
        borderRadius: 6,
        padding: "6px 10px",
        minWidth: 150,
        boxShadow: data.unconfirmed
          ? "0 0 0 2px rgba(255,77,79,0.25)"
          : "0 1px 2px rgba(0,0,0,0.06)",
      }}
    >
      <Handle type="target" position={Position.Left} style={{ opacity: 0 }} />
      <div style={{ fontWeight: 600, fontSize: 12 }}>
        {data.label.split(".")[1] ?? data.label}
      </div>
      <div style={{ display: "flex", gap: 4, marginTop: 2, alignItems: "center" }}>
        <span style={{ fontSize: 10, color: data.color, fontWeight: 700 }}>
          {data.layer}
        </span>
        {data.unconfirmed && (
          <span
            style={{
              fontSize: 10,
              color: "#ff4d4f",
              border: "1px solid #ffccc7",
              borderRadius: 4,
              padding: "0 4px",
            }}
          >
            ⚠ 未确认口径
          </span>
        )}
      </div>
      <Handle type="source" position={Position.Right} style={{ opacity: 0 }} />
    </div>
  );
}

const nodeTypes = { tableNode: TableNode };

export default function GraphHome({
  lineage,
  ontology,
  onGoRules,
  reload,
}: {
  lineage: Lineage | null;
  ontology: Ontology | null;
  onGoRules: () => void;
  reload: () => void;
}) {
  const [selected, setSelected] = useState<string | null>(null);
  useEffect(reload, [reload]);

  const { flowNodes, flowEdges } = useMemo(() => {
    if (!lineage) return { flowNodes: [] as Node[], flowEdges: [] as Edge[] };
    const W = 1400;
    const H = 820;
    const pos = forceLayout(lineage, W, H);
    const flowNodes: Node[] = lineage.nodes.map((n) => ({
      id: n.id,
      type: "tableNode",
      position: pos[n.id],
      data: {
        label: n.label,
        layer: n.layer,
        color: lineage.layers[n.layer]?.color ?? "#8c8c8c",
        unconfirmed: n.unconfirmed,
      },
    }));
    const flowEdges: Edge[] = lineage.edges.map((e, i) => ({
      id: `e${i}`,
      source: e.source,
      target: e.target,
      animated: e.unconfirmed,
      style: e.unconfirmed
        ? { stroke: "#ff4d4f", strokeWidth: 2, strokeDasharray: "6 3" }
        : { stroke: "#bfbfbf", strokeWidth: 1 },
    }));
    return { flowNodes, flowEdges };
  }, [lineage]);

  if (!lineage || !ontology) return <Typography.Text>加载中…</Typography.Text>;

  const node = selected ? lineage.nodes.find((n) => n.id === selected) : null;
  const relatedRules = selected
    ? ontology.rules.filter((r) =>
        r.related_tables.some((t) => selected.includes(t))
      )
    : [];
  const upstream = lineage.edges
    .filter((e) => e.target === selected)
    .map((e) => e.source);
  const downstream = lineage.edges
    .filter((e) => e.source === selected)
    .map((e) => e.target);

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      {ontology.summary.pending > 0 && (
        <Alert
          banner
          type="warning"
          showIcon
          message={
            <Space>
              <span>
                <b>{ontology.summary.pending}</b> 条口径待确认（已确认{" "}
                {ontology.summary.confirmed}）—— 口径没钉死，数不准
              </span>
              <Button size="small" type="primary" onClick={onGoRules}>
                去确认 →
              </Button>
            </Space>
          }
        />
      )}
      <div style={{ flex: 1, minHeight: 0 }}>
        <ReactFlow
          nodes={flowNodes}
          edges={flowEdges}
          nodeTypes={nodeTypes}
          fitView
          minZoom={0.2}
          onNodeClick={(_, n) => setSelected(n.id)}
          proOptions={{ hideAttribution: true }}
        >
          <Background gap={24} />
          <Controls showInteractive={false} />
          <MiniMap pannable zoomable />
        </ReactFlow>
      </div>
      <div
        style={{
          display: "flex",
          gap: 16,
          padding: "6px 16px",
          borderTop: "1px solid #f0f0f0",
          alignItems: "center",
          flexWrap: "wrap",
        }}
      >
        {Object.entries(lineage.layers).map(([key, l]) => (
          <Space key={key} size={4}>
            <span
              style={{
                width: 10,
                height: 10,
                background: l.color,
                borderRadius: 2,
                display: "inline-block",
              }}
            />
            <Text style={{ fontSize: 12 }}>{l.label}</Text>
          </Space>
        ))}
        <span style={{ fontSize: 12, color: "#ff4d4f" }}>
          ⚠ 红色虚线边 = 关联未确认口径规则（{lineage.stats.unconfirmed_edges} 条）
        </span>
        <Text type="secondary" style={{ fontSize: 12 }}>
          {lineage.stats.nodes} 表 · {lineage.stats.edges} 边 · 点节点看详情
        </Text>
      </div>
      <Drawer
        open={!!node}
        onClose={() => setSelected(null)}
        title={node?.id}
        width={420}
      >
        {node && (
          <Space direction="vertical" size={12} style={{ width: "100%" }}>
            <Space>
              <Tag color={lineage.layers[node.layer]?.color}>{node.layer}</Tag>
              {node.unconfirmed && (
                <Tag color="red">关联未确认口径</Tag>
              )}
            </Space>
            <div>
              <Text type="secondary">上游 {upstream.length}：</Text>
              <div>
                {upstream.map((u) => (
                  <Tag key={u} style={{ cursor: "pointer" }} onClick={() => setSelected(u)}>
                    {u}
                  </Tag>
                ))}
              </div>
            </div>
            <div>
              <Text type="secondary">下游 {downstream.length}：</Text>
              <div>
                {downstream.map((u) => (
                  <Tag key={u} style={{ cursor: "pointer" }} onClick={() => setSelected(u)}>
                    {u}
                  </Tag>
                ))}
              </div>
            </div>
            {relatedRules.length > 0 && (
              <div>
                <Text type="secondary">关联口径规则：</Text>
                {relatedRules.map((r) => (
                  <div key={r.id}>
                    <Tag color={r.status === "confirmed" ? "green" : "orange"}>
                      {r.id} {r.status === "confirmed" ? "已确认" : "未确认"}
                    </Tag>
                    <Text style={{ fontSize: 12 }}>{r.description}</Text>
                  </div>
                ))}
              </div>
            )}
            <Button block type="primary" onClick={onGoRules}>
              去口径确认页 →
            </Button>
          </Space>
        )}
      </Drawer>
    </div>
  );
}
