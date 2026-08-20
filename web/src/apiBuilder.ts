// 构建段 API 客户端（prefix /api/v1/builder，统一 Envelope 信封解包）
// 与 web/src/api.ts 风格一致：outcome=error 或 error 字段存在时抛 Error。
import type {
  ActionTypeRow,
  DagJson,
  CuratedRow,
  DatasetRow,
  ExtractionRow,
  LinkTypeRow,
  LogicRuleRow,
  MappingRow,
  ObjectTypeRow,
  Paged,
  PipelineRow,
  PipelineRunItem,
  PipelineRunResult,
} from './builderTypes';
import type { Envelope } from './types';

const BASE = '/api/v1/builder';

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(BASE + url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  const json: Envelope<T> = await res.json().catch(() => ({
    request_id: '',
    outcome: 'error',
    error: { code: 'HTTP_' + res.status, message: 'HTTP ' + res.status + ': ' + res.statusText },
  }));
  if (json.outcome === 'error' || json.error) {
    throw new Error(json.error?.message || json.outcome || '请求失败');
  }
  return json.data as T;
}

function qs(params: Record<string, string | number | undefined>): string {
  const usp = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== '') usp.set(k, String(v));
  }
  const s = usp.toString();
  return s ? '?' + s : '';
}

// ---------- object-types ----------
export function listObjectTypes(opts?: { category?: string; status?: string; page?: number; page_size?: number }) {
  return request<Paged<ObjectTypeRow>>('/object-types' + qs(opts || {}));
}
export function createObjectType(body: Record<string, unknown>) {
  return request<ObjectTypeRow>('/object-types', { method: 'POST', body: JSON.stringify(body) });
}
export function updateObjectType(id: string, patch: Record<string, unknown>) {
  return request<ObjectTypeRow>('/object-types/' + encodeURIComponent(id), { method: 'PUT', body: JSON.stringify(patch) });
}
export function deleteObjectType(id: string) {
  return request<{ id: string; deleted: boolean }>('/object-types/' + encodeURIComponent(id), { method: 'DELETE' });
}
export function reviewObjectType(id: string) {
  return request<ObjectTypeRow>('/object-types/' + encodeURIComponent(id) + '/review', { method: 'POST', body: '{}' });
}
export function publishObjectType(id: string) {
  return request<ObjectTypeRow>('/object-types/' + encodeURIComponent(id) + '/publish', { method: 'POST', body: '{}' });
}

// ---------- link-types ----------
export function listLinkTypes(opts?: { status?: string; page?: number; page_size?: number }) {
  return request<Paged<LinkTypeRow>>('/link-types' + qs(opts || {}));
}
export function createLinkType(body: Record<string, unknown>) {
  return request<LinkTypeRow>('/link-types', { method: 'POST', body: JSON.stringify(body) });
}
export function updateLinkType(id: string, patch: Record<string, unknown>) {
  return request<LinkTypeRow>('/link-types/' + encodeURIComponent(id), { method: 'PUT', body: JSON.stringify(patch) });
}
export function deleteLinkType(id: string) {
  return request<{ id: string; deleted: boolean }>('/link-types/' + encodeURIComponent(id), { method: 'DELETE' });
}
export function reviewLinkType(id: string) {
  return request<LinkTypeRow>('/link-types/' + encodeURIComponent(id) + '/review', { method: 'POST', body: '{}' });
}
export function publishLinkType(id: string) {
  return request<LinkTypeRow>('/link-types/' + encodeURIComponent(id) + '/publish', { method: 'POST', body: '{}' });
}

// ---------- datasets ----------
export function listDatasets(opts?: { kind?: string; status?: string; page?: number; page_size?: number }) {
  return request<Paged<DatasetRow>>('/datasets' + qs(opts || {}));
}
export function uploadDataset(file: File, name?: string) {
  const fd = new FormData();
  fd.append('file', file);
  if (name) fd.append('name', name);
  return request<DatasetRow>('/datasets/upload', { method: 'POST', body: fd });
}
export function previewDataset(name: string, limit = 10) {
  return request<{ name: string; kind: string; row_count?: number; preview: unknown[] }>(
    '/datasets/' + encodeURIComponent(name) + '/preview' + qs({ limit }),
  );
}

