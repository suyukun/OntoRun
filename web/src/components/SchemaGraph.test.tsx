/// <reference types="vitest/globals" />
// SchemaGraph 测试：buildGraphElements 元数据驱动断言 + 组件冒烟（cytoscape mock）
import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import SchemaGraph, { buildGraphElements } from './SchemaGraph';
import type { MetaSchema } from '../types';

vi.mock('cytoscape', () => ({
  default: (opts: { elements: unknown; container?: unknown }) => ({
    destroy: vi.fn(),
    elements: opts.elements,
  }),
}));

const mockMeta: MetaSchema = {
  objects: [
    { name: 'Order', api_name: 'order', description: '订单', pk_field: 'order_id', title_field: 'order_id', source_table: 'orders', properties: {} },
    { name: 'Customer', api_name: 'customer', description: '客户', pk_field: 'customer_id', title_field: 'customer_id', source_table: 'customers', properties: {} },
  ],
  links: [
    { name: 'order.customer', source_type: 'Order', target_type: 'Customer', cardinality: 'N:1', fk_field: 'customer_id', inverse_name: 'customer.orders', description: '下单' },
  ],
  actions: [],
};

beforeEach(() => {
  vi.clearAllMocks();
});

describe('buildGraphElements', () => {
  it('节点=对象类型，边=链接类型，标注方向与基数', () => {
    const { nodes, edges } = buildGraphElements(mockMeta);
    expect(nodes).toHaveLength(2);
    expect(nodes.map((n) => n.data.id)).toEqual(['Order', 'Customer']);
    expect(edges).toHaveLength(1);
    expect(edges[0].data.source).toBe('Order');
    expect(edges[0].data.target).toBe('Customer');
    expect(edges[0].data.label).toBe('order.customer [N:1]');
  });

  it('空 schema 返回空元素', () => {
    const { nodes, edges } = buildGraphElements({ objects: [], links: [], actions: [] });
    expect(nodes).toHaveLength(0);
    expect(edges).toHaveLength(0);
  });
});

describe('SchemaGraph 组件冒烟', () => {
  it('渲染图谱容器（cytoscape mock 不崩）', () => {
    render(<SchemaGraph meta={mockMeta} />);
    expect(screen.getByTestId('schema-graph')).toBeTruthy();
  });

  it('无数据时显示提示', () => {
    render(<SchemaGraph meta={{ objects: [], links: [], actions: [] }} />);
    expect(screen.getByText(/本体元数据为空/)).toBeTruthy();
  });
});
