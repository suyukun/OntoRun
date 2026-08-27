/// <reference types="vitest/globals" />
// RiskChatPanel 冒烟测试 —— 精准问答 / 双签确认 / 域外拒答
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import RiskChatPanel from './RiskChatPanel';
import { miniSnapshot } from './testFixtures';

const mockFetch = vi.fn();
(globalThis as typeof globalThis & { fetch: typeof mockFetch }).fetch = mockFetch;

function ok(body: unknown) {
  return Promise.resolve({ ok: true, json: () => Promise.resolve(body) });
}
let chatCalls: { path: string; body: unknown }[] = [];

beforeEach(() => {
  mockFetch.mockReset();
  chatCalls = [];
  mockFetch.mockImplementation((url: string, init?: RequestInit) => {
    if (url === '/risk-demo/risk-snapshot.json') {
      return ok(miniSnapshot);
    }
    if (url === '/api/agent/risk/chat') {
      chatCalls.push({ path: url, body: JSON.parse(String(init?.body ?? '{}')) });
      return ok(chatResponse);
    }
    if (url === '/api/agent/risk/confirm') {
      chatCalls.push({ path: url, body: JSON.parse(String(init?.body ?? '{}')) });
      return ok(confirmResponse);
    }
    return Promise.reject(new Error('unhandled ' + url));
  });
  localStorage.clear();
});

let chatResponse: unknown = { session_id: 'sess_001', reply: '' };
let confirmResponse: unknown = { reply: '', outcome: 'applied' };

describe('RiskChatPanel', () => {
  it('渲染初始空态与示例问题引导', () => {
    render(<RiskChatPanel />);
    expect(screen.getByText('风险对话 · 人机双签')).toBeTruthy();
    expect(screen.getByText('本月红色预警')).toBeTruthy();
    expect(screen.getByPlaceholderText(/输入风险问题或指令/)).toBeTruthy();
  });

  it('发送问题并展示 AI 回复（走 /agent/risk/chat）', async () => {
    chatResponse = { session_id: 'sess_001', reply: '本月新增红色预警信号共 86 条。' };
    const user = userEvent.setup();
    render(<RiskChatPanel />);
    await user.type(screen.getByPlaceholderText(/输入风险问题或指令/), '本月红色预警几条？');
    await user.click(screen.getByRole('button', { name: /发送/ }));

    await waitFor(() => {
      expect(chatCalls.some((c) => c.path === '/api/agent/risk/chat' && (c.body as { message: string }).message === '本月红色预警几条？')).toBe(true);
    });
    await waitFor(() => {
      expect(screen.getByText('本月新增红色预警信号共 86 条。')).toBeTruthy();
    });
  });

  it('高风险动作返回 need_confirm → 展示双签卡片 → 确认后调 /agent/risk/confirm', async () => {
    chatResponse = {
      session_id: 'sess_002',
      reply: '系统提议调整预警等级。',
      need_confirm: { id: 'call_001', name: 'adjust_warning_level', arguments: { warning_id: 'WS-2026-00000129', new_level: 'RED', reason: '押品贬值超过预警阈值' } },
    };
    confirmResponse = { reply: '预警等级调整已成功执行', outcome: 'applied' };
    const user = userEvent.setup();
    render(<RiskChatPanel />);

    await user.click(screen.getByRole('button', { name: /等级调整 Y→R（双签）/ }));
    await waitFor(() => {
      expect(screen.getByText('高风险动作 · 人机双签')).toBeTruthy();
    });
    expect(screen.getAllByText('adjust_warning_level').length).toBeGreaterThan(0);
    expect(screen.getByRole('button', { name: /确认执行/ })).toBeTruthy();
    expect(screen.getByRole('button', { name: /驳回/ })).toBeTruthy();

    await user.click(screen.getByRole('button', { name: /确认执行/ }));
    await waitFor(() => {
      expect(chatCalls.some((c) => c.path === '/api/agent/risk/confirm' && (c.body as { confirmed: boolean }).confirmed === true)).toBe(true);
    });
    await waitFor(() => {
      expect(screen.getByText(/已执行/)).toBeTruthy();
    });
  });

  it('驳回双签 → 调用 confirm(confirmed=false) 且不执行', async () => {
    chatResponse = {
      session_id: 'sess_003',
      reply: '系统提议调整预警等级。',
      need_confirm: { id: 'call_002', name: 'adjust_warning_level', arguments: { warning_id: 'WS-2026-00000129', new_level: 'RED' } },
    };
    confirmResponse = { reply: '已驳回，未执行', outcome: 'cancelled_by_user' };
    const user = userEvent.setup();
    render(<RiskChatPanel />);

    await user.click(screen.getByRole('button', { name: /等级调整 Y→R（双签）/ }));
    await waitFor(() => expect(screen.getByText('高风险动作 · 人机双签')).toBeTruthy());
    await user.click(screen.getByRole('button', { name: /驳回/ }));
    await waitFor(() => {
      expect(chatCalls.some((c) => c.path === '/api/agent/risk/confirm' && (c.body as { confirmed: boolean }).confirmed === false)).toBe(true);
    });
    await waitFor(() => {
      expect(screen.getByText(/已驳回，未执行任何写回/)).toBeTruthy();
    });
  });

  it('域外问题 → 明确拒答展示（fail-closed）', async () => {
    chatResponse = {
      session_id: 'sess_004',
      reply: 'DECLINE\n很抱歉，资本充足率计算超出系统可表达集，无法回答。我可以帮您查询：①集团客户信息 ②集中度限额。',
    };
    const user = userEvent.setup();
    render(<RiskChatPanel />);
    await user.click(screen.getByRole('button', { name: /巴塞尔资本充足率（拒答）/ }));
    await waitFor(() => {
      expect(screen.getByText(/超出系统可答范围（fail-closed 拒答）/)).toBeTruthy();
    });
    expect(screen.getByText(/资本充足率计算超出系统可表达集/)).toBeTruthy();
  });

  it('会话消息持久化（localStorage）', async () => {
    chatResponse = { session_id: 'sess_005', reply: '持久化测试回复。' };
    const user = userEvent.setup();
    render(<RiskChatPanel />);
    await user.type(screen.getByPlaceholderText(/输入风险问题或指令/), '持久化问题');
    await user.click(screen.getByRole('button', { name: /发送/ }));
    await waitFor(() => expect(screen.getByText('持久化测试回复。')).toBeTruthy());
    const saved = JSON.parse(localStorage.getItem('ontorun.risk.messages') || '[]');
    expect(saved.some((m: { content: string }) => m.content === '持久化问题')).toBe(true);
  });
});

