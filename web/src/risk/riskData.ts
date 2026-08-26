// 风险演示数据层 —— 物化快照加载（web/public/risk-demo/risk-snapshot.json）
// 快照由 scripts/export_risk_demo_snapshot.py 从 ap_anping 真实数据同源生成。
// 数据层已抽象：将来后端暴露 /objects/risk_* 后可在此切换为实时查询，页面零改动。
import { useEffect, useState } from 'react';

export interface RiskPropertyMeta {
  title: string;
  type?: string;
  enum?: string[];
}
export interface RiskObjectMeta {
  name: string;
  api_name: string;
  description: string;
  pk_field: string;
  title_field: string;
  source_table: string;
  properties: Record<string, RiskPropertyMeta>;
}
export interface RiskLinkMeta {
  name: string;
  source_type: string;
  target_type: string;
  cardinality: 'N:1' | '1:N';
  fk_field: string;
  inverse_name: string;
  description: string;
}
export interface RiskActionMeta {
  name: string;
  description: string;
  high_risk: boolean;
  params_schema: { properties: Record<string, RiskPropertyMeta>; required?: string[] };
}
export interface RiskMeta {
  objects: RiskObjectMeta[];
  links: RiskLinkMeta[];
  actions: RiskActionMeta[];
}
export interface RiskItem {
  pk: string;
  properties: Record<string, unknown>;
}
export interface RiskEdge {
  source: string; // 源对象 api_name
  source_pk: string;
  link: string; // 链接名（正方向）
  target: string;
  target_pk: string;
}
export interface RiskSnapshot {
  schema_version: number;
  note: string;
  meta: RiskMeta;
  totals: Record<string, number>;
  items: Record<string, RiskItem[]>;
  edges: RiskEdge[];
  group_metrics: Record<string, { index_name: string; index_value: number; index_unit: string }[]>;
}

const SNAPSHOT_URL = '/risk-demo/risk-snapshot.json';

let cache: RiskSnapshot | null = null;
let inflight: Promise<RiskSnapshot> | null = null;

export function loadSnapshot(): Promise<RiskSnapshot> {
  if (cache) return Promise.resolve(cache);
  if (!inflight) {
    inflight = fetch(SNAPSHOT_URL)
      .then((res) => {
        if (!res.ok) throw new Error('HTTP ' + res.status + ': ' + res.statusText);
        return res.json() as Promise<RiskSnapshot>;
      })
      .then((data) => {
        cache = data;
        return data;
      })
      .finally(() => {
        inflight = null;
      });
  }
  return inflight;
}

export function useRiskSnapshot(): { data: RiskSnapshot | null; loading: boolean; error: string | null } {
  const [state, setState] = useState<{ data: RiskSnapshot | null; loading: boolean; error: string | null }>({
    data: null,
    loading: true,
    error: null,
  });
  useEffect(() => {
    let cancelled = false;
    loadSnapshot()
      .then((d) => {
        if (!cancelled) setState({ data: d, loading: false, error: null });
      })
      .catch((err: Error) => {
        if (!cancelled) setState({ data: null, loading: false, error: err.message });
      });
    return () => {
      cancelled = true;
    };
  }, []);
  return state;
}

// ---- 只含真实数据的对象类型（排除无源表/空对象，保证「无空对象」） ----
export function dataObjectTypes(meta: RiskMeta, totals: Record<string, number>): RiskObjectMeta[] {
  return meta.objects.filter((o) => totals[o.api_name] > 0);
}

export function objectByApi(meta: RiskMeta, apiName: string): RiskObjectMeta | undefined {
  return meta.objects.find((o) => o.api_name === apiName);
}

export function linkByTarget(meta: RiskMeta, linkName: string): RiskLinkMeta | undefined {
  return meta.links.find((l) => l.name === linkName);
}

// 某对象在某链接里是否处于「源侧」（决定方向语义：out=正方向/入向=逆方向）
export function linkSide(link: RiskLinkMeta, objectApi: string): 'source' | 'target' {
  return link.source_type === objectApi ? 'source' : 'target';
}

