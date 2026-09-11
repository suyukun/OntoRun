import { act, cleanup, render } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { MessageCard } from '../components/MessageCard';
import {
  REWRITE_TIMEOUT_MS, numberSequence, numbersMatch, requestRewrite,
} from '../rewrite/rewrite';
import {
  CLARIFY_TEMPLATES, REJECT_TEMPLATES, renderTemplate, type TemplateSpec,
} from '../rewrite/templates';
import { buildRewriteFacts, REWRITE_SPECS } from '../rewrite/usePoliteAnswer';
import type { ChatMessage, FinalResult } from '../types';

/** T-U4 拒答话术改写（EARS §A3-US4）：改写并行发起 + 2s 超时/失败/限流模板静默回退 + 数字相等硬判据。 */

// ---------- fixtures（形态对齐 mock/stream.ts 与后端确定性文案） ----------

function baseResult(): FinalResult {
  return {
    request_id: 'REQ-TEST-01',
    started_at: '2026-09-12T10:00:00',
    question: '',
    rule: null,
    path: '',
    answer: '',
    sql: null,
    rows: [],
    tables: [],
    steps: [],
  };
}

const REJECTED: FinalResult = {
  ...baseResult(),
  question: '日活情况如何？',
  path: 'rejected',
  rule: 'OUT_OF_SCOPE',
  answer: '「日活」属于活跃/转化域——这块口径还没注册，我不猜数。现在能答：注册总量、分渠道注册、性别分布，换个问法试试？',
};

const ASK_PARAM: FinalResult = {
  ...baseResult(),
  question: '注册用户数是多少？',
  path: 'blocked_param',
  rule: 'REG_TOTAL',
  answer: '请问您要查询哪个月份？',
  block_reason: 'missing_param',
};

const OUT_OF_RANGE: FinalResult = {
  ...baseResult(),
  question: '9月注册用户数是多少？',
  path: 'blocked_param',
  rule: 'REG_TOTAL',
  answer: '当前样本数据仅覆盖 2026-07-01 ~ 2026-08-31，该时间段无数据。',
  block_reason: 'out_of_range',
};

function msgWith(result: FinalResult): ChatMessage {
  return { id: 1, role: 'ai', text: result.question, steps: [], streamedText: '', result, error: null, phase: 'done' };
}

function okFetch(text: string) {
  return vi.fn(() => Promise.resolve({ ok: true, status: 200, json: async () => ({ text }) } as unknown as Response));
}

/** 挂起不返回的 fetch：仅在超时 abort 时 reject（模拟网络黑洞） */
function hangingFetch() {
  return vi.fn((_url: RequestInfo | URL, init?: RequestInit) =>
    new Promise<Response>((_, reject) => {
      init?.signal?.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')));
    }));
}

beforeEach(() => {
  vi.unstubAllGlobals();
});
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.useRealTimers();
});

// ---------- 数字相等硬判据（单元） ----------

