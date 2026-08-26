// 测试用小快照（迷你版 risk-snapshot，结构与物化快照一致）
import type { RiskSnapshot } from './riskData';

export const miniSnapshot: RiskSnapshot = {
  schema_version: 1,
  note: 'test fixture',
  meta: {
    objects: [
      { name: 'GroupCustomer', api_name: 'group_customer', description: '集团客户（测试）', pk_field: 'group_customer_no', title_field: 'group_customer_no', source_table: 'x', properties: { group_customer_no: { title: '集团编号' }, group_customer_name: { title: '集团名称' }, member_count: { title: '成员数', type: 'integer' } } },
      { name: 'WarningSignal', api_name: 'warning_signal', description: '预警信号（测试）', pk_field: 'warning_id', title_field: 'warning_id', source_table: 'x', properties: { warning_id: { title: '预警ID' }, signal_name: { title: '信号名称' }, warn_level: { title: '预警等级', enum: ['RED', 'YELLOW', 'BLUE'] }, signal_status: { title: '信号状态' }, risk_exposure: { title: '风险敞口', type: 'number' } } },
      { name: 'Disposal', api_name: 'disposal', description: '预警处置（测试）', pk_field: 'disposal_id', title_field: 'disposal_id', source_table: 'x', properties: { disposal_id: { title: '处置ID' }, disposal_status: { title: '处置状态' } } },
      { name: 'ApproveOrder', api_name: 'approve_order', description: '审批单（测试）', pk_field: 'approve_order_id', title_field: 'approve_order_id', source_table: 'x', properties: { approve_order_id: { title: '审批单ID' }, approve_order_status: { title: '审批状态' } } },
    ],
    links: [
      { name: 'warning.for_group', source_type: 'WarningSignal', target_type: 'GroupCustomer', cardinality: 'N:1', fk_field: 'group_customer_no', inverse_name: 'group_customer.warning_signals', description: '集团预警' },
      { name: 'disposal.for_warning', source_type: 'Disposal', target_type: 'WarningSignal', cardinality: 'N:1', fk_field: 'warning_id', inverse_name: 'warning_signal.disposals', description: '处置归属' },
    ],
    actions: [
      { name: 'adjust_warning_level', description: '预警等级调整', high_risk: true, params_schema: { properties: { warning_id: { title: '预警ID' }, new_level: { title: '新等级', enum: ['RED'] } }, required: ['warning_id'] } },
    ],
  },
  totals: { group_customer: 8000, warning_signal: 80000, disposal: 20000, approve_order: 20000 },
  items: {
    group_customer: [{ pk: 'GRP-2026-000001', properties: { group_customer_no: 'GRP-2026-000001', group_customer_name: '中科智造产业发展集团', member_count: 6 } }],
    warning_signal: [
      { pk: 'WS-2026-00000004', properties: { warning_id: 'WS-2026-00000004', signal_name: '信用风险-押品贬值预警信号', warn_level: 'YELLOW', signal_status: '已确认', risk_exposure: 48210.7 } },
      { pk: 'WS-2026-00000129', properties: { warning_id: 'WS-2026-00000129', signal_name: '信用风险-逾期预警信号', warn_level: 'YELLOW', signal_status: '确认中', risk_exposure: 1234 } },
    ],
    disposal: [{ pk: 'WD-2026-00000095', properties: { disposal_id: 'WD-2026-00000095', disposal_status: '暂缓处置' } }],
    approve_order: [{ pk: 'APP-2026-00000001', properties: { approve_order_id: 'APP-2026-00000001', approve_order_status: 'APPROVED' } }],
  },
  edges: [
    { source: 'warning_signal', source_pk: 'WS-2026-00000004', link: 'warning.for_group', target: 'group_customer', target_pk: 'GRP-2026-000001' },
    { source: 'disposal', source_pk: 'WD-2026-00000095', link: 'disposal.for_warning', target: 'warning_signal', target_pk: 'WS-2026-00000004' },
  ],
  group_metrics: {},
};
