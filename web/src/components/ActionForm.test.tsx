/// <reference types="vitest/globals" />
// ActionForm 组件测试 —— 验证 schema 驱动表单生成
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import ActionForm from './ActionForm';
import type { ActionMeta } from '../types';

const mockFetch = vi.fn();
(globalThis as typeof globalThis & { fetch: typeof mockFetch }).fetch = mockFetch;

const mockAction: ActionMeta = {
  name: 'cancel_order',
  description: '取消订单',
  high_risk: false,
  params_schema: {
    type: 'object',
    properties: {
      order_id: { type: 'string', title: '订单号' },
      reason: { type: 'string', title: '取消原因' },
    },
    required: ['order_id'],
  },
  preconditions: [
    { error_code: 'ORDER_NOT_FOUND', summary: '订单存在' },
  ],
  error_codes: ['ORDER_NOT_FOUND', 'ORDER_NOT_CANCELLABLE'],
  state_effects: {
    source_backed: ['Order.status'],
    ontology_owned: ['Order.cancel_reason'],
  },
};

const mockHighRiskAction: ActionMeta = {
  ...mockAction,
  name: 'approve_refund',
  description: '审核退款',
  high_risk: true,
};

beforeEach(() => {
  mockFetch.mockReset();
});

describe('ActionForm', () => {
  it('renders form fields from params_schema', () => {
    const onDone = vi.fn();
    render(<ActionForm action={mockAction} onDone={onDone} />);

    expect(screen.getByText('订单号')).toBeTruthy();
    expect(screen.getByText('取消原因')).toBeTruthy();
  });

  it('renders description text', () => {
    const onDone = vi.fn();
    render(<ActionForm action={mockAction} onDone={onDone} />);

    expect(screen.getByText('取消订单')).toBeTruthy();
  });

  it('renders preconditions as alert', () => {
    const onDone = vi.fn();
    render(<ActionForm action={mockAction} onDone={onDone} />);

    expect(screen.getByText('前置规则')).toBeTruthy();
    expect(screen.getByText(/订单存在/)).toBeTruthy();
  });

  it('shows high risk tag for high risk actions', () => {
    const onDone = vi.fn();
    render(<ActionForm action={mockHighRiskAction} onDone={onDone} />);

    expect(screen.getByText('高风险')).toBeTruthy();
  });

  it('renders execute button', () => {
    const onDone = vi.fn();
    render(<ActionForm action={mockAction} onDone={onDone} />);

    expect(screen.getByText(/执.*行.*动.*作/)).toBeTruthy();
  });

  it('renders reset button', () => {
    const onDone = vi.fn();
    render(<ActionForm action={mockAction} onDone={onDone} />);

    // Ant Design inserts zero-width spaces in Chinese text buttons
    expect(screen.getByText(/重.*置/)).toBeTruthy();
  });
});
