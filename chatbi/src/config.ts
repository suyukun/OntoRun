/**
 * 壳级配置常量（UX v0.2 · US3 / NC-U4 裁决：配置文件开关，演示默认开）。
 * 关掉 DEMO_PACING_ENABLED 后思考流按事件真实节奏展示（门槛稿 D3 演示路径④「关演示模式对比节奏」）。
 */

/** 演示节奏开关：SSE 全程快于最短展示时长时，按真实步骤事件补间展示（false = 纯真实节奏，不补间） */
export const DEMO_PACING_ENABLED = true;

/** 思考流最短展示时长（ms，真实时钟）：补间目标下限 */
export const MIN_THINKING_MS = 2500;
