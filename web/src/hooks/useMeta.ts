// 元数据加载 hook —— /meta/schema 一次加载全局共享（可 reload）
import { useEffect, useState } from 'react';
import { fetchMetaSchema } from '../api';
import type { MetaSchema } from '../types';

interface MetaState {
  meta: MetaSchema | null;
  loading: boolean;
  error: string | null;
  reload: () => void;
}

export function useMeta(): MetaState {
  const [state, setState] = useState<MetaState>({
    meta: null,
    loading: true,
    error: null,
    reload: () => undefined,
  });
  const [nonce, setNonce] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setState((prev) => ({ ...prev, loading: true, error: null }));
    fetchMetaSchema()
      .then((meta) => {
        if (!cancelled) setState({ meta, loading: false, error: null, reload: () => setNonce((n) => n + 1) });
      })
      .catch((err: Error) => {
        if (!cancelled) setState({ meta: null, loading: false, error: err.message, reload: () => setNonce((n) => n + 1) });
      });
    return () => { cancelled = true; };
  }, [nonce]);

  return state;
}