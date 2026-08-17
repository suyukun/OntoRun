// API 客户端：封装所有后端语义接口调用
import type {
  ActionMeta,
  AgentChatRequest,
  AgentChatResponse,
  AgentConfirmRequest,
  AgentConfirmResponse,
  Envelope,
  MetaSchema,
  ObjectDetailData,
  ObjectListData,
  ObjectTypeMeta,
} from './types';

const BASE = '/api';

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(BASE + url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    throw new Error('HTTP ' + res.status + ': ' + res.statusText);
  }
  const json: Envelope<T> = await res.json();
  if (json.outcome === 'error' || json.error) {
    throw new Error(json.error?.message || json.outcome);
  }
  return json.data as T;
}

export async function fetchMetaSchema(): Promise<MetaSchema> {
  return request<MetaSchema>('/meta/schema');
}

export async function fetchObjectTypes(): Promise<ObjectTypeMeta[]> {
  return request<ObjectTypeMeta[]>('/meta/objects');
}

export async function fetchActions(): Promise<ActionMeta[]> {
  return request<ActionMeta[]>('/meta/actions');
}

export async function fetchObjectList(
  type: string,
  params?: Record<string, string>,
): Promise<ObjectListData> {
  const qs = new URLSearchParams(params).toString();
  return request<ObjectListData>('/objects/' + type + (qs ? '?' + qs : ''));
}

export async function fetchObjectDetail(
  type: string,
  pk: string,
): Promise<ObjectDetailData> {
  return request<ObjectDetailData>('/objects/' + type + '/' + encodeURIComponent(pk));
}

export async function fetchLinkTraversal(
  type: string,
  pk: string,
  linkName: string,
  direction: string = 'out',
): Promise<{ link_name: string; direction: string; objects: import('./types').ObjectItem[] }> {
  return request('/objects/' + type + '/' + encodeURIComponent(pk) + '/links/' + linkName + '?direction=' + direction);
}

export async function submitAction(
  actionName: string,
  params: Record<string, unknown>,
): Promise<Envelope> {
  const res = await fetch(BASE + '/actions/' + actionName, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Actor': 'api',
    },
    body: JSON.stringify(params),
  });
  return res.json() as Promise<Envelope>;
}

export async function agentChat(
  body: AgentChatRequest,
): Promise<AgentChatResponse> {
  const res = await fetch(BASE + '/agent/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return res.json();
}

export async function agentConfirm(
  body: AgentConfirmRequest,
): Promise<AgentConfirmResponse> {
  const res = await fetch(BASE + '/agent/confirm', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return res.json();
}
