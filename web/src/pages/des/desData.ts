// DES 企业模拟数据层 —— /des/enterprises/* 端点契约（单一事实来源：后端实时统计）。
// 行数由后端打开 SQLite 实时 COUNT(*)，manifest/yaml 只作元信息与对照值；
// 本层不缓存不伪造，缺省字段如实透传 null。
import { useEffect, useState } from 'react';

export interface DesTableStat {
  table: string;
  rows: number | null;
  manifest_rows: number | null;
  error?: string;
}
export interface DesDatabaseStat {
  file: string;
  live_total_rows: number | null;
  tables: DesTableStat[];
  error?: string;
}
export interface DesEnterpriseMeta {
  directory: string;
  display_name: string | null;
  code_prefix: string | null;
  seed: number | null;
  data_version: string | null;
  config_sha256: string | null;
  manifest_total_rows: number | null;
  generated_at: string | null;
}
/** yaml 顶层 domains 未定型（当前产物缺该键），宽松透传，由 UI 如实渲染。 */
export interface DesDomain {
  [key: string]: unknown;
}
export interface DesOverview {
  enterprise: DesEnterpriseMeta;
  databases: DesDatabaseStat[];
  totals: { databases: number; tables: number; live_rows: number };
  domains: DesDomain[] | null;
}
export interface DesEnterpriseListItem {
  name: string;
  display_name: string | null;
}

async function getJson<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error('请求失败: ' + url + ' (' + res.status + ')');
  }
  return (await res.json()) as T;
}

export async function fetchDesEnterprises(): Promise<DesEnterpriseListItem[]> {
  const body = await getJson<{ data: { items: DesEnterpriseListItem[] } }>('/des/enterprises');
  return body.data.items;
}

export async function fetchDesOverview(name: string): Promise<DesOverview> {
  const body = await getJson<{ data: DesOverview }>('/des/enterprises/' + name + '/overview');
  return body.data;
}

/** 拉企业清单并给出默认选择（优先 ap_anping，否则取清单首项）。 */
export function useDesEnterprises(): {
  items: DesEnterpriseListItem[];
  selected: string;
  setSelected: (name: string) => void;
} {
  const [items, setItems] = useState<DesEnterpriseListItem[]>([]);
  const [selected, setSelected] = useState<string>('ap_anping');
  useEffect(() => {
    let alive = true;
    fetchDesEnterprises()
      .then((list) => {
        if (!alive) return;
        setItems(list);
        setSelected((cur) => (list.some((i) => i.name === cur) ? cur : list[0]?.name ?? ''));
      })
      .catch(() => setItems([]));
    return () => {
      alive = false;
    };
  }, []);
  return { items, selected, setSelected };
}

/** 表格扁平行：库分组筛选所需展开结构。 */
export interface FlatTableRow extends DesTableStat {
  key: string;
  library: string;
}

export function flattenDatabases(databases: DesDatabaseStat[]): FlatTableRow[] {
  return databases.flatMap((db) =>
    db.tables.map((t) => ({ ...t, key: db.file + '.' + t.table, library: db.file })),
  );
}
