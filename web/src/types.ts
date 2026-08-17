// 本体元数据类型（后端 /meta/schema 返回结构，元数据驱动 UI）

export interface PropertyMeta {
  type?: string;
  title?: string;
  description?: string;
  format?: string;
  enum?: string[];
  default?: unknown;
  items?: PropertyMeta;
  properties?: Record<string, PropertyMeta>;
  anyOf?: PropertyMeta[];
}

export interface ObjectTypeMeta {
  name: string;
  api_name: string;
  description: string;
  pk_field: string;
  title_field: string;
  source_table: string;
  properties: Record<string, PropertyMeta>;
}

export interface LinkTypeMeta {
  name: string;
  source_type: string;
  target_type: string;
  cardinality: "N:1" | "1:N";
  fk_field: string;
  inverse_name: string;
  description: string;
}

export interface PreconditionMeta {
  error_code: string;
  summary: string;
}

export interface StateEffects {
  source_backed: string[];
  ontology_owned: string[];
  derived?: string[];
}

export interface ActionMeta {
  name: string;
  description: string;
  high_risk: boolean;
  params_schema: {
    type: string;
    properties: Record<string, PropertyMeta>;
    required?: string[];
  };
  preconditions: PreconditionMeta[];
  error_codes: string[];
  state_effects: StateEffects;
}

export interface MetaSchema {
  objects: ObjectTypeMeta[];
  links: LinkTypeMeta[];
  actions: ActionMeta[];
}

export interface Envelope<T = unknown> {
  request_id: string;
  outcome: string;
  data?: T;
  error?: { code: string; message: string; detail?: unknown };
}

export interface ObjectItem {
  object_type: string;
  pk: string;
  properties: Record<string, unknown>;
}

export interface ObjectListData {
  type: string;
  page: number;
  page_size: number;
  total: number;
  items: ObjectItem[];
}

export interface ObjectDetailData {
  object_type: string;
  pk: string;
  properties: Record<string, unknown>;
  links: Record<string, number>;
}

export interface AgentChatRequest {
  message: string;
  session_id?: string;
}

export interface AgentChatResponse {
  session_id: string;
  reply?: string;
  need_confirm?: {
    id: string;
    name: string;
    arguments: Record<string, unknown>;
  };
  outcome?: string;
}

export interface AgentConfirmRequest {
  session_id: string;
  call_id: string;
  confirmed: boolean;
}

export interface AgentConfirmResponse {
  reply?: string;
  outcome?: string;
}