describe('数字相等断言（硬判据）', () => {
  it('改写文案数字序列 === 结构化字段数字序列（含日期/千分位归一）', () => {
    expect(numbersMatch('覆盖 2026-07-01 ~ 2026-08-31', '样本数据仅覆盖 2026-07-01 ~ 2026-08-31，无数据。')).toBe(true);
    expect(numbersMatch('注册 2,893 人', '注册 2893 人')).toBe(true);
    expect(numbersMatch('覆盖 2026-07-01 ~ 2026-09-01', '覆盖 2026-07-01 ~ 2026-08-31')).toBe(false);
    expect(numbersMatch('无数字文案', '覆盖 2026 年')).toBe(false);
    expect(numberSequence('2026-07-01 ~ 2026-08-31')).toEqual(['2026', '07', '01', '2026', '08', '31']);
  });

  it('LLM 改写保数字 → 采纳；数字漂移（多/少/改）→ 拒收返回 null', async () => {
    const answer = OUT_OF_RANGE.answer;
    const keep = await requestRewrite({
      kind: 'reject',
      answer,
      facts: buildRewriteFacts(OUT_OF_RANGE),
      fetchImpl: okFetch('该时间段（2026-07-01 ~ 2026-08-31）暂无数据，换个区间再试试。'),
    });
    expect(keep).toBe('该时间段（2026-07-01 ~ 2026-08-31）暂无数据，换个区间再试试。');

    for (const drifted of [
      '当前数据仅覆盖 2026-07-01 ~ 2026-09-30。', // 改数字
      '当前数据仅覆盖 2026-07-01 ~ 2026-08-31 以及 2025 年。', // 多数字
      '当前数据无覆盖，请调整范围。', // 少数字
    ]) {
      const got = await requestRewrite({ kind: 'reject', answer, facts: {}, fetchImpl: okFetch(drifted) });
      expect(got).toBeNull();
    }
  });

  it('模板兜底同样守住硬判据：模板输出数字 === 结构化字段数字', () => {
    const cases: { r: FinalResult; spec: TemplateSpec }[] = [
      { r: OUT_OF_RANGE, spec: REWRITE_SPECS.out_of_range! },
      { r: REJECTED, spec: REWRITE_SPECS.rejected! },
      { r: ASK_PARAM, spec: REWRITE_SPECS.ask_param! },
    ];
    for (const { r, spec } of cases) {
      const text = renderTemplate(spec, buildRewriteFacts(r));
      expect(numbersMatch(text, r.answer)).toBe(true);
    }
    // 模板静态文本零数字：数字只经占位符从 facts 回填
    for (const t of Object.values(REJECT_TEMPLATES)) {
      expect(numberSequence(t.replace(/\{range\}/g, ''))).toEqual([]);
    }
    for (const t of CLARIFY_TEMPLATES) {
      expect(numberSequence(t)).toEqual([]);
    }
    expect(numberSequence(renderTemplate({ kind: 'reject', slot: 'scope' }, {}))).toEqual([]);
    expect(numberSequence(renderTemplate({ kind: 'clarify' }, { question: 'x' }))).toEqual([]);
  });

  it('结构化字段抽取：kw 取「」引用，range 取日期边界，question 必含', () => {
    expect(buildRewriteFacts(REJECTED)).toEqual({ question: REJECTED.question, kw: '日活' });
    expect(buildRewriteFacts(OUT_OF_RANGE)).toEqual({ question: OUT_OF_RANGE.question, range: '2026-07-01 ~ 2026-08-31' });
    expect(buildRewriteFacts(ASK_PARAM)).toEqual({ question: ASK_PARAM.question });
  });
});

// ---------- test_rewrite_fallback（单元：offline / 超时 / 限流） ----------

describe('test_rewrite_fallback：旁路失败一律静默回退模板', () => {
  it('offline（fetch 直接拒绝）→ null，模板路径零网络可用', async () => {
    const got = await requestRewrite({
      kind: 'reject',
      answer: REJECTED.answer,
      facts: buildRewriteFacts(REJECTED),
      fetchImpl: vi.fn(() => Promise.reject(new Error('offline'))),
    });
    expect(got).toBeNull();
    // 模板路径完全不依赖网络：纯函数渲染
    expect(renderTemplate({ kind: 'reject', slot: 'scope' }, buildRewriteFacts(REJECTED))).toContain('不猜数');
    expect(renderTemplate({ kind: 'clarify' }, buildRewriteFacts(ASK_PARAM))).toBe('请问您要查询哪个月份？');
  });

  it('超时 2s → abort → null；单次尝试不重试', async () => {
    vi.useFakeTimers();
    const f = hangingFetch();
    const p = requestRewrite({ kind: 'clarify', answer: ASK_PARAM.answer, facts: {}, fetchImpl: f as unknown as typeof fetch });
    const settled = expect(p).resolves.toBeNull();
    await vi.advanceTimersByTimeAsync(REWRITE_TIMEOUT_MS + 50);
    await settled;
    expect(f).toHaveBeenCalledTimes(1);
    expect(f.mock.calls[0]?.[0]).toBe('/api/rewrite/answer');
    const init = f.mock.calls[0]?.[1] as RequestInit;
    expect(init.method).toBe('POST');
    expect(JSON.parse(String(init.body))).toEqual({ kind: 'clarify', answer: ASK_PARAM.answer, facts: {} });
  });

  it('HTTP 404 / 429 限流 → null（不出错态，调用方静默保模板）', async () => {
    const notFound = vi.fn(() => Promise.resolve({ ok: false, status: 404 } as Response));
    const limited = vi.fn(() => Promise.resolve({ ok: false, status: 429 } as Response));
    await expect(requestRewrite({ kind: 'reject', answer: REJECTED.answer, facts: {}, fetchImpl: notFound as unknown as typeof fetch })).resolves.toBeNull();
    await expect(requestRewrite({ kind: 'reject', answer: REJECTED.answer, facts: {}, fetchImpl: limited as unknown as typeof fetch })).resolves.toBeNull();
  });

  it('响应缺 text / 空 text → null', async () => {
    const empty = vi.fn(() => Promise.resolve({ ok: true, json: async () => ({ text: '  ' }) } as unknown as Response));
    const noField = vi.fn(() => Promise.resolve({ ok: true, json: async () => ({}) } as unknown as Response));
    await expect(requestRewrite({ kind: 'reject', answer: REJECTED.answer, facts: {}, fetchImpl: empty as unknown as typeof fetch })).resolves.toBeNull();
    await expect(requestRewrite({ kind: 'reject', answer: REJECTED.answer, facts: {}, fetchImpl: noField as unknown as typeof fetch })).resolves.toBeNull();
  });
});

