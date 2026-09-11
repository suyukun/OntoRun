/** T-U4 拒答话术模板池（REJECT/CLARIFY 各一组，风格对齐 labels.ts）。
 * 硬约束：模板静态文本零数字——文案中的数字只允许经占位符从结构化字段回填
 * （「数字相等」硬判据的构造性保证，见 rewrite.numbersMatch）。 */

export type RewriteKind = 'reject' | 'clarify';

/** REJECT 组内语义槽：范围外拒答 / 未注册口径 / 数据边界外（后端确定性文案的三种拒答形态） */
export type RejectSlot = 'scope' | 'unregistered' | 'range';

export type TemplateSpec = { kind: 'reject'; slot: RejectSlot } | { kind: 'clarify' };

/** 结构化事实字段：模板占位符与 LLM 改写校验的唯一数字/事实来源 */
export type RewriteFacts = Record<string, string>;

/** REJECT 模板组：占位符 {kw}=命中词、{range}=数据覆盖边界（缺失时回落 PLACEHOLDER_DEFAULTS，均零数字） */
export const REJECT_TEMPLATES: Record<RejectSlot, string> = {
  scope: '「{kw}」超出了当前已注册的语义范围。我不猜数，宁可不答，不出假数。',
  unregistered: '该问题尚未注册口径。我不猜数、不编数，先把已注册的口径答准。',
  range: '当前数据仅覆盖 {range}。这段范围之外如实说没有，不硬答。',
};

/** CLARIFY 模板组：按问题哈希确定性轮换（同问题同句，不随机），[0] 为后端规范句 */
export const CLARIFY_TEMPLATES: string[] = [
  '请问您要查询哪个月份？',
  '想查哪个月？说个月份就能继续。',
  '补一个月份，我按已注册口径接着查。',
];

/** 占位符缺失时的回落值（零数字，保证硬判据不被模板本身破坏） */
const PLACEHOLDER_DEFAULTS: Record<string, string> = { kw: '该问题' };

/** 确定性哈希（DJB2）：跨问题轮换模板池，同输入恒定 */
export function hashSeed(s: string): number {
  let h = 5381;
  for (const ch of s) h = ((h * 33) ^ (ch.codePointAt(0) ?? 0)) >>> 0;
  return h;
}

function fill(template: string, facts: RewriteFacts): string {
  return template.replace(/\{(\w+)\}/g, (_, k: string) => facts[k] ?? PLACEHOLDER_DEFAULTS[k] ?? '');
}

/** 渲染模板：纯函数、零网络（模板兜底路径完全不依赖任何请求） */
export function renderTemplate(spec: TemplateSpec, facts: RewriteFacts): string {
  if (spec.kind === 'clarify') {
    const pool = CLARIFY_TEMPLATES;
    return fill(pool[hashSeed(facts.question ?? '') % pool.length], facts);
  }
  return fill(REJECT_TEMPLATES[spec.slot], facts);
}
