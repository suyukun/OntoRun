/* oxlint-disable react/only-export-components */
// 全局元数据上下文 —— 运行时 schema 一处加载、各处消费（本体驱动 UI 的数据源）
import { createContext, useContext, type ReactNode } from 'react';
import { useMeta } from '../hooks/useMeta';
import type { MetaSchema } from '../types';

interface MetaContextValue {
  meta: MetaSchema | null;
  loading: boolean;
  error: string | null;
  reload: () => void;
}

const MetaContext = createContext<MetaContextValue>({
  meta: null,
  loading: true,
  error: null,
  reload: () => undefined,
});

export function useMetaContext(): MetaContextValue {
  return useContext(MetaContext);
}

export function MetaProvider({ children }: { children: ReactNode }) {
  const { meta, loading, error, reload } = useMeta();
  return <MetaContext.Provider value={{ meta, loading, error, reload }}>{children}</MetaContext.Provider>;
}