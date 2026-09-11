import { useCallback, useRef, useState } from 'react';
import { MIN_THINKING_MS } from '../config';
import { buildMockEvents } from '../mock/stream';
import type { ChatEvent, EndReason, FinalResult, StepInfo, StreamError } from '../types';

/** 附录 A：客户端 30s 无任何帧 → 超时态（按服务异常处理） */
const FRAME_TIMEOUT_MS = 30_000;
const MOCK_STEP_DELAY_MS = 120;
const MOCK_TOKEN_DELAY_MS = 10;
/** 相邻步骤最小可读间隔（ms）：同批到达快于它的步骤稍候错开，防思考区一帧闪跳；自然到达慢于它则零延迟 */
const MIN_STEP_GAP_MS = 150;

export interface StreamCallbacks {
  onStep: (s: StepInfo) => void;
  onToken: (text: string) => void;
  onFinal: (r: FinalResult) => void;
  onEnded: (why: EndReason, err?: StreamError) => void;
}

/** 发送附加字段：会话归属 + 幂等键（重试复用同 client_request_id → 后端回放快照不产生重复 trace，附录 A） */
export interface SendExtras {
  conversationId?: string;
  clientRequestId?: string;
}

export interface ChatStream {
  send: (question: string, extras?: SendExtras) => void;
  stop: () => void;
  busy: boolean;
}

/**
 * SSE 消费 hook（附录 A 协议 + demo chat.html send 的帧格式）：
 * - fetch reader 解析 data: 帧（兼容 event: 名 + data kind 双风格，payload 兼容包一层/平铺两种）
 * - AbortController：stop() 用户取消；30s 无帧看门狗超时
 * - 断连/无 final 帧 → interrupted；error 帧 → error
 * - mock 模式不发起请求，按事件序列延时回放（独立开发不依赖后端）
 * - US3 演示节奏（cfg.pacing，总时长兜底制）：步骤按到达自然速度释放，仅当整个思考流快于 MIN_THINKING_MS
 *   时把 final 展示落点兜底至最短时长（Jack 2026-09-11 裁决）；只释放真实收到的事件（展示步骤 ⊆ SSE 事件，
 *   假步骤零容忍），关掉开关即纯真实节奏
 */
export function useChatStream(cfg: {
  endpoint: string;
  mock: boolean;
  pacing?: boolean;
  callbacks: StreamCallbacks;
}): ChatStream {
  const [busy, setBusy] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  const userAbortRef = useRef(false);
  const cbRef = useRef(cfg.callbacks);
  cbRef.current = cfg.callbacks;

  const stop = useCallback(() => {
    if (!abortRef.current) return;
    userAbortRef.current = true;
    abortRef.current.abort();
  }, []);

  const send = useCallback(
    (question: string, extras?: SendExtras) => {
      if (abortRef.current) return; // BUSY：一次一问（§3.6 连发不做排队）
      const ctrl = new AbortController();
      abortRef.current = ctrl;
      userAbortRef.current = false;
      setBusy(true);
      const finish = (why: EndReason, err?: StreamError) => {
        if (abortRef.current !== ctrl) return;
        abortRef.current = null;
        setBusy(false);
        cbRef.current.onEnded(why, err);
      };
      const dispatch = (ev: ChatEvent): boolean => {
        switch (ev.kind) {
          case 'step':
            cbRef.current.onStep(ev.step);
            return false;
          case 'token':
            cbRef.current.onToken(ev.text);
            return false;
          case 'final':
            cbRef.current.onFinal(ev.result);
            finish('final');
            return true;
          case 'error':
            finish('error', { code: ev.code, message: ev.message });
            return true;
        }
      };
      // US3：演示节奏补间——pacer 持有真实事件按节拍释放；流自身终局（取消/断流/异常）弃未展示缓冲
      const pacer = cfg.pacing ? new StepPacer(Date.now(), MIN_THINKING_MS, dispatch) : null;
      const finishNow = (why: EndReason, err?: StreamError) => {
        if (pacer) pacer.cancel();
        finish(why, err);
      };
      const sink: Dispatch = (ev) => (pacer ? pacer.push(ev) : dispatch(ev));
      if (cfg.mock) void runMock(question, sink, ctrl.signal, finishNow);
      else void runSse(question, cfg.endpoint, extras, sink, ctrl, finishNow);
    },
    [cfg.endpoint, cfg.mock, cfg.pacing],
  );

  return { send, stop, busy };
}

type Terminal = (why: EndReason, err?: StreamError) => void;
type Dispatch = (ev: ChatEvent) => boolean;

/**
 * US3 节奏器（演示模式，总时长兜底制）：只释放真实收到的 SSE 事件，SHALL NOT 插入不存在步骤。
 * - 步骤与回答 token 到达即放（自然速度）；相邻步骤仅保留 MIN_STEP_GAP_MS 最小可读间隔防同批闪跳。
 * - 仅当整个思考流快于最短展示时长（final 提前到达）时，final 展示落点兜底至 t0+minMs；流到得慢
 *   （真实节奏 ≥ minMs）时 2.5s 截止后到点即放，不额外拖长。
 * - 展示顺序 = 事件真实顺序：兜底的 final/error 不越过缓冲中未展示的步骤。
 * - 拍点只取决于队头与固定锚点（t0 / lastStepAt），已在等的定时器不必因后续入队重排。
 */
class StepPacer {
  private queue: ChatEvent[] = [];
  private timer: ReturnType<typeof setTimeout> | null = null;
  private lastStepAt: number;
  private stopped = false;

