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
  RESULT_BADGE_LABELS, copyText,
} from './labels';
import { StepList } from './StepList';
import { WAIT_EGGS } from './eggs';

interface Props {
  msg: ChatMessage;
  pathLabels: Record<string, string>;
  /** profile 示例问题（拒答时给出可点的换问引导） */
  examples?: string[];
  onRetry: (q: string) => void;
  onFollowUp: (q: string) => void;
}

/** 参数追问快捷 chips（§4.2 #3：选中即续查；P0 前端常量，规则表生成随 T5 接入）。 */
const PARAM_CHIPS = ['8月', '7月'];

/** §3.3：总决策 >2.5s 时追加「处理中」呼吸态（不自动展开思考区）。 */
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

/** rows → TSV（复制数据用：表头 + 行，制表符分隔，贴 Excel/微信即用） */
function rowsToTsv(rows: Record<string, unknown>[]): string {
  if (rows.length === 0) return '';
  const keys = Object.keys(rows[0]);
  return [keys.join('\t'), ...rows.map((r) => keys.map((k) => String(r[k] ?? '')).join('\t'))].join('\n');
}

/**
 * AI 消息卡（Agent 惯例交互，UX 2026-09-09 重构）：
 * 思考区（流式时展开直播步骤 → 首个回答 token 自动折叠 → 「已思考 N 步 · X.Xs」一行可再展开）
 * → 回答区 → 数据区（含复制）→ 操作行（详情）。req id 收进详情抽屉，不再常驻卡面。
 */
