/**
 * 思考流话术模板池（UX v0.2 · US3）：同一步骤类型备多模板随机取用，避免每次展示一字不差。
 * 约束（门槛稿 A4）：中文、克制、不夸张；不含数字与归因（因果沉默=诚实铁律）——
 * 数字与事实永远由结构化字段回填，模板只改措辞；步骤集合仍完全来自真实 SSE 事件（假步骤零容忍）。
 */

/** 步骤标题（与语义层步骤定义同源）→ 话术模板池（导出供测试与审查） */
export const PHRASE_POOL: Record<string, string[]> = {
  意图路由: ['理解问题在问什么', '判断问题对应的口径', '匹配已注册的查询规则'],
  口径声明: ['核对统计口径', '确认指标计算方式', '对齐口径定义'],
  '参数抽取+校验': ['提取并检查查询参数', '解析时间范围等条件', '校验参数完整性'],
  参数校验: ['检查查询参数', '核对时间范围', '校验参数边界'],
  'SQL 编译': ['按规则模板生成查询', '准备参数化查询', '组织查询语句'],
  下推执行: ['在数据层执行查询', '查询源数据', '下推到存储层执行'],
  结果校验: ['检查结果结构', '核对数值一致性', '复核返回结果'],
  回答: ['组织回答', '汇总结果作答', '整理最终结论'],
  口径拦截: ['核对口径范围', '检查是否在已注册口径内'],
};

/** 未登记步骤类型的通用兜底池 */
const FALLBACK_POOL = ['正在处理', '按流程推进', '继续执行'];

/** 同一步骤类型的上一次取用（连续两次不同模板，保证随机性可观感） */
const lastPicked = new Map<string, string>();

/** 按步骤类型随机取一条话术；池内多模板时避开上一次取用 */
export function pickThinkingPhrase(stepTitle: string): string {
  const pool = PHRASE_POOL[stepTitle] ?? FALLBACK_POOL;
  let phrase = pool[Math.floor(Math.random() * pool.length)];
  const last = lastPicked.get(stepTitle);
  if (last != null && phrase === last) phrase = pool[(pool.indexOf(phrase) + 1) % pool.length];
  lastPicked.set(stepTitle, phrase);
  return phrase;
}