  constructor(
    private readonly t0: number,
    private readonly minMs: number,
    private readonly out: Dispatch,
  ) {
    this.lastStepAt = t0;
  }

  /** 入队一个真实事件；返回是否终局帧（final/error），供 SSE 读流循环提前退出 */
  push(ev: ChatEvent): boolean {
    const terminal = ev.kind === 'final' || ev.kind === 'error';
    if (this.stopped) {
      this.out(ev);
      return terminal;
    }
    this.queue.push(ev);
    if (!this.timer) this.pump();
    return terminal;
  }

  /** 流自身终局（用户取消/断流/异常）时调用：丢弃未展示缓冲，不补发表演帧 */
  cancel(): void {
    this.stopped = true;
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }
    this.queue = [];
  }

  private pump = (): void => {
    this.timer = null;
    for (;;) {
      const head = this.queue[0];
      if (!head || this.stopped) return;
      const now = Date.now();
      if (now >= this.t0 + this.minMs) {
        // 已到最短展示时长：剩余真实事件立即放行，不再拉长（到点即放）
        while (this.queue.length > 0 && !this.stopped) this.releaseHead();
        return;
      }
      if (head.kind === 'token') {
        this.releaseHead();
        continue;
      }
      // step：相邻步骤最小可读间隔；final/error：总时长兜底落点
      const due = head.kind === 'step' ? this.lastStepAt + MIN_STEP_GAP_MS : this.t0 + this.minMs;
      if (now < due) {
        this.timer = setTimeout(this.pump, due - now);
        return;
      }
      this.releaseHead();
    }
  };

  private releaseHead(): void {
    const head = this.queue.shift();
    if (!head) return;
    if (head.kind === 'step') this.lastStepAt = Date.now();
    if (this.out(head)) {
      // 终局帧已出 → 停拍弃队
      this.stopped = true;
      this.queue = [];
    }
  }
}

async function runMock(question: string, dispatch: Dispatch, signal: AbortSignal, finish: Terminal): Promise<void> {
  const events = buildMockEvents(question);
  const sleep = (ms: number) => new Promise<void>((r) => setTimeout(r, ms));
  for (const ev of events) {
    if (signal.aborted) {
      finish('canceled');
      return;
    }
    const done = dispatch(ev);
    if (done) return;
    await sleep(ev.kind === 'token' ? MOCK_TOKEN_DELAY_MS : MOCK_STEP_DELAY_MS);
  }
  finish('interrupted'); // mock 序列必有 final，正常不会到这里
}

async function runSse(
  question: string,
  endpoint: string,
  extras: SendExtras | undefined,
  dispatch: Dispatch,
  ctrl: AbortController,
  finish: Terminal,
): Promise<void> {
  let timedOut = false;
  let watchdog: ReturnType<typeof setTimeout> | undefined;
  const resetWatchdog = () => {
    if (watchdog) clearTimeout(watchdog);
    watchdog = setTimeout(() => {
      timedOut = true;
      ctrl.abort();
    }, FRAME_TIMEOUT_MS);
  };
  let sawFinal = false;
  try {
    const resp = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question,
        conversation_id: extras?.conversationId,
        client_request_id: extras?.clientRequestId,
      }),
      signal: ctrl.signal,
    });
    if (!resp.ok || !resp.body) throw new Error('HTTP ' + resp.status);
    resetWatchdog();
    const reader = resp.body.getReader();
    const dec = new TextDecoder();
    let buf = '';
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      resetWatchdog();
      buf += dec.decode(value, { stream: true });
      const parts = buf.split('\n\n');
      buf = parts.pop() ?? '';
      for (const ev of parseFrames(parts)) {
        if (dispatch(ev)) {
          sawFinal = true;
          break;
        }
      }
      if (sawFinal) return;
    }
    if (!sawFinal) finish('interrupted'); // 附录 A：断流半成品标记「已中断」
  } catch {
    if (ctrl.signal.aborted) {
      if (timedOut) finish('error', { code: 'E_NET', message: '查询失败：服务未响应（30 秒无数据帧）' });
      else finish('canceled');
    } else {
      finish('error', { code: 'E_NET', message: '查询失败：服务未响应' });
    }
  } finally {
    if (watchdog) clearTimeout(watchdog);
  }
}

/** 解析 SSE 帧：兼容 data-only（demo 风格，kind 字段在 payload 内）与 event-name + data（标准 SSE）两种风格。 */
function parseFrames(frames: string[]): ChatEvent[] {
  const out: ChatEvent[] = [];
  for (const f of frames) {
    let name = '';
    const dataLines: string[] = [];
    for (const ln of f.split('\n')) {
      if (ln.startsWith('event:')) name = ln.slice(6).trim();
      else if (ln.startsWith('data:')) dataLines.push(ln.slice(5).trimStart());
    }
    if (dataLines.length === 0) continue;
    let obj: Record<string, unknown>;
    try {
      obj = JSON.parse(dataLines.join('\n')) as Record<string, unknown>;
    } catch {
      continue; // 非 JSON 帧（如心跳 comment）忽略
    }
    const kind = (name || String(obj.kind ?? '')).toLowerCase();
    if (kind === 'step') out.push({ kind: 'step', step: (obj.step ?? obj) as StepInfo });
    else if (kind === 'token') out.push({ kind: 'token', text: String(obj.text ?? '') });
    else if (kind === 'final') out.push({ kind: 'final', result: (obj.result ?? obj) as FinalResult });
    else if (kind === 'error') {
      out.push({ kind: 'error', code: String(obj.code ?? 'E_NET'), message: String(obj.message ?? '服务异常') });
    }
  }
  return out;
}