export function inverseOf(link: RiskLinkMeta, objectApi: string): string {
  // 当前对象在 target 侧时，展示方向用 inverse_name（对象在 target = 入向链接）
  return linkSide(link, objectApi) === 'target' ? link.inverse_name : link.name;
}

export function itemsOf(snapshot: RiskSnapshot, apiName: string): RiskItem[] {
  return snapshot.items[apiName] || [];
}

export function findItem(snapshot: RiskSnapshot, apiName: string, pk: string): RiskItem | undefined {
  return itemsOf(snapshot, apiName).find((i) => i.pk === pk);
}

// 某对象某 pk 的 出向/入向 链接汇总（返回 展示链接名 → 目标记录数组）
export function linksFor(
  snapshot: RiskSnapshot,
  objectApi: string,
  pk: string,
  direction: 'out' | 'in',
): Map<string, { targetType: string; items: RiskItem[] }> {
  const result = new Map<string, { targetType: string; items: RiskItem[] }>();
  const isOut = direction === 'out';
  for (const e of snapshot.edges) {
    const matches = isOut ? e.source === objectApi && e.source_pk === pk : e.target === objectApi && e.target_pk === pk;
    if (!matches) continue;
    // 当前对象为 source → 正方向 link 是出向；当前对象为 target → inverse 是出向
    const displayLink = e.source === objectApi ? e.link : (linkByTarget(snapshot.meta, e.link)?.inverse_name ?? e.link);
    if (displayLink !== e.link) continue; // 只在本对象为 source 时走正方向展示；target 侧在 in 分支处理
    const targetType = e.source === objectApi ? e.target : e.source;
    const targetItem = findItem(snapshot, targetType, isOut ? e.target_pk : e.source_pk);
    if (!targetItem) continue;
    const entry = result.get(e.link) ?? { targetType, items: [] };
    entry.items.push(targetItem);
    result.set(e.link, entry);
  }
  return result;
}

// 更稳的版本：按「当前对象所在侧」计算展示链接名与目标记录（含入向）
export function traversalFor(
  snapshot: RiskSnapshot,
  objectApi: string,
  pk: string,
  direction: 'out' | 'in',
): Map<string, { displayLink: string; targetType: string; items: RiskItem[] }> {
  const result = new Map<string, { displayLink: string; targetType: string; items: RiskItem[] }>();
  const isOut = direction === 'out';
  for (const e of snapshot.edges) {
    const onSource = e.source === objectApi && e.source_pk === pk;
    const onTarget = e.target === objectApi && e.target_pk === pk;
    if (isOut && onSource) {
      const entry = result.get(e.link) ?? { displayLink: e.link, targetType: e.target, items: [] };
      const ti = findItem(snapshot, e.target, e.target_pk);
      if (ti) {
        entry.items.push(ti);
        result.set(e.link, entry);
      }
    } else if (!isOut && onTarget) {
      const link = linkByTarget(snapshot.meta, e.link);
      const display = link?.inverse_name ?? e.link;
      const entry = result.get(display) ?? { displayLink: display, targetType: e.source, items: [] };
      const si = findItem(snapshot, e.source, e.source_pk);
      if (si) {
        entry.items.push(si);
        result.set(display, entry);
      }
    }
  }
  return result;
}

// 值格式化（数字/日期/布尔），供列表与详情展示
export function formatRiskValue(value: unknown): string {
  if (value === null || value === undefined || value === '') return '—';
  if (typeof value === 'number') {
    if (Number.isInteger(value)) return value.toLocaleString('zh-CN');
    return value.toLocaleString('zh-CN', { maximumFractionDigits: 2 });
  }
  if (typeof value === 'boolean') return value ? '是' : '否';
  const s = String(value);
  const iso = /^\d{4}-\d{2}-\d{2}/.test(s);
  if (iso) {
    const d = new Date(s);
    if (!Number.isNaN(d.getTime())) {
      return s.length > 10 ? d.toLocaleString('zh-CN') : d.toLocaleDateString('zh-CN');
    }
  }
  return s;
}
