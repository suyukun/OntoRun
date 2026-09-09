import type { AiStatus } from '../state/deriveStatus';

/** path → 业务化徽章文案（§附录 G 术语表：热路径→月报口径（预聚合）、冷路径→明细即席计算）。 */
export const BUSINESS_PATH_LABELS: Record<string, string> = {
  hot: '月报口径（预聚合）',
  cold_pushdown: '明细即席计算',
  cold_adhoc: '明细即席计算',
};

/** 结果态徽章文案（blocked/拒绝/校验族按状态区分，profile.path_labels 作深回落）。 */
export const RESULT_BADGE_LABELS: Partial<Record<AiStatus, string>> = {
  ask_param: '待补参数',
  out_of_range: '超出数据范围',
  rejected: '范围外拒答',
  unregistered: '未注册口径',
  validation_failed: '校验未通过',
};

/** 生命周期变体徽章（无 final 帧时 L1 亦常驻可读）。 */
export const LIFECYCLE_BADGE_LABELS: Partial<Record<AiStatus, string>> = {
  error: '服务异常',
  interrupted: '已中断',
  canceled: '已取消',
};

/** 附录 B 错误码 → 用户文案（兜底表；后端 error 帧 message 已脱敏且优先展示）。 */
export const ERROR_COPY: Record<string, string> = {
  E_NET: '查询失败：服务未响应',
  E_SQL: '查询执行出错，系统已记录，可重试。',
  E_VALIDATION: '校验未通过，拒绝返回',
  E_PARAM_MISSING: '请问您要查询哪个月份？',
  E_PARAM_RANGE: '当前查询时间超出数据覆盖范围',
  E_SCOPE: '该问题不在当前语义范围内',
};

export const DEFAULT_ERROR_TEXT = '查询失败：服务未响应';

/** 证据编号 hover 提示（§附录 G 术语表）。 */
export const REQ_ID_HINT = '本次查询的唯一编号，报此编号可完整复现过程与结果';

/** 剪贴板复制：clipboard API 优先，非安全上下文回落 execCommand。 */
export async function copyText(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    try {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      const ok = document.execCommand('copy');
      document.body.removeChild(ta);
      return ok;
    } catch {
      return false;
    }
  }
}
