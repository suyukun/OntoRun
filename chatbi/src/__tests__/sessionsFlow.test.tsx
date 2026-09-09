import { afterEach, describe, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import App from '../App';

afterEach(cleanup); // vitest 未开 globals：显式清理，避免跨用例 DOM 叠加

/** T4 核心不变量：刷新恢复（快照渲染）/ client_request_id 幂等重试 / 历史回放与 404。 */

const PROFILE = {
  name: 'fortune-registration',
  display: '财富广场 · 注册域',
  endpoint: '/api/chat',
  panels: [],
  examples: [],
  path_labels: {},
};

const SNAPSHOT = {
  request_id: 'REQ-SNAPSHOT-1',
  started_at: '2026-09-10T08:00:00',
  question: '8月注册用户数是多少？',
  rule: 'REG_TOTAL',
  path: 'hot',
  answer: '存量回答：2,893 人',
  sql: null,
  rows: [{ 渠道: 'A', 用户数: 100 }],
  tables: [],
  steps: [{ n: 1, title: '意图路由', status: 'ok', detail: 'x' }],
};

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
}

function sseResponse(frames: unknown[]): Response {
  const payload = frames.map((f) => 'data: ' + JSON.stringify(f) + '\n\n').join('');
  return new Response(new ReadableStream({ start(c) { c.enqueue(new TextEncoder().encode(payload)); c.close(); } }), { status: 200 });
}

function sessionRaw(id: string, title: string) {
  return { id, title, pinned: 0, starred: 0, created_at: '2026-09-10T08:00:00', updated_at: '2026-09-10T08:00:00' };
}

type Handler = (url: string, init: RequestInit | undefined) => Response | undefined;

function stubFetch(handlers: Handler[]): { bodies: Record<string, unknown>[] } {
  const bodies: Record<string, unknown>[] = [];
  const fn = vi.fn((url: string, init?: RequestInit) => {
    for (const h of handlers) {
      const r = h(url, init);
      if (r) return r;
    }
    return jsonResponse({ detail: 'no route' }, 404);
  }) as unknown as typeof fetch;
  const orig = fn as unknown as { __bodies?: Record<string, unknown>[] };
  orig.__bodies = bodies;
  vi.stubGlobal('fetch', vi.fn(((u: string, i?: RequestInit) => {
    const resp = (fn as unknown as (u: string, i?: RequestInit) => Response)(u, i);
    if (u.includes('/api/chat') && i?.body) bodies.push(JSON.parse(String(i.body)));
    return Promise.resolve(resp);
  }) as typeof fetch));
  return { bodies };
}

const sseFinal = (result: Record<string, unknown>) => sseResponse([{ kind: 'final', result }]);

