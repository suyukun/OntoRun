/// <reference types="vitest/globals" />
// LinkNav 组件测试 —— TD-14 修复：请求名必须与方向匹配（out=name / in=inverse_name）
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import LinkNav from './LinkNav';
import type { LinkTypeMeta, ObjectTypeMeta } from '../types';

const mockFetch = vi.fn();
(globalThis as typeof globalThis & { fetch: typeof mockFetch }).fetch = mockFetch;

const sourceMeta: ObjectTypeMeta = {
  name: 'Order',
  api_name: 'order',
  description: '订单',
  pk_field: 'order_id',
  title_field: 'order_id',
  source_table: 'orders',
  properties: { order_id: { type: 'string', title: '订单号' } },
};
const customerMeta: ObjectTypeMeta = {
  name: 'Customer',
  api_name: 'customer',
  description: '客户',
  pk_field: 'customer_id',
  title_field: 'customer_id',
  source_table: 'customers',
  properties: { customer_id: { type: 'string', title: '客户号' } },
};
const objectTypes = [sourceMeta, customerMeta];

const links: LinkTypeMeta[] = [
  {
    name: 'order.customer',
    source_type: 'Order',
    target_type: 'Customer',
    cardinality: 'N:1',
    fk_field: 'customer_id',
    inverse_name: 'customer.orders',
    description: '下单：一个订单属于一个客户',
  },
];

function okBody(linkName: string, direction: string, objects: unknown[]) {
  return {
    ok: true,
    json: () => Promise.resolve({ outcome: 'ok', data: { link_name: linkName, direction, objects } }),
  };
}

const noop = () => {};

function renderLinkNav(linkName: string) {
  return render(
    <LinkNav
      sourceType={sourceMeta}
      sourcePk="ORD-1"
      linkName={linkName}
      links={links}
      objectTypes={objectTypes}
      onSelectObject={noop}
      onBack={noop}
    />,
  );
}

function lastUrl(): string {
  const calls = mockFetch.mock.calls;
  return calls[calls.length - 1][0] as string;
}

describe('LinkNav 链接遍历方向（TD-14）', () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  it('正向链接名 + 初始 out → 请求正向名 + out', async () => {
    mockFetch.mockResolvedValue(okBody('order.customer', 'out', []));
    renderLinkNav('order.customer');
    await waitFor(() => {
      expect(lastUrl()).toContain('/objects/order/ORD-1/links/order.customer?direction=out');
    });
  });

  it('点「反向」→ 请求反向名 + in（此前 404）', async () => {
    mockFetch.mockResolvedValue(okBody('order.customer', 'out', []));
    renderLinkNav('order.customer');
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalled();
    });
    mockFetch.mockResolvedValue(okBody('customer.orders', 'in', []));
    const rev = screen.getByRole('button', { name: /反\s*向/ });
    rev.click();
    await waitFor(() => {
      expect(lastUrl()).toContain('/objects/order/ORD-1/links/customer.orders?direction=in');
    });
  });

  it('入向链接名打开（初始 out）→ 请求正向名 + out（此前 404）', async () => {
    mockFetch.mockResolvedValue(okBody('order.customer', 'out', []));
    renderLinkNav('customer.orders');
    await waitFor(() => {
      expect(lastUrl()).toContain('/objects/order/ORD-1/links/order.customer?direction=out');
    });
  });
});
