import { useCallback, useEffect, useRef, useState } from 'react';
import type { ChatMessage, ServerMessage, ServerSession, SessionItem } from '../types';

/** 新对话默认标题（首问命名策略的判据） */
export const NEW_TITLE = '新对话';

const LOCAL_SEED_ID = 'local-0';

function toSession(raw: ServerSession): SessionItem {
  return {
    id: raw.id,
    title: raw.title,
    pinned: !!raw.pinned,
    starred: !!raw.starred,
    archived: !!raw.archived,
    updatedAt: raw.updated_at,
  };
}

async function listRemote(archived = false): Promise<SessionItem[]> {
  const resp = await fetch('/api/sessions' + (archived ? '?archived=1' : ''));
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

type PatchFields = Partial<Pick<SessionItem, 'title' | 'pinned' | 'starred' | 'archived'>>;

async function patchRemote(id: string, fields: PatchFields): Promise<void> {
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
  /** 未归档会话（服务端模式已过滤；本地降级模式前端过滤） */
  sessions: SessionItem[];
  /** 归档区会话 */
  archivedSessions: SessionItem[];
  activeId: string | null;
  /** true = /api/sessions 可达（服务端为唯一事实源）；false = 后端未起，本地降级 */
  serverMode: boolean;
  select: (id: string) => void;
  create: () => Promise<void>;
  rename: (id: string, title: string) => Promise<void>;
  togglePin: (id: string) => Promise<void>;
  toggleStar: (id: string) => Promise<void>;
  archive: (id: string) => Promise<void>;
  restore: (id: string) => Promise<void>;
  remove: (id: string) => Promise<void>;
}

/**
 * 会话栏状态（§3.5）：服务端 CRUD + 刷新恢复；后端未起时降级为本地会话（壳可独立开发）。
 * 归档（UX 2026-09-09）：archived=1 移出主列表进归档区，可恢复；区别于删除（hidden，不可恢复）。
 * 本地降级模式下 sessions 数组承载全部会话，派生时按 archived 过滤。
 */
export function useSessions(): SessionsApi {
  const [rawSessions, setRawSessions] = useState<SessionItem[]>([]);
  const [rawArchived, setRawArchived] = useState<SessionItem[]>([]);
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
      archived: false,
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
        void listRemote(true).then((arch) => { if (!cancelled) setRawArchived(arch); }).catch(() => undefined);
        if (list.length > 0) {
          setRawSessions(list);
          setActiveId(list[0].id);
        } else {
          const created = await createRemote();
          if (cancelled) return;
          setRawSessions([created]);
          setActiveId(created.id);
        }
      } catch {
        if (cancelled) return;
        const seed: SessionItem = { id: LOCAL_SEED_ID, title: NEW_TITLE, pinned: false, starred: false };
        setServerMode(false);
        setRawSessions([seed]);
        setActiveId(seed.id);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const refresh = useCallback(async (): Promise<SessionItem[]> => {
    const list = await listRemote();
    setRawSessions(list);
    void listRemote(true).then(setRawArchived).catch(() => undefined);
    return list;
  }, []);

  const create = useCallback(async () => {
    if (!serverMode) {
      const s = localCreate();
      setRawSessions((ss) => [...ss, s]);
      setActiveId(s.id);
      return;
    }
    const created = await createRemote();
    await refresh();
    setActiveId(created.id);
  }, [serverMode, localCreate, refresh]);

  const mutate = useCallback(
    async (id: string, fields: PatchFields) => {
      if (serverMode) {
        await patchRemote(id, fields);
        await refresh();
      } else {
        setRawSessions((ss) => ss.map((s) => (s.id === id ? { ...s, ...fields } : s)));
      }
    },
    [serverMode, refresh],
  );

  const rename = useCallback((id: string, title: string) => mutate(id, { title }), [mutate]);

  const togglePin = useCallback(
    (id: string) => {
      const cur = rawSessions.find((s) => s.id === id) ?? rawArchived.find((s) => s.id === id);
      return cur ? mutate(id, { pinned: !cur.pinned }) : Promise.resolve();
    },
    [mutate, rawSessions, rawArchived],
  );

  const toggleStar = useCallback(
    (id: string) => {
      const cur = rawSessions.find((s) => s.id === id) ?? rawArchived.find((s) => s.id === id);
      return cur ? mutate(id, { starred: !cur.starred }) : Promise.resolve();
    },
    [mutate, rawSessions, rawArchived],
  );

  const archive = useCallback(
    async (id: string) => {
      await mutate(id, { archived: true });
      if (activeRef.current === id) {
        const next = (serverMode ? await listRemote() : rawSessions.filter((s) => !s.archived && s.id !== id))[0];
        setActiveId(next ? next.id : null);
      }
    },
    [mutate, serverMode, rawSessions],
  );

  const restore = useCallback((id: string) => mutate(id, { archived: false }), [mutate]);

  const remove = useCallback(
    async (id: string) => {
      if (!serverMode) {
        const rest = rawSessions.filter((s) => s.id !== id);
        const next = rest.length > 0 ? rest : [localCreate()];
        setRawSessions(next);
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
    [serverMode, rawSessions, refresh, create, localCreate],
  );

  const select = useCallback((id: string) => setActiveId(id), []);

  const sessions = serverMode ? rawSessions : rawSessions.filter((s) => !s.archived);
  const archivedSessions = serverMode ? rawArchived : rawSessions.filter((s) => !!s.archived);

  return { sessions, archivedSessions, activeId, serverMode, select, create, rename, togglePin, toggleStar, archive, restore, remove };
}