// ---------- UI：并行性 + 模板上屏 + 静默兜底 ----------

describe('改写并行发起：不阻塞主回答渲染', () => {
  it('改写请求挂起时，模板文案同步上屏（render 返回即断言，不等任何定时器/微任务）', () => {
    vi.stubGlobal('fetch', hangingFetch());
    const { container } = render(
      <MessageCard msg={msgWith(REJECTED)} pathLabels={{}} onRetry={() => {}} onFollowUp={() => {}} />,
    );
    expect(container.textContent).toContain('「日活」超出了当前已注册的语义范围');
    expect(container.textContent).toContain('不猜数');
  });

  it('改写超时不换稿、无重试轰炸、无出错态', async () => {
    vi.useFakeTimers();
    const f = hangingFetch();
    vi.stubGlobal('fetch', f);
    const { container } = render(
      <MessageCard msg={msgWith(ASK_PARAM)} pathLabels={{}} onRetry={() => {}} onFollowUp={() => {}} />,
    );
    expect(container.textContent).toContain('请问您要查询哪个月份？'); // 模板先行
    await vi.advanceTimersByTimeAsync(REWRITE_TIMEOUT_MS + 100);
    expect(f).toHaveBeenCalledTimes(1); // 单次旁路，不重试
    expect(container.textContent).toContain('请问您要查询哪个月份？'); // 静默保模板
    expect(container.querySelector('.badtext')).toBeNull(); // 无出错态
  });

  it('改写成功且过数字断言 → 换稿；数字漂移 → 静默保模板', async () => {
    let resolveFetch!: (v: unknown) => void;
    vi.stubGlobal('fetch', vi.fn(() => new Promise((res) => { resolveFetch = res; })));
    const card = render(
      <MessageCard msg={msgWith(OUT_OF_RANGE)} pathLabels={{}} onRetry={() => {}} onFollowUp={() => {}} />,
    );
    expect(card.container.textContent).toContain('2026-07-01 ~ 2026-08-31'); // 模板先行（旁路未回）
    expect(card.container.textContent).toContain('这段范围之外如实说没有');

    await act(async () => {
      resolveFetch({ ok: true, json: async () => ({ text: '该时间段（2026-07-01 ~ 2026-08-31）暂无数据，换个区间再试试。' }) });
    });
    expect(card.container.textContent).toContain('换个区间再试试'); // LLM 稿换上

    // 数字漂移场景：另一张卡，LLM 改数字 → 拒收，保持模板
    let resolveDrift!: (v: unknown) => void;
    const fd = vi.fn(() => new Promise((res) => { resolveDrift = res; }));
    vi.stubGlobal('fetch', fd);
    const drift = render(
      <MessageCard msg={{ ...msgWith(OUT_OF_RANGE), id: 2 }} pathLabels={{}} onRetry={() => {}} onFollowUp={() => {}} />,
    );
    await act(async () => {
      resolveDrift({ ok: true, json: async () => ({ text: '覆盖 2026-07-01 ~ 2026-09-30，换个范围。' }) });
    });
    expect(drift.container.textContent).toContain('这段范围之外如实说没有'); // 模板兜底
    expect(drift.container.textContent).not.toContain('2026-09-30');
    expect(fd).toHaveBeenCalledTimes(1);
  });
});