describe('T4 会话恢复与持久化联调', () => {
  it('刷新恢复：服务端消息快照直接渲染（未重新执行），查询携带 conversation_id + client_request_id', async () => {
    const handlers: Handler[] = [
      (u) => (u === '/api/profile' ? jsonResponse(PROFILE) : undefined),
      (u) => (u === '/api/sessions' ? jsonResponse([sessionRaw('s1', '存量会话')]) : undefined),
      (u) =>
        u === '/api/sessions/s1'
          ? jsonResponse({
              conversation: sessionRaw('s1', '存量会话'),
              messages: [
                { id: 'm1', conversation_id: 's1', role: 'user', question: SNAPSHOT.question, request_id: null, state: null, answer: null, result: null, created_at: '2026-09-10T08:00:00' },
                { id: 'm2', conversation_id: 's1', role: 'assistant', question: SNAPSHOT.question, request_id: SNAPSHOT.request_id, state: 'success', answer: SNAPSHOT.answer, result: SNAPSHOT, created_at: '2026-09-10T08:00:01' },
              ],
            })
          : undefined,
      (u, i) => (u === '/api/chat' && i?.method === 'POST' ? sseFinal({ ...SNAPSHOT, request_id: 'REQ-NEW-1', answer: '新回答：2,893 人' }) : undefined),
    ];
    const { bodies } = stubFetch(handlers);

    render(<App />);
    // 刷新恢复：不发问即见快照回答 + 数据表格（快照渲染，非重新执行）
    expect(await screen.findByText('存量回答：2,893 人')).toBeTruthy();
    expect(screen.getByRole('table')).toBeTruthy();

    fireEvent.change(screen.getByPlaceholderText('输入问题…'), { target: { value: '9月注册用户数是多少？' } });
    fireEvent.click(screen.getByRole('button', { name: '发送' }));
    await screen.findByText('新回答：2,893 人');

    expect(bodies.length).toBe(1);
    expect(bodies[0]['conversation_id']).toBe('s1');
    expect(typeof bodies[0]['client_request_id']).toBe('string');
    expect(bodies[0]['client_request_id']).not.toBe('');
  });

  it('幂等重试：失败后点重试复用同一 client_request_id（附录 A）', async () => {
    const handlers: Handler[] = [
      (u) => (u === '/api/profile' ? jsonResponse(PROFILE) : undefined),
      (u) => (u === '/api/sessions' ? jsonResponse([sessionRaw('s1', '存量会话')]) : undefined),
      (u) => (u === '/api/sessions/s1' ? jsonResponse({ conversation: sessionRaw('s1', '存量会话'), messages: [] }) : undefined),
      (u, i) => (u === '/api/chat' && i?.method === 'POST' ? jsonResponse({ detail: 'down' }, 500) : undefined),
    ];
    const { bodies } = stubFetch(handlers);

    render(<App />);
    fireEvent.change(await screen.findByPlaceholderText('输入问题…'), { target: { value: '8月注册用户数是多少？' } });
    fireEvent.click(screen.getByRole('button', { name: '发送' }));

    fireEvent.click(await screen.findByRole('button', { name: '重试' }));
    await waitFor(() => expect(bodies.length).toBe(2));
    expect(bodies[0]['client_request_id']).toBe(bodies[1]['client_request_id']);
  });

  it('历史回放：列表点击 → 快照渲染为消息卡（标注数据截至）；已删条目 404 友好提示', async () => {
    const okTrace = { ...SNAPSHOT, request_id: 'REQ-OK', started_at: '2026-09-10T07:30:00', answer: '回放回答：2,893 人', question: '可回放的问题' };
    const handlers: Handler[] = [
      (u) => (u === '/api/profile' ? jsonResponse(PROFILE) : undefined),
      (u) => (u === '/api/sessions' ? jsonResponse([]) : undefined),
      (u, i) => (u === '/api/sessions' && i?.method === 'POST' ? jsonResponse(sessionRaw('s-new', '新对话')) : undefined),
      (u) => (u === '/api/sessions/s-new' ? jsonResponse({ conversation: sessionRaw('s-new', '新对话'), messages: [] }) : undefined),
      (u) =>
        u === '/api/history'
          ? jsonResponse([
              { request_id: 'REQ-GONE', started_at: '2026-09-10T07:00:00', question: '已删条目的问题', path: 'hot', state: 'success', answer: 'a' },
              { request_id: 'REQ-OK', started_at: '2026-09-10T07:30:00', question: '可回放的问题', path: 'hot', state: 'success', answer: '回放回答' },
            ])
          : undefined,
      (u) => (u === '/api/trace/REQ-GONE' ? jsonResponse({ detail: 'trace not found' }, 404) : undefined),
      (u) => (u === '/api/trace/REQ-OK' ? jsonResponse(okTrace) : undefined),
    ];
    stubFetch(handlers);

    render(<App />);
    fireEvent.click(await screen.findByRole('button', { name: '查询历史' }));

    // 已删条目 → 404 友好提示
    fireEvent.click(await screen.findByText('已删条目的问题'));
    expect(await screen.findByText('该条记录已删除或不存在，无法回放。')).toBeTruthy();

    // 返回列表 → 正常条目 → 快照回放为消息卡 + 数据截至标注
    fireEvent.click(screen.getByRole('button', { name: '返回历史列表' }));
    fireEvent.click(screen.getByText('可回放的问题'));
    expect(await screen.findByText(/历史回放 · 数据截至 2026-09-10 07:30:00/)).toBeTruthy();
    expect(await screen.findByText('回放回答：2,893 人')).toBeTruthy();
  });
});