import { useEffect, useState } from 'react';
import { fetchMetaSchema } from '../api';
import type { MetaSchema } from '../types';

interface MetaState {
  meta: MetaSchema | null;
  loading: boolean;
  error: string | null;
}

export function useMeta(): MetaState {
  const [state, setState] = useState<MetaState>({
    meta: null,
    loading: true,
    error: null,
  });

  useEffect(() => {
    let cancelled = false;
    fetchMetaSchema()
      .then((meta) => {
        if (!cancelled) setState({ meta, loading: false, error: null });
      })
      .catch((err: Error) => {
        if (!cancelled) setState({ meta: null, loading: false, error: err.message });
      });
    return () => { cancelled = true; };
  }, []);

  return state;
}
