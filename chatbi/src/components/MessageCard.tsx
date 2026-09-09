import { useEffect, useRef, useState } from 'react';
import { DEFAULT_PATH_LABELS } from '../mock/profile';
import { Icon } from './Icon';
import { deriveStatus, type AiStatus } from '../state/deriveStatus';
import type { ChatMessage, FinalResult } from '../types';
import { Chart } from './Chart';
import { DataTable } from './DataTable';
import { DetailDrawer } from './DetailDrawer';
import {
  BUSINESS_PATH_LABELS, DEFAULT_ERROR_TEXT, ERROR_COPY, LIFECYCLE_BADGE_LABELS,
  REQ_ID_HINT, RESULT_BADGE_LABELS, copyText,
} from './labels';
import { StepList } from './StepList';

interface Props {
  msg: ChatMessage;
  pathLabels: Record<string, string>;
  onRetry: (q: string) => void;
  onFollowUp: (q: string) => void;
}

/** 参数追问快捷 chips（§4.2 #3：选中即续查；P0 前端常量，规则表生成随 T5 接入）。 */
const PARAM_CHIPS = ['8月', '7月'];

/** §3.3：总决策 >2.5s 时 L1 追加「处理中」呼吸态（不自动展开 L2）。 */
const SLOW_MS = 2500;
const COPIED_RESET_MS = 1600;

/** 徽章文案：成功路径用业务化常量（附录 G），结果态/生命周期按状态表，最后回落 profile。 */
function badgeText(status: AiStatus, r: FinalResult | null, pathLabels: Record<string, string>): string {
  if (!r) return LIFECYCLE_BADGE_LABELS[status] ?? status;
  return (
    BUSINESS_PATH_LABELS[r.path]
    ?? RESULT_BADGE_LABELS[status]
    ?? pathLabels[r.path]
    ?? DEFAULT_PATH_LABELS[r.path]
    ?? r.path
  );
}