export function MessageCard({ msg, pathLabels, examples = [], onRetry, onFollowUp }: Props) {
  // 恢复/回放的消息以 done 态挂载 → 思考区收起；新消息流式挂载 → 展开直播
  const [thinkOpen, setThinkOpen] = useState(msg.phase === 'streaming');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [slow, setSlow] = useState(false);
  /** null=未操作，true/false=最近一次复制成败（三态反馈） */
  const [copiedData, setCopiedData] = useState<boolean | null>(null);
  /** 等待期彩蛋序号（起点按消息 id 错开，避免多卡同步换句） */
  const [eggIdx, setEggIdx] = useState((msg.id * 7) % WAIT_EGGS.length);
  const userToggled = useRef(false);
  const dataTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const status = deriveStatus(msg);
  const r = msg.result;
  const streaming = status === 'loading';
  const badge = badgeText(status, r, pathLabels);

  // 回答 token 开始输出 → 思考区自动折叠；终局（含无 token 的追问/拒答路径）同样折叠。
  // 用户手动展开/收起过则尊重用户选择。
  useEffect(() => {
    if (streaming && msg.streamedText && !userToggled.current) setThinkOpen(false);
  }, [streaming, msg.streamedText]);
  useEffect(() => {
    if (!streaming) setThinkOpen((v) => (userToggled.current ? v : false));
  }, [streaming]);

  // 等待期彩蛋轮换：仅流式且回答未开始时；1.8s 换句，回答一开始即停（不留痕）
  useEffect(() => {
    if (!streaming || msg.streamedText) return;
    const t = setInterval(() => setEggIdx((i) => i + 1), 1800);
    return () => clearInterval(t);
  }, [streaming, msg.streamedText]);

  // 呼吸态：本次流式超过阈值后追加「处理中」
  useEffect(() => {
    if (!streaming) {
      setSlow(false);
      return;
    }
    const t = setTimeout(() => setSlow(true), SLOW_MS);
    return () => clearTimeout(t);
  }, [streaming, msg.id]);

  useEffect(() => () => {
    if (dataTimer.current) clearTimeout(dataTimer.current);
  }, []);

  const copyData = () => {
    if (!r || r.rows.length === 0) return;
    void copyText(rowsToTsv(r.rows)).then((ok) => {
      setCopiedData(ok);
      if (dataTimer.current) clearTimeout(dataTimer.current);
      dataTimer.current = setTimeout(() => setCopiedData(null), COPIED_RESET_MS);
    });
  };

  // 生成期直播（§3.3：直播只在思考区头部体现）。成功路径步骤数不固定（D6 动态追加
  // 「数字校验」步），final 前总数未知——只报当前进度 n，不硬编码分母。
  const lastStep = msg.steps[msg.steps.length - 1];
  const liveText = msg.streamedText
    ? '生成回答中…'
    : lastStep
      ? `第 ${msg.steps.length} 步 · ${lastStep.title}`
      : '正在建立连接…';

  const secs = r?.total_ms != null ? r.total_ms / 1000 : msg.steps.reduce((a, s) => a + (s.ms ?? 0), 0) / 1000;
  const durText = secs >= 1 ? ` · ${secs.toFixed(1)}s` : '';

  const checkSteps = r ? r.steps.filter((s) => s.title.includes('校验')) : [];
  const failedSteps = r ? r.steps.filter((s) => s.status === 'fail') : [];
  const toggleThink = () => {
    if (msg.steps.length === 0) return;
    userToggled.current = true;
    setThinkOpen((v) => !v);
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
        return (
          <div className="ans">
            {r?.answer}
            {examples.length > 0 && (
              <span className="chips-inline">
                {examples.slice(0, 3).map((ex) => (
                  <button key={ex} onClick={() => onFollowUp(ex)}>{ex}</button>
                ))}
              </span>
            )}
            <span className="hint">点上方任一问题即可直接查询。</span>
          </div>
        );
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
        {/* 思考区头部：生成期直播进度；完成后「已思考 N 步」可展开；右侧徽章 + 校验摘要 */}
        <div
          className={'thinkbar' + (msg.steps.length > 0 ? ' clickable' : '')}
          onClick={toggleThink}
          role={msg.steps.length > 0 ? 'button' : undefined}
          aria-expanded={msg.steps.length > 0 ? thinkOpen : undefined}
          title={msg.steps.length > 0 ? '点击展开/收起决策过程' : undefined}
        >
          {streaming ? (
            <span className="think-live">
              <Icon name="loader" size={13} className="icon-spin" />
              {liveText}
              {slow && <em className="l1-breath">处理中</em>}
            </span>
          ) : (
            <>
              {msg.steps.length > 0 && (
                <Icon name="chevron-down" size={12} className={'think-chev' + (thinkOpen ? ' open' : '')} />
              )}
              <span className="think-done">
                {msg.steps.length > 0 ? `已思考 ${msg.steps.length} 步${durText}` : '未产生决策步骤'}
              </span>
            </>
          )}
          <span className="think-right">
            {!streaming && (
              <>
                <span className={'badge path-' + (r?.path ?? status)}>
                  <span className="dot" aria-hidden="true" />
                  {badge}
                </span>
                {(status === 'success' || status === 'success_degraded') && checkSteps.length > 0 && (
                  <span className="oktext">{checkSteps.length} 项校验全过</span>
                )}
              </>
            )}
          </span>
        </div>

        {/* 等待期彩蛋（Jack 2026-09-09）：星芒脉冲 + 轮换小字，回答开始即消失 */}
        {streaming && !msg.streamedText && (
          <div className="eggrow">
            <Icon name="spark" size={11} className="egg-spark" filled />
            <span>{WAIT_EGGS[eggIdx % WAIT_EGGS.length]}</span>
          </div>
        )}

        {/* 思考过程：流式时逐步直播追加；完成后默认折叠 */}
        {thinkOpen && msg.steps.length > 0 && (
          <div className="thinkbody">
            <StepList steps={msg.steps} />
          </div>
        )}

        {/* 回答区 */}
        <div className="sec">
          <h4>回答</h4>
          {answer()}
        </div>

        {/* 数据区：有 rows 必显示（§4.2）；渲染器按规则 viz 字段分支（D7：图表与表格同源同一 rows） */}
        {(status === 'success' || status === 'success_degraded') && r && r.rows.length > 0 && (
          <div className="sec">
            <div className="sechead">
              <h4>数据</h4>
              <button className="opbtn" onClick={copyData} title="复制为 TSV（表头+数据，可直接贴 Excel）">
                <Icon name="copy" size={12} />
                {copiedData === true ? '已复制' : copiedData === false ? '复制失败' : '复制'}
              </button>
            </div>
            {r.viz === 'bar' || r.viz === 'kpi'
              ? <Chart viz={r.viz} rows={r.rows} />
              : <DataTable rows={r.rows} />}
          </div>
        )}
        {status === 'success_empty' && (
          <div className="sec">
            <h4>数据</h4>
            <div className="tbl-empty">空结果集（0 行）</div>
          </div>
        )}

        {/* 操作行：详情（审计视图：口径/校验/SQL/证据编号） */}
        {!streaming && r && (
          <div className="actrow">
            <button className="actbtn" onClick={() => setDrawerOpen(true)}>
              详情
            </button>
          </div>
        )}
      </div>
      {drawerOpen && <DetailDrawer msg={msg} onClose={() => setDrawerOpen(false)} />}
    </div>
  );
}
