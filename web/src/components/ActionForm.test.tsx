/// <reference types="vitest/globals" />
// ActionForm 组件测试 —— 验证 schema 驱动表单生成 + 提交结果展示
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
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

    expect(screen.getByText(/重.*置/)).toBeTruthy();
  });

  it('shows success result after submit returns applied', async () => {
    const user = userEvent.setup();
    const onDone = vi.fn();

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({
          request_id: 'req_001',
          outcome: 'applied',
          data: {
            audit_id: 'audit_abc123',
            action_name: 'cancel_order',
            effects: [],
            request_id: 'req_001',
          },
        }),
    });

    render(<ActionForm action={mockAction} onDone={onDone} />);

    await user.type(
      screen.getByPlaceholderText('订单号'),
      'ORD001',
    );
    await user.click(screen.getByText(/执.*行.*动.*作/));

    await waitFor(() => {
      // 后端 POST /actions/cancel_order
      expect(mockFetch).toHaveBeenCalledWith(
        '/api/actions/cancel_order',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({ 'X-Actor': 'api' }),
          body: JSON.stringify({ order_id: 'ORD001' }),
        }),
      );
    });

    await waitFor(() => {
      expect(screen.getByText(/动作执行成功/)).toBeTruthy();
      expect(screen.getByText(/audit_abc123/)).toBeTruthy();
    });

    // onDone 被调用
    await waitFor(() => {
      expect(onDone).toHaveBeenCalled();
    });
  });

  it('shows error when submit returns rejected', async () => {
    const user = userEvent.setup();
    const onDone = vi.fn();

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({
          request_id: 'req_002',
          outcome: 'rejected',
          error: {
            code: 'ORDER_NOT_CANCELLABLE',
            message: '订单不可取消',
          },
        }),
    });

    render(<ActionForm action={mockAction} onDone={onDone} />);

    await user.type(
      screen.getByPlaceholderText('订单号'),
      'ORD002',
    );
    await user.click(screen.getByText(/执.*行.*动.*作/));

    await waitFor(() => {
      expect(screen.getByText(/被拒绝/)).toBeTruthy();
      expect(screen.getByText(/订单不可取消/)).toBeTruthy();
    });
  });
});
