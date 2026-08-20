// 管道画布纯函数测试（dag → ReactFlow 元素；jsdom 无需 DOM）
import { describe, expect, it } from 'vitest';
import { SAMPLE_DAG, buildE2EFlow, buildPipelineFlow, layoutDagNodes } from './pipelineFlow';

describe('layoutDagNodes', () => {
  it('按拓扑层布局：roots=0，逐层 +1', () => {
    const layer = layoutDagNodes(SAMPLE_DAG.nodes);
    expect(layer.get('read_csv')).toBe(0);
    expect(layer.get('infer_schema')).toBe(1);
    expect(layer.get('cleanse')).toBe(2);
    expect(layer.get('store_curated')).toBe(3);
    expect(layer.get('output')).toBe(4);
  });
});

describe('buildPipelineFlow', () => {
  it('示例管道生成 5 节点 4 边', () => {
    const { nodes, edges } = buildPipelineFlow(SAMPLE_DAG);
    expect(nodes).toHaveLength(5);
    expect(edges).toHaveLength(4);
    expect(edges[0]).toEqual({ id: 'read_csv__infer_schema', source: 'read_csv', target: 'infer_schema' });
  });

  it('节点 kind 着色（connector=青 / storage=绿 / transform=橙 / output=蓝）', () => {
    const { nodes } = buildPipelineFlow(SAMPLE_DAG);
    const byId = new Map(nodes.map((n) => [n.id, n.data.color]));
    expect(byId.get('read_csv')).toBe('#13c2c2');
    expect(byId.get('store_curated')).toBe('#52c41a');
    expect(byId.get('cleanse')).toBe('#fa8c16');
    expect(byId.get('output')).toBe('#1677ff');
  });

  it('环状 DAG 不崩溃且仍生成边', () => {
    const dag = {
      nodes: [
        { id: 'a', kind: 'connector' as const, next: ['b'] },
        { id: 'b', kind: 'transform' as const, next: ['a'] },
      ],
    };
    const { nodes, edges } = buildPipelineFlow(dag);
    expect(nodes).toHaveLength(2);
    expect(edges).toHaveLength(2);
  });
});

describe('buildE2EFlow', () => {
  it('生成 5 个阶段聚合节点 + 4 条骨架边，条数来自各段列表', () => {
    const segments = {
      datasets: [{ name: 'suppliers_dirty.csv' }],
      curated: [{ name: 'cur_1' }],
      mappings: [],
      extractions: [],
      published: [{ name: 'Supplier' }],
    };
    const t = (k: string, _o?: Record<string, unknown>) => k;
    const { nodes, edges, counts } = buildE2EFlow(segments, t);
    expect(nodes).toHaveLength(5);
    expect(edges).toHaveLength(4);
    expect(counts).toEqual({ datasets: 1, curated: 1, mappings: 0, extractions: 0, publish: 1 });
    // 首节点 label 含真实条数（元数据驱动）
    expect(nodes[0].data.label).toContain('datasets');
    expect(nodes[0].data.label).toContain('1');
  });
});
