import { useCallback, useState } from 'react';
import type { FinalResult, HistoryEntry } from '../types';

/** 回放源不存在：条目被删除（删除=隐藏标记）后 GET /api/trace/{rid} 返回 404。 */
export class TraceNotFoundError extends Error {
  constructor() {
    super('trace not found');
    this.name = 'TraceNotFoundError';
  }
}

export async function fetchHistory(): Promise<HistoryEntry[]> {
  const resp = await fetch('/api/history');
  if (!resp.ok) throw new Error('HTTP ' + resp.status);
  const data = (await resp.json()) as unknown;
  if (!Array.isArray(data)) throw new Error('history 结构缺失');
  return data as HistoryEntry[];
}

/** 快照回放数据源：trace JSONL 存有当时完整 result（含 rows），回放不重新执行（附录 D）。 */
export async function fetchTrace(requestId: string): Promise<FinalResult> {
  const resp = await fetch('/api/trace/' + encodeURIComponent(requestId));
  if (resp.status === 404) throw new TraceNotFoundError();
  if (!resp.ok) throw new Error('HTTP ' + resp.status);
  return (await resp.json()) as FinalResult;
}

async function deleteRemote(requestId: string): Promise<void> {
  const resp = await fetch('/api/history/' + encodeURIComponent(requestId), { method: 'DELETE' });
  if (!resp.ok) throw new Error('HTTP ' + resp.status);
}

export function useHistory() {
  const [entries, setEntries] = useState<HistoryEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setEntries(await fetchHistory());
    } catch {
      setError('查询历史加载失败，请稍后重试。');
    } finally {
      setLoading(false);
    }
  }, []);

  const remove = useCallback(
    async (requestId: string) => {
      await deleteRemote(requestId);
      await reload();
    },
    [reload],
  );

  return { entries, loading, error, reload, remove };
}
