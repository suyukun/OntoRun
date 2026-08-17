/// <reference types="vitest/globals" />
// ObjectList 组件测试 —— 验证 schema 驱动列渲染
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import ObjectList from './ObjectList';
import type { ObjectTypeMeta } from '../types';

// Mock fetch
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
    status: { type: 'string', title: '状态', enum: ['pending', 'confirmed', 'shipped'] },
    total_cents: { type: 'integer', title: '金额（分）' },
    created_at: { type: 'string', title: '创建时间', format: 'date-time' },
  },
};

const mockResponse = {
  outcome: 'ok',
  data: {
    type: 'order',
    page: 1,
    page_size: 20,
    total: 2,
    items: [
      {
        object_type: 'Order',
        pk: 'ORD001',
        properties: {
          order_id: 'ORD001',
          status: 'pending',
          total_cents: 10000,
          created_at: '2025-01-01T00:00:00Z',
        },
      },
      {
        object_type: 'Order',
        pk: 'ORD002',
        properties: {
          order_id: 'ORD002',
          status: 'shipped',
          total_cents: 20000,
          created_at: '2025-01-02T00:00:00Z',
        },
      },
    ],
  },
};

beforeEach(() => {
  mockFetch.mockReset();
  mockFetch.mockResolvedValue({
    ok: true,
    json: () => Promise.resolve(mockResponse),
  });
});

describe('ObjectList', () => {
  it('renders table with schema-driven columns', async () => {
    const onSelect = vi.fn();
    render(<ObjectList meta={mockMeta} onSelectObject={onSelect} />);

    await waitFor(() => {
      expect(screen.getByText('订单号')).toBeTruthy();
      expect(screen.getByText('状态')).toBeTruthy();
      expect(screen.getByText('金额（分）')).toBeTruthy();
      expect(screen.getByText('创建时间')).toBeTruthy();
    });
  });

  it('renders object data from API', async () => {
    const onSelect = vi.fn();
    render(<ObjectList meta={mockMeta} onSelectObject={onSelect} />);

    await waitFor(() => {
      expect(screen.getByText('ORD001')).toBeTruthy();
      expect(screen.getByText('ORD002')).toBeTruthy();
    });
  });

  it('renders enum values as tags', async () => {
    const onSelect = vi.fn();
    render(<ObjectList meta={mockMeta} onSelectObject={onSelect} />);

    await waitFor(() => {
      expect(screen.getByText('pending')).toBeTruthy();
      expect(screen.getByText('shipped')).toBeTruthy();
    });
  });

  it('calls API with correct type', async () => {
    const onSelect = vi.fn();
    render(<ObjectList meta={mockMeta} onSelectObject={onSelect} />);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/objects/order'),
        expect.any(Object),
      );
    });
  });

  it('calls onSelectObject when row is clicked', async () => {
    const onSelect = vi.fn();
    render(<ObjectList meta={mockMeta} onSelectObject={onSelect} />);

    await waitFor(() => {
      const row = screen.getByText('ORD001');
      row.click();
      expect(onSelect).toHaveBeenCalledWith('order', 'ORD001');
    });
  });
});