// ---------- pipelines ----------
export function getPipeline(name: string) {
  return request<PipelineRow>('/pipelines/' + encodeURIComponent(name));
}
export function createPipeline(name: string, dagJson: DagJson, status = 'draft') {
  return request<PipelineRow>('/pipelines', { method: 'POST', body: JSON.stringify({ name, dag_json: dagJson, status }) });
}
export function runPipeline(name: string) {
  return request<PipelineRunResult>('/pipelines/' + encodeURIComponent(name) + '/run', { method: 'POST', body: '{}' });
}
export function pipelineRuns(name: string) {
  return request<{ pipeline_name: string; runs: PipelineRunItem[]; total: number }>(
    '/pipelines/' + encodeURIComponent(name) + '/runs',
  );
}

// ---------- curated ----------
export function listCurated(opts?: { status?: string; page?: number; page_size?: number }) {
  return request<Paged<CuratedRow>>('/curated' + qs(opts || {}));
}
export function reviewCurated(name: string) {
  return request<CuratedRow>('/curated/' + encodeURIComponent(name) + '/review', { method: 'POST', body: '{}' });
}

// ---------- mappings ----------
export function listMappings(opts?: { entity_class?: string; status?: string; page?: number; page_size?: number }) {
  return request<Paged<MappingRow>>('/mappings' + qs(opts || {}));
}
export function runMappingAuto(payload: Record<string, unknown>) {
  return request<MappingRow & { property_schema?: unknown; alias_matches?: unknown }>('/mappings/auto', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
export function applyMapping(name: string) {
  return request<{ result: Record<string, unknown>; issues?: Record<string, unknown>[] }>(
    '/mappings/' + encodeURIComponent(name) + '/apply',
    { method: 'POST', body: '{}' },
  );
}

// ---------- extractions ----------
export function listExtractions(opts?: { status?: string; page?: number; page_size?: number }) {
  return request<Paged<ExtractionRow>>('/extractions' + qs(opts || {}));
}
export function runExtraction(payload: Record<string, unknown>) {
  return request<ExtractionRow>('/extractions/run', { method: 'POST', body: JSON.stringify(payload) });
}

// ---------- logic ----------
export function listLogicRules(opts?: { logic_type?: string; severity?: string; status?: string; page?: number; page_size?: number }) {
  return request<Paged<LogicRuleRow>>('/logic' + qs(opts || {}));
}
export function discoverLogic(objectType?: string) {
  return request<Record<string, unknown>>('/logic/discover', {
    method: 'POST',
    body: JSON.stringify({ object_type: objectType ?? null }),
  });
}
export function reviewLogic(ref: string) {
  return request<LogicRuleRow>('/logic/' + encodeURIComponent(ref) + '/review', { method: 'POST', body: '{}' });
}
export function publishLogic(ref: string) {
  return request<LogicRuleRow>('/logic/' + encodeURIComponent(ref) + '/publish', { method: 'POST', body: '{}' });
}

// ---------- actions（构建段：动作类型元数据 + E6 执行） ----------
export function listActionTypes(opts?: { status?: string; page?: number; page_size?: number }) {
  return request<Paged<ActionTypeRow>>('/actions' + qs(opts || {}));
}
export function getActionType(name: string) {
  return request<ActionTypeRow>('/actions/' + encodeURIComponent(name));
}
export function runActionType(name: string, params: Record<string, unknown>, dryRun = false) {
  return request<Record<string, unknown>>('/actions/' + encodeURIComponent(name) + '/run', {
    method: 'POST',
    body: JSON.stringify({ params, dry_run: dryRun }),
  });
}
export function actionRuns(name: string) {
  return request<{ items: Record<string, unknown>[]; total: number }>('/actions/' + encodeURIComponent(name) + '/runs');
}