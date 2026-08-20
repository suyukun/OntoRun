// 构建段类型（对齐后端 src/api/builder_*_routes.py 的 row_to_dict 输出，统一 Envelope）

export interface Paged<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface PropertySchema {
  type: string;
  properties: Record<string, { type?: string; title?: string; description?: string; enum?: string[]; format?: string; items?: unknown }>;
  required?: string[];
}

export interface ObjectTypeRow {
  id: string;
  ontology_id: string;
  name: string;
  name_cn: string;
  description: string;
  category: string; // domain | artifact | conceptual
  property_schema: PropertySchema;
  status: string; // draft | reviewed | published
  pk_field: string;
  title_field: string;
  source_table: string;
  created_at: string;
  updated_at: string;
  api_name: string;
  _warning?: string;
}

export interface LinkTypeRow {
  id: string;
  ontology_id: string;
  name: string;
  semantic_name: string;
  category: string; // semantic | fk_inferred | structural
  source_type_id: string;
  target_type_id: string;
  cardinality: string; // 1:1 | 1:N | N:1 | N:M
  fk_field: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface DatasetRow {
  id: string;
  ontology_id: string;
  name: string;
  kind: string;
  status: string;
  row_count: number;
  schema_json: Record<string, unknown>;
  source_path: string;
  created_at: string;
  updated_at: string;
}

export interface DagNode {
  id: string;
  kind: 'connector' | 'storage' | 'transform' | 'output';
  config?: Record<string, unknown>;
  next?: string[];
}

export interface DagJson {
  nodes: DagNode[];
}

export interface PipelineRow {
  id: string;
  ontology_id: string;
  name: string;
  dag_json: DagJson;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface PipelineRunItem {
  run_id: string;
  pipeline_name: string;
  final_status: string;
  started_at: string;
  finished_at: string;
  node_count: number;
  curated_dataset_id: string | null;
  error: string | null;
}

export interface PipelineRunResult {
  run_id: string;
  pipeline_name: string;
  final_status: string;
  nodes: { node_id: string; status: string; error?: string | null }[];
  curated_dataset_id?: string | null;
}

export interface CuratedRow {
  id: string;
  dataset_id: string;
  quality: Record<string, unknown>;
  status: string; // draft | reviewed | approved
  version: number;
  row_count: number;
  created_at: string;
  updated_at: string;
}

export interface MappingRow {
  id: string;
  ontology_id: string;
  entity_class: string;
  source_table: string;
  field_mapping: Record<string, unknown>[];
  fk_mappings: Record<string, unknown>[];
  cardinalities: Record<string, unknown>;
  status: string;
  created_at: string;
  updated_at: string;
  property_schema?: PropertySchema;
  alias_matches?: unknown;
}

export interface ExtractionRow {
  id: string;
  ontology_id: string;
  status: string;
  result_summary: Record<string, unknown>;
  validation_report: Record<string, unknown>;
  source_path: string;
  provider: string;
  created_at: string;
  updated_at: string;
}

export interface LogicRuleRow {
  id: string;
  ontology_id: string;
  name: string;
  logic_type: string;
  expression: Record<string, unknown>;
  severity: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ActionTypeRow {
  id: string;
  ontology_id: string;
  name: string;
  parameters: Record<string, unknown>;
  submission_criteria: Record<string, unknown>;
  effects: Record<string, unknown>;
  status: string;
  created_at: string;
  updated_at: string;
}
