/// <reference types="vitest/globals" />
// ObjectTypesPage 冒烟：builder 列表渲染 + 状态标签 + 新建入口
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import ObjectTypesPage from './ObjectTypesPage';
import type { ObjectTypeRow } from '../../builderTypes';
import type { PropertySchema } from '../../builderTypes';

const mockFetch = vi.fn();
(globalThis as typeof globalThis & { fetch: typeof mockFetch }).fetch = mockFetch;

const rows: ObjectTypeRow[] = [
  {
    id: 'ot_1',
    ontology_id: 'default',
    name: 'Supplier',
    name_cn: '供应商',
    description: '供应商主数据',
    category: 'domain',
    property_schema: {
      type: 'object',
      properties: { supplier_id: { type: 'string', title: '供应商号' } },
      required: ['supplier_id'],
    } as PropertySchema,
    status: 'published',
    pk_field: 'supplier_id',
    title_field: 'supplier_id',
    source_table: '',
    api_name: 'supplier',
    created_at: '2025-01-01 00:00:00',
    updated_at: '2025-01-01 00:00:00',
  },
  {
    id: 'ot_2',
    ontology_id: 'default',
    name: 'PurchaseOrder',
    name_cn: '采购单',
    description: '采购单',
    category: 'artifact',
    property_schema: {
      type: 'object',
      properties: { po_id: { type: 'string', title: '采购单号' } },
      required: ['po_id'],
    } as PropertySchema,
    status: 'draft',
    pk_field: 'po_id',
    title_field: 'po_id',
    source_table: '',
    api_name: 'purchase_order',
    created_at: '2025-01-02 00:00:00',
    updated_at: '2025-01-02 00:00:00',
  },
];

beforeEach(() => {
  mockFetch.mockReset();
  mockFetch.mockResolvedValue({
    ok: true,
    json: () =>
      Promise.resolve({
        request_id: 'req_test',
        outcome: 'ok',
        data: { items: rows, total: 2, page: 1, page_size: 20 },
      }),
  });
});

describe('ObjectTypesPage', () => {
  it('渲染 builder 对象类型列表（元数据驱动）', async () => {
    render(<ObjectTypesPage />);
    await waitFor(() => {
      expect(screen.getByText('Supplier')).toBeTruthy();
      expect(screen.getByText('PurchaseOrder')).toBeTruthy();
    });
    expect(screen.getByText('供应商')).toBeTruthy();
    // 状态标签：published（已发布）/ draft（草稿）
    expect(screen.getByText('已发布')).toBeTruthy();
    expect(screen.getByText('草稿')).toBeTruthy();
  });

  it('展示新建入口与操作列', async () => {
    render(<ObjectTypesPage />);
    await waitFor(() => expect(screen.getByText('Supplier')).toBeTruthy());
    expect(screen.getByText('新建')).toBeTruthy();
    // draft 行有审阅按钮，published 行无
    expect(screen.getAllByText(/编.*辑/).length).toBe(2);
  });

  it('请求正确的 builder 端点（/api/v1/builder/object-types）', async () => {
    render(<ObjectTypesPage />);
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/builder/object-types'),
        expect.any(Object),
      );
    });
  });
});