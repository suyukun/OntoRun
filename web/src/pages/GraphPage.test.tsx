/// <reference types="vitest/globals" />
// GraphPage 冒烟：聚合图谱端点（/api/v1/builder/graph）驱动渲染，含 S3 金控风险行
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import GraphPage from './GraphPage';

vi.mock('cytoscape', () => ({
  default: (opts: { elements: unknown; container?: unknown }) => ({
    destroy: vi.fn(),
    elements: opts.elements,
  }),
}));

const mockFetch = vi.fn();
(globalThis as typeof globalThis & { fetch: typeof mockFetch }).fetch = mockFetch;

// 聚合图谱响应：内置零售段（Order）+ S3 金控风险段（risk_customer / warning_signal）
const graphResponse = {
  request_id: 'req_graph',
  outcome: 'ok',
  data: {
    objects: [
      { name: 'Order', api_name: 'order', description: '订单', pk_field: 'order_id', title_field: 'order_id', source_table: 'orders', properties: {} },
      { name: 'risk_customer', api_name: 'risk_customer', description: '风险客户', pk_field: 'customer_no', title_field: 'customer_no', source_table: 'customer.ap_customer', properties: {} },
      { name: 'warning_signal', api_name: 'warning_signal', description: '预警信号', pk_field: 'signal_id', title_field: 'signal_id', source_table: 'ap_warning_signal', properties: {} },
    ],
    links: [
      { name: 'order.customer', source_type: 'Order', target_type: 'Customer', cardinality: 'N:1', fk_field: 'customer_id', inverse_name: 'customer.orders', description: '下单' },
      { name: 'risk_customer.belongs_to_group', source_type: 'risk_customer', target_type: 'group_customer', cardinality: 'N:1', fk_field: 'group_customer_no', inverse_name: 'group_customer.risk_customers', description: '归属集团' },
      { name: 'warning.for_customer', source_type: 'warning_signal', target_type: 'risk_customer', cardinality: 'N:1', fk_field: 'customer_no', inverse_name: 'risk_customer.warnings', description: '预警客户' },
    ],
  },
};

beforeEach(() => {
  mockFetch.mockReset();
  mockFetch.mockResolvedValue({
    ok: true,
    json: () => Promise.resolve(graphResponse),
  });
});

describe('GraphPage', () => {
  it('渲染聚合图谱容器（数据来自 builder 图谱端点，不经 /meta/schema）', async () => {
    render(<GraphPage />);
    await waitFor(() => {
      expect(screen.getByTestId('schema-graph')).toBeTruthy();
    });
    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toContain('/api/v1/builder/graph');
    expect(url).not.toContain('/meta/schema');
  });

  it('请求失败时显示错误提示', async () => {
    mockFetch.mockReset();
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ request_id: 'x', outcome: 'error', error: { code: 'E', message: '图谱加载失败' } }),
    });
    render(<GraphPage />);
    await waitFor(() => {
      expect(screen.getByText(/图谱加载失败/)).toBeTruthy();
    });
  });
});