/** AI 消息卡（§3.2）：L1 摘要条（常驻）→ 回答区 → 数据区 → L2 决策过程（默认收起）→ L3 抽屉。 */
export function MessageCard({ msg, pathLabels, onRetry, onFollowUp }: Props) {
  const [l2Open, setL2Open] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [slow, setSlow] = useState(false);
  /** null=未操作，true/false=最近一次复制成败（三态反馈） */
  const [copied, setCopied] = useState<boolean | null>(null);
  const copyTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const status = deriveStatus(msg);
  const r = msg.result;
  const streaming = status === 'loading';
  const badge = badgeText(status, r, pathLabels);

  // 呼吸态：本次流式超过阈值后 L1 追加「处理中」
  useEffect(() => {
    if (!streaming) {
      setSlow(false);
      return;
    }
    const t = setTimeout(() => setSlow(true), SLOW_MS);
    return () => clearTimeout(t);
  }, [streaming, msg.id]);

  useEffect(() => () => {
    if (copyTimer.current) clearTimeout(copyTimer.current);
  }, []);

  const copyRequestId = () => {
    if (!r) return;
    void copyText(r.request_id).then((ok) => {
      setCopied(ok);
      if (copyTimer.current) clearTimeout(copyTimer.current);
      copyTimer.current = setTimeout(() => setCopied(false), COPIED_RESET_MS);
    });
  };

  // 生成期直播（§3.3：直播只在 L1 体现，不展开 L2）。成功路径步骤数不固定（D6 动态追加
  // 「数字校验」步），final 前总数未知——只报当前进度 n，不硬编码分母。
  const lastStep = msg.steps[msg.steps.length - 1];
  const liveText = msg.streamedText
    ? '生成回答中…'
    : lastStep
      ? `第 ${msg.steps.length} 步 · ${lastStep.title}`
      : '正在建立连接…';

  const checkSteps = r ? r.steps.filter((s) => s.title.includes('校验')) : [];
  const failedSteps = r ? r.steps.filter((s) => s.status === 'fail') : [];
  const toggleL2 = () => {
    if (msg.steps.length > 0 && !streaming) setL2Open((v) => !v);
  };

  const retryRow = (text: string) => (
    <div className="retryrow">
      <span className="badtext">{text}</span>
      <button className="evbtn" onClick={() => onRetry(msg.text)}>重试</button>
    </div>
  );

  const answer = () => {
    switch (status) {
      case 'loading':
        return msg.streamedText ? (
          <div className="ans" aria-busy="true">
            {msg.streamedText}
            <span className="cursor" aria-hidden="true" />
          </div>
        ) : (
          <div className="skeleton" aria-hidden="true" />
        );
      case 'success':
      case 'success_degraded':
        return (
          <div className="ans">
            {status === 'success_degraded' && <span className="warnbadge">本次由简化路由回答</span>}
            {r?.answer}
          </div>
        );
      case 'success_empty':
        return (
          <div className="ans emptybox">
            <span className="empty-ic" aria-hidden="true"><Icon name="inbox" size={18} /></span>
            该范围无数据
            <span className="hint">建议调整时间范围后重试。</span>
          </div>
        );
      case 'ask_param':
        return (
          <div className="ans">
            {r?.answer}
            <span className="chips-inline">
              {PARAM_CHIPS.map((m) => (
                <button key={m} onClick={() => onFollowUp(m + msg.text)}>{m}</button>
              ))}
            </span>
            <span className="hint">点击月份即自动续查。</span>
          </div>
        );
      case 'out_of_range':
        return (
          <div className="ans">
            {r?.answer}
            <span className="hint">数据边界来自语义层元数据，请调整查询范围。</span>
          </div>
        );
      case 'rejected':
        return <div className="ans">{r?.answer}</div>;
      case 'unregistered':
        return (
          <div className="ans">
            {r?.answer}
            <span className="hint">可将该问题提交为派生规则候选，纳入口径治理流程。</span>
          </div>
        );
      case 'validation_failed': {
        const comparisons = failedSteps.filter((s) => s.title.includes('校验'));
        return (
          <div className="ans">
            {r?.answer}
            {comparisons.length > 0 && (
              <div className="cmp">
                <div className="cmp-title">数值对照（宁可不答，不出假数）</div>
                {comparisons.map((s, i) => (
                  <div className="cmp-row" key={i}>{s.detail}</div>
                ))}
              </div>
            )}
          </div>
        );
      }
      case 'error':
        return retryRow(msg.error?.message ?? ERROR_COPY[msg.error?.code ?? ''] ?? DEFAULT_ERROR_TEXT);
      case 'interrupted':
        return retryRow('连接中断，本次回答未完成，可重试。');
      case 'canceled':
        return retryRow('已取消本次查询。');
    }
  };

  return (
    <div className="m ai">
      <div className="bub">
        {/* L1 摘要条：生成期动态进度；完成后 徽章 · 校验摘要 · 证据编号（hover 说明 + 点击复制）；点击展开/收起 L2 */}
        <div
          className={'l1bar' + (msg.steps.length > 0 && !streaming ? ' clickable' : '')}
          onClick={toggleL2}
          role={msg.steps.length > 0 && !streaming ? 'button' : undefined}
          aria-expanded={msg.steps.length > 0 && !streaming ? l2Open : undefined}
          title={msg.steps.length > 0 && !streaming ? '点击展开/收起决策过程' : undefined}
        >
          {streaming ? (
            <span className={'l1-live' + (slow ? ' slow' : '')}>
              <Icon name="loader" size={13} className="icon-spin" />
              {liveText}
              {slow && <em className="l1-breath">处理中</em>}
            </span>
          ) : (
            <>
              <span className={'badge path-' + (r?.path ?? status)}>
                <span className="dot" aria-hidden="true" />
                {badge}
              </span>
              {(status === 'success' || status === 'success_degraded') && checkSteps.length > 0 && (
                <span className="oktext">{checkSteps.length} 项校验全过</span>
              )}
              {r && (
                <button
                  className="req"
                  title={REQ_ID_HINT}
                  onClick={(e) => { e.stopPropagation(); copyRequestId(); }}
                >
                  {r.request_id}
                  <span className="req-ic">
                    {copied === null ? (
                      <><Icon name="copy" size={11} /> 复制</>
                    ) : copied ? (
                      <><Icon name="check" size={11} /> 已复制</>
                    ) : (
                      <><Icon name="x" size={11} /> 未复制</>
                    )}
                  </span>
                </button>
              )}
            </>
          )}
          <span className="l1-right">
            {!streaming && (
              <button className="evbtn" onClick={(e) => { e.stopPropagation(); setDrawerOpen(true); }}>
                详情
              </button>
            )}
            {msg.steps.length > 0 && !streaming && (
              <span className="l2hint">
                <Icon name="chevron-down" size={11} className={l2Open ? 'open' : undefined} />
                {l2Open ? '收起过程' : '展开过程'}
              </span>
            )}
          </span>
        </div>

        {/* 回答区 */}
        <div className="sec">
          <h4>回答</h4>
          {answer()}
        </div>

        {/* 数据区：有 rows 必显示（§4.2）；空结果显示空态；渲染器按规则 viz 字段分支（D7：图表与表格同源同一 rows） */}
        {(status === 'success' || status === 'success_degraded') && r && r.rows.length > 0 && (
          <div className="sec">
            <h4>返回数据</h4>
            {r.viz === 'bar' || r.viz === 'kpi'
              ? <Chart viz={r.viz} rows={r.rows} />
              : <DataTable rows={r.rows} />}
          </div>
        )}
        {status === 'success_empty' && (
          <div className="sec">
            <h4>返回数据</h4>
            <div className="tbl-empty">空结果集（0 行）</div>
          </div>
        )}

        {/* L2 决策过程：默认收起，点击 L1 展开/收起；编号连续（展示序 1..N，步数动态） */}
        {l2Open && msg.steps.length > 0 && (
          <div className="sec">
            <h4>决策过程（{msg.steps.length} 步）</h4>
            <StepList steps={msg.steps} />
          </div>
        )}
      </div>
      {drawerOpen && <DetailDrawer msg={msg} onClose={() => setDrawerOpen(false)} />}
    </div>
  );
}