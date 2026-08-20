/// <reference types="vitest/globals" />
// ChatPanel 组件测试 —— 验证 /agent/chat 和 /agent/confirm 交互
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ChatPanel from './ChatPanel';

const mockFetch = vi.fn();
(globalThis as typeof globalThis & { fetch: typeof mockFetch }).fetch = mockFetch;

beforeEach(() => {
  mockFetch.mockReset();
  localStorage.clear();
});

// Ant Design inserts zero-width spaces in Chinese text buttons
const sendBtn = () => screen.getByRole('button', { name: /发.*送/ });
const rejectBtn = () => screen.getByRole('button', { name: /拒.*绝/ });

describe('ChatPanel', () => {
  it('renders initial empty state', () => {
    render(<ChatPanel />);

    expect(screen.getByText('AI 助手')).toBeTruthy();
    expect(screen.getByPlaceholderText('输入消息...')).toBeTruthy();
    expect(sendBtn()).toBeTruthy();
  });

  it('sends message and displays reply', async () => {
    const user = userEvent.setup();

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({
          session_id: 'sess_001',
          reply: '你好！我可以帮你查询订单信息。',
        }),
    });

    render(<ChatPanel />);

    const input = screen.getByPlaceholderText('输入消息...');
    await user.type(input, '查询订单');
    await user.click(sendBtn());

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        '/api/agent/chat',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ message: '查询订单' }),
        }),
      );
    });

    await waitFor(() => {
      expect(screen.getByText('你好！我可以帮你查询订单信息。')).toBeTruthy();
    });
  });

  it('shows confirm buttons when need_confirm is returned', async () => {
    const user = userEvent.setup();

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({
          session_id: 'sess_002',
          need_confirm: {
            id: 'call_001',
            name: 'approve_refund',
            arguments: { refund_id: 'REF001', approved: true },
          },
        }),
    });

    render(<ChatPanel />);

    await user.type(screen.getByPlaceholderText('输入消息...'), '批准退款');
    await user.click(sendBtn());

    await waitFor(() => {
      expect(screen.getByText('确认执行')).toBeTruthy();
      expect(rejectBtn()).toBeTruthy();
    });
  });

  it('calls /agent/confirm when confirm button clicked', async () => {
    const user = userEvent.setup();

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({
          session_id: 'sess_003',
          need_confirm: {
            id: 'call_002',
            name: 'approve_refund',
            arguments: { refund_id: 'REF001', approved: true },
          },
        }),
    });

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({
          reply: '退款已批准',
          outcome: 'applied',
        }),
    });

    render(<ChatPanel />);

    await user.type(screen.getByPlaceholderText('输入消息...'), '批准退款');
    await user.click(sendBtn());

    await waitFor(() => {
      expect(screen.getByText('确认执行')).toBeTruthy();
    });

    await user.click(screen.getByText('确认执行'));

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        '/api/agent/confirm',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            session_id: 'sess_003',
            call_id: 'call_002',
            confirmed: true,
          }),
        }),
      );
    });
  });

  it('handles reject button', async () => {
    const user = userEvent.setup();

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({
          session_id: 'sess_004',
          need_confirm: {
            id: 'call_003',
            name: 'approve_refund',
            arguments: { refund_id: 'REF001', approved: true },
          },
        }),
    });

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({
          reply: '已取消该操作',
          outcome: 'cancelled',
        }),
    });

    render(<ChatPanel />);

    await user.type(screen.getByPlaceholderText('输入消息...'), '批准退款');
    await user.click(sendBtn());

    await waitFor(() => {
      expect(rejectBtn()).toBeTruthy();
    });

    await user.click(rejectBtn());

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        '/api/agent/confirm',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            session_id: 'sess_004',
            call_id: 'call_003',
            confirmed: false,
          }),
        }),
      );
    });
  });

  it('restores messages and session from localStorage (TD-15)', () => {
    localStorage.setItem(
      'ontorun.chat.messages',
      JSON.stringify([
        { role: 'user', content: '之前的消息' },
        { role: 'assistant', content: '之前的回复' },
      ]),
    );
    localStorage.setItem('ontorun.chat.sessionId', 'sess_prev');

    render(<ChatPanel />);

    expect(screen.getByText('之前的消息')).toBeTruthy();
    expect(screen.getByText('之前的回复')).toBeTruthy();
  });
});
