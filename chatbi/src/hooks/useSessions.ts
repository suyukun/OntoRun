import { useCallback, useEffect, useRef, useState } from 'react';
import type { ChatMessage, ServerMessage, ServerSession, SessionItem } from '../types';

/** 新对话默认标题（首问命名策略的判据） */
export const NEW_TITLE = '新对话';

const LOCAL_SEED_ID = 'local-0';

function toSession(raw: ServerSession): SessionItem {
  return { id: raw.id, title: raw.title, pinned: !!raw.pinned, starred: !!raw.starred };
}

async function listRemote(): Promise<SessionItem[]> {
  const resp = await fetch('/api/sessions');
  if (!resp.ok) throw new Error('HTTP ' + resp.status);
  const data = (await resp.json()) as unknown;
  if (!Array.isArray(data)) throw new Error('sessions 结构缺失');
  return (data as ServerSession[]).map(toSession);
}

async function createRemote(): Promise<SessionItem> {
  const resp = await fetch('/api/sessions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: NEW_TITLE }),
  });
  if (!resp.ok) throw new Error('HTTP ' + resp.status);
  return toSession((await resp.json()) as ServerSession);
}

async function patchRemote(id: string, fields: Partial<Pick<SessionItem, 'title' | 'pinned' | 'starred'>>): Promise<void> {
  const resp = await fetch('/api/sessions/' + id, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(fields),
  });
  if (!resp.ok) throw new Error('HTTP ' + resp.status);
}

/** 恢复消息流：assistant 消息直接用服务端 result 快照渲染（回放=快照，非重新执行，附录 D）。 */
export async function fetchMessages(sessionId: string): Promise<ChatMessage[]> {
  const resp = await fetch('/api/sessions/' + sessionId);
  if (!resp.ok) throw new Error('HTTP ' + resp.status);
  const data = (await resp.json()) as { messages?: ServerMessage[] };
  let id = 1;
  return (data.messages ?? []).map((m) => {
    const base = { id: id++, text: m.question ?? '', streamedText: '', error: null, phase: 'done' as const };
    if (m.role === 'user') return { ...base, role: 'user' as const, steps: [] as const, result: null };
    return {
      ...base,
      role: 'ai' as const,
      steps: m.result?.steps ?? [],
      result: m.result ?? null,
      endedBy: m.result ? ('final' as const) : ('error' as const),
    };
  });
}

export interface SessionsApi {
  sessions: SessionItem[];
  activeId: string | null;
  /** true = /api/sessions 可达（服务端为唯一事实源）；false = 后端未起，本地降级 */
  serverMode: boolean;
  select: (id: string) => void;
  create: () => Promise<void>;
  rename: (id: string, title: string) => Promise<void>;
  togglePin: (id: string) => Promise<void>;
  toggleStar: (id: string) => Promise<void>;
  remove: (id: string) => Promise<void>;
}

/** 会话栏状态（§3.5）：服务端 CRUD + 刷新恢复；后端未起时降级为本地会话（壳可独立开发）。 */
export function useSessions(): SessionsApi {
  const [sessions, setSessions] = useState<SessionItem[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [serverMode, setServerMode] = useState(false);
  const localSeq = useRef(0);
  const activeRef = useRef<string | null>(null);
  activeRef.current = activeId;

  const localCreate = useCallback((): SessionItem => {
    return {
      id: 'local-' + Date.now().toString(36) + '-' + localSeq.current++,
      title: NEW_TITLE,
      pinned: false,
      starred: false,
    };
  }, []);

  // 启动装配：GET /api/sessions → 服务端模式（列表序：置顶优先、更新时间倒序 → 首个即最近会话，刷新恢复）；
  // 空列表则建一个「新对话」；不可达 → 本地降级模式。
  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const list = await listRemote();
        if (cancelled) return;
        setServerMode(true);
        if (list.length > 0) {
          setSessions(list);
          setActiveId(list[0].id);
        } else {
          const created = await createRemote();
          if (cancelled) return;
          setSessions([created]);
          setActiveId(created.id);
        }
      } catch {
        if (cancelled) return;
        const seed: SessionItem = { id: LOCAL_SEED_ID, title: NEW_TITLE, pinned: false, starred: false };
        setServerMode(false);
        setSessions([seed]);
        setActiveId(seed.id);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const refresh = useCallback(async (): Promise<SessionItem[]> => {
    const list = await listRemote();
    setSessions(list);
    return list;
  }, []);

  const create = useCallback(async () => {
    if (!serverMode) {
      const s = localCreate();
      setSessions((ss) => [...ss, s]);
      setActiveId(s.id);
      return;
    }
    const created = await createRemote();
    await refresh();
    setActiveId(created.id);
  }, [serverMode, localCreate, refresh]);

  const mutate = useCallback(
    async (id: string, fields: Partial<Pick<SessionItem, 'title' | 'pinned' | 'starred'>>) => {
      if (serverMode) {
        await patchRemote(id, fields);
        await refresh();
      } else {
        setSessions((ss) => ss.map((s) => (s.id === id ? { ...s, ...fields } : s)));
      }
    },
    [serverMode, refresh],
  );

  const rename = useCallback((id: string, title: string) => mutate(id, { title }), [mutate]);

  const togglePin = useCallback(
    (id: string) => {
      const cur = sessions.find((s) => s.id === id);
      return cur ? mutate(id, { pinned: !cur.pinned }) : Promise.resolve();
    },
    [mutate, sessions],
  );

  const toggleStar = useCallback(
    (id: string) => {
      const cur = sessions.find((s) => s.id === id);
      return cur ? mutate(id, { starred: !cur.starred }) : Promise.resolve();
    },
    [mutate, sessions],
  );

  const remove = useCallback(
    async (id: string) => {
      if (!serverMode) {
        const rest = sessions.filter((s) => s.id !== id);
        const next = rest.length > 0 ? rest : [localCreate()];
        setSessions(next);
        if (activeRef.current === id) setActiveId(next[0].id);
        return;
      }
      const resp = await fetch('/api/sessions/' + id, { method: 'DELETE' });
      if (!resp.ok) throw new Error('HTTP ' + resp.status);
      const rest = (await refresh()).filter((s) => s.id !== id);
      if (activeRef.current === id) {
        if (rest.length > 0) setActiveId(rest[0].id);
        else await create(); // 空列表兜底：保留一个可用会话
      }
    },
    [serverMode, sessions, refresh, create, localCreate],
  );

  const select = useCallback((id: string) => setActiveId(id), []);

  return { sessions, activeId, serverMode, select, create, rename, togglePin, toggleStar, remove };
}
