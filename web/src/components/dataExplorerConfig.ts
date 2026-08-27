// DataExplorer 展示配置 —— 业务域分组 / 列表字段偏好 / 状态语义色映射
// （展示偏好层；对象与字段仍由 schema 驱动，语义色沿用 riskTheme 浅底预警色）
import { RISK_COLORS as C } from '../risk/riskTheme';

export const DOMAIN_GROUPS: { key: string; label: string; objects: string[] }[] = [
  { key: 'customer', label: '客户域', objects: ['group_customer', 'risk_customer'] },
  { key: 'monitor', label: '风险监测域', objects: ['warning_signal', 'concentration_limit', 'metric'] },
  { key: 'disposal', label: '预警处置域', objects: ['disposal', 'approve_order', 'approve_task'] },
  { key: 'project', label: '风险项目域', objects: ['risk_project'] },
];

export const LIST_FIELDS: Record<string, string[]> = {
  risk_customer: ['customer_name', 'customer_no', 'industry_name', 'internal_level', 'asset_quality_level', 'group_customer_no'],
  group_customer: ['group_customer_name', 'member_count', 'customer_status', 'asset_quality_level'],
  warning_signal: ['signal_name', 'customer_name', 'warn_level', 'signal_status', 'risk_exposure', 'signal_generate_date'],
  disposal: ['disposal_status', 'warning_id', 'disposal_time'],
  approve_order: ['approve_order_title', 'approve_order_status', 'business_type', 'apply_time'],
  approve_task: ['approve_order_id', 'approve_task_status', 'approve_result', 'approve_time'],
  concentration_limit: ['customer_name', 'concentration_limit', 'warning_value', 'current_status'],
  risk_project: ['project_name', 'group_customer_name', 'business_balance', 'risk_exposure_balance', 'five_classification', 'guarantee_method'],
  metric: ['index_name', 'index_value', 'index_unit', 'dim_type_name', 'group_customer_no'],
};

// 状态语义色（浅底描边样式；灰阶项沿用文本层级色）
export const STATUS_COLORS: Record<string, string> = {
  待确认: C.textFaint,
  确认中: C.blue,
  已确认: C.yellow,
  处置中: C.red,
  已关闭: C.textDim,
  已撤销: C.textFaint,
  未处置: C.textFaint,
  暂缓处置: C.textDim,
  已处置: C.green,
  PROCESS: C.blue,
  APPROVED: C.green,
  REJECTED: C.red,
  PENDING: C.yellow,
  COMPLETED: C.green,
  NORMAL: C.green,
  ORANGE_ALERT: C.yellow,
  RED_ALERT: C.red,
};
