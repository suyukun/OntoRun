/**
 * 壳级配置常量（UX v0.2 · US3 / NC-U4 裁决：配置文件开关，演示默认开）。
 * 关掉 DEMO_PACING_ENABLED 后思考流按事件真实节奏展示（门槛稿 D3 演示路径④「关演示模式对比节奏」）。
 */

/** 演示节奏开关：步骤自然速度展示＋final 落点总时长兜底（false = 纯真实节奏，不兜底） */
export const DEMO_PACING_ENABLED = true;

/** 思考流最短展示时长（ms，真实时钟）：整个思考流快于它时，final 展示落点兜底至该值 */
export const MIN_THINKING_MS = 2500;
