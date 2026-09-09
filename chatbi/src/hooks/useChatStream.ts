import { useCallback, useRef, useState } from 'react';
import { buildMockEvents } from '../mock/stream';
import type { ChatEvent, EndReason, FinalResult, StepInfo, StreamError } from '../types';

/** 附录 A：客户端 30s 无任何帧 → 超时态（按服务异常处理） */
const FRAME_TIMEOUT_MS = 30_000;
const MOCK_STEP_DELAY_MS = 120;
const MOCK_TOKEN_DELAY_MS = 10;

export interface StreamCallbacks {
  onStep: (s: StepInfo) => void;
  onToken: (text: string) => void;
  onFinal: (r: FinalResult) => void;
  onEnded: (why: EndReason, err?: StreamError) => void;
}

export interface ChatStream {
  send: (question: string) => void;
  stop: () => void;
  busy: boolean;
}

/**
 * SSE 消费 hook（附录 A 协议 + demo chat.html send 的帧格式）：
 * - fetch reader 解析 data: 帧（兼容 event: 名 + data kind 双风格，payload 兼容包一层/平铺两种）
 * - AbortController：stop() 用户取消；30s 无帧看门狗超时
 * - 断连/无 final 帧 → interrupted；error 帧 → error
 * - mock 模式不发起请求，按事件序列延时回放（独立开发不依赖后端）
 */
export function useChatStream(cfg: { endpoint: string; mock: boolean; callbacks: StreamCallbacks }): ChatStream {
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
    (question: string) => {
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
      if (cfg.mock) void runMock(question, dispatch, ctrl.signal, finish);
      else void runSse(question, cfg.endpoint, dispatch, ctrl, finish);
    },
    [cfg.endpoint, cfg.mock],
  );

  return { send, stop, busy };
}

type Terminal = (why: EndReason, err?: StreamError) => void;
type Dispatch = (ev: ChatEvent) => boolean;

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

async function runSse(question: string, endpoint: string, dispatch: Dispatch, ctrl: AbortController, finish: Terminal): Promise<void> {
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
      body: JSON.stringify({ question }),
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
