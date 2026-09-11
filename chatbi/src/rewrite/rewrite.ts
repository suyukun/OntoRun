import type { RewriteFacts, RewriteKind } from './templates';

/** T-U4 拒答话术旁路改写（NC-U3：zai glm-5.3-flash，模型选择在后端旁路端点内做）。
 * 后端缺口：src/semantic 尚无该端点（app.py 由 T-U2 独占），串行任务补；
 * 本模块为独立封装：fetch 可注入、模板兜底路径完全不依赖网络。 */

/** 旁路改写端点（待后端串行补齐；404/网络失败 → 模板静默兜底） */
export const REWRITE_ENDPOINT = '/api/rewrite/answer';

/** EARS：改写超时 2s 回退模板 */
export const REWRITE_TIMEOUT_MS = 2000;

/** 数字序列提取：NFKC 归一 + 去千分位逗号后按数字 token 抽取（日期/金额/百分比统一口径） */
export function numberSequence(text: string): string[] {
  const norm = text.normalize('NFKC').replace(/(\d),(\d)/g, '$1$2');
  return norm.match(/\d+(?:\.\d+)?/g) ?? [];
}

/** 数字相等硬判据：改写文案与结构化来源的数字序列逐一相等 */
export function numbersMatch(rewritten: string, source: string): boolean {
  const a = numberSequence(rewritten);
  const b = numberSequence(source);
  return a.length === b.length && a.every((v, i) => v === b[i]);
}

export interface RewriteRequest {
  kind: RewriteKind;
  /** 后端结构化文案（数字事实唯一来源；改写稿的数字必须与其逐一相等） */
  answer: string;
  /** 结构化事实字段 */
  facts: RewriteFacts;
  endpoint?: string;
  /** 可注入 fetch（测试离线路径用；缺省走全局 fetch） */
  fetchImpl?: typeof fetch;
  timeoutMs?: number;
}

/** LLM 只改措辞：成功返回改写文案。超时/网络失败/限流/非 2xx/数字断言不符 → null（调用方静默回退模板）。
 * 单次尝试，不重试（不出错态、不重试轰炸）。 */
export async function requestRewrite(req: RewriteRequest): Promise<string | null> {
  const doFetch = req.fetchImpl ?? fetch;
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), req.timeoutMs ?? REWRITE_TIMEOUT_MS);
  try {
    const resp = await doFetch(req.endpoint ?? REWRITE_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ kind: req.kind, answer: req.answer, facts: req.facts }),
      signal: ctrl.signal,
    });
    if (!resp.ok) return null;
    const data = (await resp.json()) as { text?: unknown };
    if (typeof data?.text !== 'string' || !data.text.trim()) return null;
    if (!numbersMatch(data.text, req.answer)) return null; // 数字漂移一律拒收
    return data.text;
  } catch {
    return null;
  } finally {
    clearTimeout(timer);
  }
}
