import { afterEach, describe, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import App from '../App';

afterEach(cleanup); // vitest 未开 globals：显式清理，避免跨用例 DOM 叠加

/** T4 核心不变量：刷新恢复（快照渲染）/ client_request_id 幂等重试 / 归档与恢复。 */

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

  it('归档：菜单归档 → 主列表消失、归档区出现；恢复 → 回到主列表（PATCH archived）', async () => {
    let sess = [sessionRaw('s1', '会话A'), sessionRaw('s2', '会话B')];
    let arch: ReturnType<typeof sessionRaw>[] = [];
    const patches: Record<string, unknown>[] = [];
    const handlers: Handler[] = [
      (u) => (u === '/api/profile' ? jsonResponse(PROFILE) : undefined),
      (u) => (u === '/api/sessions' ? jsonResponse(sess) : undefined),
      (u) => (u === '/api/sessions?archived=1' ? jsonResponse(arch) : undefined),
      (u, i) => {
        // PATCH 必须排在 GET /api/sessions/s1 之前（handler 顺序匹配，GET 分支不区分 method）
        if (u === '/api/sessions/s1' && i?.method === 'PATCH') {
          const body = JSON.parse(String(i.body)) as Record<string, unknown>;
          patches.push(body);
          if (body['archived'] === true) {
            sess = sess.filter((s) => s.id !== 's1');
            arch = [sessionRaw('s1', '会话A')];
          } else if (body['archived'] === false) {
            arch = [];
            sess = [sessionRaw('s1', '会话A'), sessionRaw('s2', '会话B')];
          }
          return jsonResponse(sessionRaw('s1', '会话A'));
        }
        return undefined;
      },
      (u) => (u === '/api/sessions/s1' ? jsonResponse({ conversation: sessionRaw('s1', '会话A'), messages: [] }) : undefined),
    ];
    stubFetch(handlers);

    render(<App />);
    expect(await screen.findByText('会话A')).toBeTruthy();

    // ⋯ 菜单 → 归档
    fireEvent.click(screen.getAllByRole('button', { name: '更多操作' })[0]);
    fireEvent.click(screen.getByText('归档'));
    expect(await screen.findByText(/已归档 · 1/)).toBeTruthy();
    await waitFor(() => expect(screen.queryByText('会话A')).toBeNull()); // 主列表消失

    // 展开归档区 → 恢复
    fireEvent.click(screen.getByText(/已归档 · 1/));
    fireEvent.click(screen.getByTitle('恢复到会话列表'));
    await screen.findByText('会话A');
    expect(patches[0]).toEqual({ archived: true });
    expect(patches[1]).toEqual({ archived: false });
  });
});