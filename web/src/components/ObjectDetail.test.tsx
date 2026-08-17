/// <reference types="vitest/globals" />
// ObjectDetail 组件测试 —— 验证属性渲染 + 链接导航
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import ObjectDetail from './ObjectDetail';
import type { ObjectTypeMeta } from '../types';

const mockFetch = vi.fn();
(globalThis as typeof globalThis & { fetch: typeof mockFetch }).fetch = mockFetch;

const mockMeta: ObjectTypeMeta = {
  name: 'Order',
  api_name: 'order',
  description: '订单',
  pk_field: 'order_id',
  title_field: 'order_id',
  source_table: 'orders',
  properties: {
    order_id: { type: 'string', title: '订单号' },
    status: { type: 'string', title: '状态' },
    total_cents: { type: 'integer', title: '金额（分）' },
  },
};

const mockDetail = {
  outcome: 'ok',
  data: {
    object_type: 'Order',
    pk: 'ORD001',
    properties: {
      order_id: 'ORD001',
      status: 'pending',
      total_cents: 10000,
      customer_id: 'C001',
    },
    links: {
      'order.customer': 1,
      'order.items': 3,
      'order.shipments': 0,
    },
  },
};

beforeEach(() => {
  mockFetch.mockReset();
  mockFetch.mockResolvedValue({
    ok: true,
    json: () => Promise.resolve(mockDetail),
  });
});

describe('ObjectDetail', () => {
  it('renders all properties from schema', async () => {
    const onNav = vi.fn();
    const onBack = vi.fn();
    render(
      <ObjectDetail meta={mockMeta} pk="ORD001" onNavigateLink={onNav} onBack={onBack} />,
    );

    await waitFor(() => {
      expect(screen.getByText('ORD001')).toBeTruthy();
      expect(screen.getByText('pending')).toBeTruthy();
    });
  });

  it('renders link navigation buttons', async () => {
    const onNav = vi.fn();
    const onBack = vi.fn();
    render(
      <ObjectDetail meta={mockMeta} pk="ORD001" onNavigateLink={onNav} onBack={onBack} />,
    );

    await waitFor(() => {
      expect(screen.getByText(/order\.customer/)).toBeTruthy();
      expect(screen.getByText(/order\.items/)).toBeTruthy();
    });
  });

  it('calls onNavigateLink when link button clicked', async () => {
    const onNav = vi.fn();
    const onBack = vi.fn();
    render(
      <ObjectDetail meta={mockMeta} pk="ORD001" onNavigateLink={onNav} onBack={onBack} />,
    );

    await waitFor(() => {
      const btn = screen.getByText(/order\.customer/);
      btn.click();
      expect(onNav).toHaveBeenCalledWith('order', 'ORD001', 'order.customer');
    });
  });

  it('calls onBack when back button clicked', async () => {
    const onNav = vi.fn();
    const onBack = vi.fn();
    render(
      <ObjectDetail meta={mockMeta} pk="ORD001" onNavigateLink={onNav} onBack={onBack} />,
    );

    await waitFor(() => {
      const btn = screen.getByText('返回列表');
      btn.click();
      expect(onBack).toHaveBeenCalled();
    });
  });
});
