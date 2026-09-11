import { useEffect, useMemo, useRef, useState } from 'react';
import type { AiStatus } from '../state/deriveStatus';
import type { FinalResult } from '../types';
import { requestRewrite } from './rewrite';
import { renderTemplate, type RewriteFacts, type TemplateSpec } from './templates';

/** T-U4 拒答/追问话术 hook：模板同步上屏（offline 安全）+ LLM 改写并行旁路（不阻塞主回答渲染）。
 * 旁路超时/失败/限流/数字不符 → 静默保模板：不出错态、不重试。 */

/** 状态 → 改写模板规格（模块级常量：引用稳定，供 effect 依赖） */
export const REWRITE_SPECS: Partial<Record<AiStatus, TemplateSpec>> = {
  rejected: { kind: 'reject', slot: 'scope' },
  unregistered: { kind: 'reject', slot: 'unregistered' },
  out_of_range: { kind: 'reject', slot: 'range' },
  ask_param: { kind: 'clarify' },
};

/** 从 FinalResult 结构化载体抽取事实字段：kw 取后端确定性文案的「」引用、range 取日期边界（两端稳定约定） */
export function buildRewriteFacts(r: FinalResult): RewriteFacts {
  const facts: RewriteFacts = { question: r.question };
  const kw = r.answer.match(/「(.+?)」/)?.[1];
  if (kw) facts.kw = kw;
  const range = r.answer.match(/\d{4}-\d{2}-\d{2}\s*~\s*\d{4}-\d{2}-\d{2}/)?.[0];
  if (range) facts.range = range;
  return facts;
}

export interface PoliteAnswer {
  text: string;
  /** raw=后端原文（非改写态）；template=本地模板兜底；llm=旁路改写稿（已过数字断言） */
  source: 'raw' | 'template' | 'llm';
}

/** REJECT/CLARIFY 话术：模板先渲染保证主回答不被改写阻塞；改写稿仅在通过数字断言后无感换上。 */
export function usePoliteAnswer(status: AiStatus, r: FinalResult | null): PoliteAnswer {
  const spec = REWRITE_SPECS[status];
  const enabled = spec != null && r != null;
  const facts = useMemo(() => (r != null ? buildRewriteFacts(r) : {}), [r]);
  const [llm, setLlm] = useState<string | null>(null);
  const seq = useRef(0);

  useEffect(() => {
    if (!enabled || !spec || !r) return;
    const my = ++seq.current;
    let cancelled = false;
    requestRewrite({ kind: spec.kind, answer: r.answer, facts })
      .then((text) => {
        if (!cancelled && my === seq.current && text != null) setLlm(text);
      })
      .catch(() => { /* 静默：模板兜底 */ });
    return () => { cancelled = true; };
  }, [enabled, spec, r, facts]);

  if (!enabled || !spec || !r) return { text: r?.answer ?? '', source: 'raw' };
  return { text: llm ?? renderTemplate(spec, facts), source: llm != null ? 'llm' : 'template' };
}
