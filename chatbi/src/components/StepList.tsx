import type { StepInfo } from '../types';

const STATUS_LABEL: Record<StepInfo['status'], string> = { ok: '通过', fail: '失败', blocked: '拦截' };

/**
 * 决策步骤列表（L2 与 L3 共用）：按展示序连续编号 1..N（§7 #3 无跳号）。
 * 步骤数完全由事件流决定（后端 D6 会动态追加「数字校验」步），严禁硬编码步数；
 * fail/blocked 视觉区分；ms 为该步实测耗时（L3 视角数据，随步展示）。
 * 用户可见层零 SQL（Jack 2026-09-11 裁决）：step.sql 仅存于审计链数据结构，不再渲染。
 */
export function StepList({ steps }: { steps: StepInfo[] }) {
  return (
    <ol className="steps">
      {steps.map((s, i) => (
        <li className={'stp stp-' + s.status} key={i}>
          <div className="stp-head">
            <span className="stp-no">{i + 1}</span>
            <span className={'st st-' + s.status}>{STATUS_LABEL[s.status]}</span>
            <b>{s.title}</b>
            {s.ms != null && <span className="stp-ms">{s.ms}ms</span>}
          </div>
          <div className="stp-detail">{s.detail}</div>
        </li>
      ))}
    </ol>
  );
}
