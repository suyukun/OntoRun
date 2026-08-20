// 管道画布数据转换（纯函数，不依赖 React/DOM，便于 vitest 断言）
import type { Node, Edge } from '@xyflow/react';
import type { DagJson, DagNode } from './builderTypes';

export type FlowNodeData = {
  label: string;
  sub?: string;
  kind?: string;
  status?: string;
  color?: string;
} & Record<string, unknown>;

export type FlowNode = Node<FlowNodeData>;
export type FlowEdge = Edge;

export const NODE_KINDS = ['connector', 'storage', 'transform', 'output'] as const;

export const KIND_COLORS: Record<string, string> = {
  connector: '#13c2c2',
  storage: '#52c41a',
  transform: '#fa8c16',
  output: '#1677ff',
};

/** 对 dag 节点做分层布局（BFS：roots 在 layer 0，next 指向的节点层 = 最大上游层 + 1） */
export function layoutDagNodes(nodes: DagNode[]): Map<string, number> {
  const layer = new Map<string, number>();
  const indegree = new Map(nodes.map((n) => [n.id, 0]));
  for (const n of nodes) {
    for (const nx of n.next || []) {
      indegree.set(nx, (indegree.get(nx) || 0) + 1);
    }
  }
  // Kahn 拓扑（保持 id 稳定顺序）
  const queue = nodes.filter((n) => (indegree.get(n.id) || 0) === 0).map((n) => n.id);
  const order: string[] = [];
  const downstream = new Map<string, string[]>();
  for (const n of nodes) downstream.set(n.id, [...(n.next || [])]);
  while (queue.length) {
    const id = queue.shift()!;
    order.push(id);
    for (const nx of downstream.get(id) || []) {
      indegree.set(nx, (indegree.get(nx) || 0) - 1);
      if ((indegree.get(nx) || 0) === 0) queue.push(nx);
    }
  }
  // 环兜底：未入序的节点按序补在最后
  for (const n of nodes) {
    if (!order.includes(n.id)) order.push(n.id);
  }
  for (const id of order) {
    const ups = nodes.filter((x) => (x.next || []).includes(id));
    const upLayers = ups.map((u) => layer.get(u.id) ?? 0);
    layer.set(id, ups.length ? Math.max(...upLayers) + 1 : 0);
  }
  return layer;
}

/** dag_json → ReactFlow 元素（自动分层布局 + kind 着色） */
export function buildPipelineFlow(dag: DagJson): { nodes: FlowNode[]; edges: FlowEdge[] } {
  const nodesList: DagNode[] = Array.isArray(dag.nodes) ? dag.nodes : [];
  const layer = layoutDagNodes(nodesList);
  const perLayer = new Map<number, number>();
  const nodes: FlowNode[] = nodesList.map((n) => {
    const l = layer.get(n.id) ?? 0;
    const idx = perLayer.get(l) ?? 0;
    perLayer.set(l, idx + 1);
    const status = (n.config && typeof n.config.status === 'string') ? n.config.status : undefined;
    return {
      id: n.id,
      type: 'dag',
      position: { x: 40 + l * 280, y: 40 + idx * 130 },
      data: {
        label: n.id,
        sub: n.kind,
        kind: n.kind,
        status,
        color: KIND_COLORS[n.kind] || '#8c8c8c',
      },
    };
  });
  const edges: FlowEdge[] = [];
  for (const n of nodesList) {
    for (const nx of n.next || []) {
      if (nodesList.some((x) => x.id === nx)) {
        edges.push({ id: n.id + '__' + nx, source: n.id, target: nx });
      }
    }
  }
  return { nodes, edges };
}

export interface E2ESegments {
  datasets: { name?: string; id?: string }[];
  curated: { name?: string; id?: string }[];
  mappings: { name?: string; id?: string }[];
  extractions: { name?: string; id?: string }[];
  published: { name?: string; id?: string }[];
}

export interface E2EStage {
  key: string;
  x: number;
  color: string;
}

export const E2E_STAGES: E2EStage[] = [
  { key: 'datasets', x: 80, color: '#13c2c2' },
  { key: 'curated', x: 340, color: '#52c41a' },
  { key: 'mappings', x: 600, color: '#fa8c16' },
  { key: 'extractions', x: 860, color: '#722ed1' },
  { key: 'publish', x: 1120, color: '#eb2f96' },
];

function namesOf(list: { name?: string; id?: string }[], n: number): string[] {
  return list.slice(0, n).map((x) => x.name || x.id || '').filter(Boolean);
}

/** 端到端流程概览：5 个构建阶段聚合节点 + 层间骨架边（条数/条目来自各段列表） */
export function buildE2EFlow(segments: E2ESegments, t: (key: string, opts?: Record<string, unknown>) => string): {
  nodes: FlowNode[];
  edges: FlowEdge[];
  counts: Record<string, number>;
} {
  const counts: Record<string, number> = {
    datasets: segments.datasets.length,
    curated: segments.curated.length,
    mappings: segments.mappings.length,
    extractions: segments.extractions.length,
    publish: segments.published.length,
  };
  const items: Record<string, string[]> = {
    datasets: namesOf(segments.datasets, 3),
    curated: namesOf(segments.curated, 3),
    mappings: namesOf(segments.mappings, 3),
    extractions: namesOf(segments.extractions, 3),
    publish: namesOf(segments.published, 3),
  };
  const nodes: FlowNode[] = E2E_STAGES.map((s, i) => ({
    id: 'stage-' + s.key,
    type: 'dag',
    position: { x: s.x, y: 120 + i * 20 },
    data: {
      label: t('builder.' + s.key) + ' (' + (counts[s.key] ?? 0) + ')',
      sub: (items[s.key] || []).join(' · ') || t('common.noData'),
      kind: i === 4 ? 'output' : i === 0 ? 'connector' : i === 1 ? 'storage' : 'transform',
      color: s.color,
    },
  }));
  const edges: FlowEdge[] = E2E_STAGES.slice(1).map((s, i) => ({
    id: 'e2e-' + E2E_STAGES[i].key + '-' + s.key,
    source: 'stage-' + E2E_STAGES[i].key,
    target: 'stage-' + s.key,
    animated: true,
  }));
  return { nodes, edges, counts };
}

/** 示例管道（演示端到端：CSV → schema 推断 → 清洗 → 落 curated → 输出） */
export const SAMPLE_DAG: DagJson = {
  nodes: [
    { id: 'read_csv', kind: 'connector', config: { path: 'data/builder_samples/suppliers_dirty.csv' }, next: ['infer_schema'] },
    { id: 'infer_schema', kind: 'transform', config: { op: 'schema_infer' }, next: ['cleanse'] },
    { id: 'cleanse', kind: 'transform', config: { op: 'cleanse' }, next: ['store_curated'] },
    { id: 'store_curated', kind: 'storage', config: { op: 'curated' }, next: ['output'] },
    { id: 'output', kind: 'output', config: {}, next: [] },
  ],
};