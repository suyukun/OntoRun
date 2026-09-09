import type { ChatMessage, FinalResult } from '../types';

/** 八状态（v0.2 §4.2）+ 三个生命周期变体（canceled/interrupted/error）。path→状态一对一显式映射。 */
export type AiStatus =
  | 'loading'
  | 'success'
  | 'success_empty'
  | 'success_degraded'
  | 'ask_param'
  | 'out_of_range'
  | 'rejected'
  | 'unregistered'
  | 'validation_failed'
  | 'error'
  | 'interrupted'
  | 'canceled';

const SUCCESS_PATHS = ['hot', 'cold_pushdown', 'cold_adhoc'];

export function deriveStatus(m: ChatMessage): AiStatus {
  if (m.phase === 'streaming') return 'loading';
  if (m.endedBy === 'canceled') return 'canceled';
  if (m.endedBy === 'interrupted') return 'interrupted';
  if (m.endedBy === 'error' || !m.result) return 'error';
  return deriveFinal(m.result);
}

export function deriveFinal(r: FinalResult): AiStatus {
  if (SUCCESS_PATHS.includes(r.path)) {
    if (!r.rows || r.rows.length === 0) return 'success_empty';
    return r.degraded ? 'success_degraded' : 'success';
  }
  if (r.path === 'blocked_param') {
    return r.block_reason === 'out_of_range' ? 'out_of_range' : 'ask_param';
  }
  if (r.path === 'rejected') return 'rejected';
  if (r.path === 'unregistered') return 'unregistered';
  if (r.path === 'validation_failed') return 'validation_failed';
  return 'error';
}
