// 中文预警等级（黄/橙/红）类型与元数据辅助 —— 非组件模块（供组件/常量/API 共用，避免 fast-refresh 告警）。
import { ZH_WARN_META } from './riskTheme';
import type { ZhWarnMeta } from './riskTheme';

export type ZhWarnLevel = '黄' | '橙' | '红';

export function isZhWarnLevel(v: unknown): v is ZhWarnLevel {
  return v === '黄' || v === '橙' || v === '红';
}

export function zhWarnMeta(level: ZhWarnLevel): ZhWarnMeta {
  return ZH_WARN_META[level];
}
