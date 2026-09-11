import { useEffect } from 'react';
import { Icon } from './Icon';
import type { ChatMessage, StepInfo } from '../types';

/**
 * T-U1 口径溯源面板（UX v0.2 · US1 溯源穿透·汇总级，Jack 裁决 2026-09-11）：
 * 点答案中任一数字 → 口径卡（这句数怎么算的人话＋规则状态）＋确认历史（谁何时确认）。
 * 产品红线：汇总级穿透，不含 SQL / 表结构 / 来源明细行；SQL 仅留审计层内部。
 * 数据只来自现有服务返回（steps 的「口径声明」步骤）；不足处显式空态（宁缺毋滥）。
 */

/** B3 契约：穿透面板数据 = { caliber_card, confirm_history }（汇总级）。
 * 现有服务返回未携带确认记录（谁/何时），确认历史一律渲染显式空态，
 * 待后端下发 confirm_history 后在此接线（不自行加端点）。 */

/** 「口径声明」步骤 detail → 人话口径＋规则状态。
 * 后端格式："{口径人话}；口径规则 {规则状态}"（engine.py 口径声明帧）；
 * 无后缀（如 mock 流）时规则状态为 null → 面板显式空态。 */
export function parseCaliber(steps: StepInfo[]): { text: string; ruleStatus: string | null } {
  const detail = steps.find((s) => s.title === '口径声明')?.detail?.trim();
  if (!detail) return { text: '', ruleStatus: null };
  const sep = '；口径规则 ';
  const i = detail.indexOf(sep);
  if (i < 0) return { text: detail, ruleStatus: null };
  return { text: detail.slice(0, i), ruleStatus: detail.slice(i + sep.length) };
}

/** 数字 token：千分位（1,240）/ 小数（52.7%），日期片段（2026-08 中的 2026、08）也算「任一数字」 */
const NUMBER_RE = /(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?%?/g;

/** 回答文本 → 数字可点击（US1：点答案里任一数字；数字本身不改写，不加归因文案） */
export function AnswerText({ text, onNumber }: { text: string; onNumber: () => void }) {
  const parts: (string | { num: string })[] = [];
  let last = 0;
  for (const m of text.matchAll(NUMBER_RE)) {
    const i = m.index ?? 0;
    if (i > last) parts.push(text.slice(last, i));
    parts.push({ num: m[0] });
    last = i + m[0].length;
  }
  if (last < text.length) parts.push(text.slice(last));
  return (
    <>
      {parts.map((p, k) =>
        typeof p === 'string' ? (
          <span key={k}>{p}</span>
        ) : (
          <button key={k} className="numlink" title="查看这个数的口径" onClick={onNumber}>
            {p.num}
          </button>
        ),
      )}
    </>
  );
}

/** 口径溯源面板（汇总级）：口径卡＋确认历史；复用详情抽屉的 drawer 视觉，不新增样式体系。 */
export function CaliberPanel({ msg, onClose }: { msg: ChatMessage; onClose: () => void }) {
  // Esc 关闭（与详情抽屉一致的键盘可达性）
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [onClose]);

  const caliber = parseCaliber(msg.steps);

  return (
    <>
      <div className="drawer-mask" onClick={onClose} />
      <div className="drawer" role="dialog" aria-label="口径溯源">
        <div className="drawer-head">
          <b>口径溯源 · {(msg.text || '').slice(0, 24)}{(msg.text || '').length > 24 ? '…' : ''}</b>
          <button className="opbtn" aria-label="关闭" onClick={onClose}><Icon name="x" size={14} /></button>
        </div>
        <div className="drawer-body">
          <div className="basis">
            <div>
              <b>口径说明：</b>{caliber.text || '—'}
            </div>
            <div>
              <b>规则状态：</b>{caliber.ruleStatus ?? '暂无规则状态记录'}
            </div>
          </div>
          <div className="basis-confirm">
            <b>确认历史</b>
            <div className="hint">暂无确认记录。口径确认在管理台完成后，这里将显示谁在何时确认。</div>
          </div>
          <p className="hint">
            汇总级口径说明；完整过程复现请用「详情」中的证据编号。
          </p>
        </div>
      </div>
    </>
  );
}
