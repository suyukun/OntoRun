/// <reference types="vitest/globals" />
// BrowsePage 冒烟：/meta/schema 驱动对象类型侧栏 + 对象列表渲染
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import BrowsePage from './BrowsePage';
import { MetaProvider } from '../context/MetaContext';

const mockFetch = vi.fn();
(globalThis as typeof globalThis & { fetch: typeof mockFetch }).fetch = mockFetch;

const schemaResponse = {
  request_id: 'req_meta',
  outcome: 'ok',
  data: {
    objects: [
      {
        name: 'Order',
        api_name: 'order',
        description: '订单',
        pk_field: 'order_id',
        title_field: 'order_id',
        source_table: 'orders',
        properties: {
          order_id: { type: 'string', title: '订单号' },
          status: { type: 'string', title: '状态', enum: ['pending', 'shipped'] },
        },
      },
    ],
    links: [
      { name: 'order.customer', source_type: 'Order', target_type: 'Customer', cardinality: 'N:1', fk_field: 'customer_id', inverse_name: 'customer.orders', description: '下单' },
    ],
    actions: [
      { name: 'cancel_order', description: '取消订单', high_risk: false, params_schema: { type: 'object', properties: { order_id: { type: 'string' } }, required: ['order_id'] }, preconditions: [], error_codes: [], state_effects: { source_backed: [], ontology_owned: [] } },
    ],
  },
};

beforeEach(() => {
  mockFetch.mockReset();
  mockFetch.mockResolvedValueOnce({
    ok: true,
    json: () => Promise.resolve(schemaResponse),
  });
  mockFetch.mockResolvedValue({
    ok: true,
    json: () =>
      Promise.resolve({
        request_id: 'req_list',
        outcome: 'ok',
        data: {
          type: 'order',
          page: 1,
          page_size: 20,
          total: 1,
          items: [
            {
              object_type: 'Order',
              pk: 'ORD001',
              properties: { order_id: 'ORD001', status: 'pending' },
            },
          ],
        },
      }),
  });
});

describe('BrowsePage', () => {
  it('渲染对象类型侧栏（schema 驱动）', async () => {
    render(
      <MetaProvider>
        <BrowsePage />
      </MetaProvider>,
    );
    await waitFor(() => {
      expect(screen.getByText(/订单/)).toBeTruthy();
    });
    // 侧栏标题（对象类型）存在
    expect(screen.getByText('对象类型')).toBeTruthy();
  });

  it('点击对象类型渲染对象列表（schema 列）', async () => {
    render(
      <MetaProvider>
        <BrowsePage />
      </MetaProvider>,
    );
    await waitFor(() => {
      const item = screen.getByText(/订单/);
      item.click();
    });
    await waitFor(() => {
      expect(screen.getByText('订单号')).toBeTruthy();
      expect(screen.getByText('ORD001')).toBeTruthy();
    });
  });
});