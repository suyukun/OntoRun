import { useState } from 'react';
import { DEFAULT_PATH_LABELS } from '../mock/profile';
import { deriveStatus, type AiStatus } from '../state/deriveStatus';
import type { ChatMessage } from '../types';
import { DataTable } from './DataTable';
import { DetailDrawer } from './DetailDrawer';

interface Props {
  msg: ChatMessage;
  pathLabels: Record<string, string>;
  onRetry: (q: string) => void;
  onFollowUp: (q: string) => void;
}

const STATUS_TEXT: Partial<Record<AiStatus, string>> = {
  error: '服务异常',
  interrupted: '已中断',
  canceled: '已取消',
};

/** 参数追问 chips（占位：真实 chips 按裁决由规则表生成，T4/T5 接入；选中即续查） */
const PARAM_CHIPS = ['8月', '7月'];

/** AI 消息卡（§3.2）：L1 摘要条 → 回答区 → 数据区 → L2 决策过程（收起）→ L3 抽屉。 */
export function MessageCard({ msg, pathLabels, onRetry, onFollowUp }: Props) {
  const [l2Open, setL2Open] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const status = deriveStatus(msg);
  const r = msg.result;
  const badge = r ? (pathLabels[r.path] ?? DEFAULT_PATH_LABELS[r.path] ?? r.path) : (STATUS_TEXT[status] ?? status);
  const checks = r ? r.steps.filter((s) => s.title === '结果校验' && s.status === 'ok') : [];
  const streaming = status === 'loading';
  const l1Live = msg.streamedText.length > 0 ? '⏳ 生成回答中…' : '⏳ 校验中 · 第 ' + msg.steps.length + '/' + (msg.steps.length + 1) + ' 步';

  const answer = () => {
    switch (status) {
      case 'loading':
        return msg.streamedText ? (
          <div className="ans">
            {msg.streamedText}
            <span className="cursor" />
          </div>
        ) : (
          <div className="skeleton" />
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
        return <div className="ans empty-tip">该范围无数据。建议调整时间范围后重试。</div>;
      case 'ask_param':
        return (
          <div className="ans">
            {r?.answer}
            <span className="chips-inline">
              {PARAM_CHIPS.map((m) => (
                <button key={m} onClick={() => onFollowUp(m + msg.text)}>
                  {m}
                </button>
              ))}
            </span>
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
            <span className="hint">可提交规则候选（引导占位——T3 接入）。</span>
          </div>
        );
      case 'validation_failed':
        return (
          <div className="ans">
            {r?.answer}
            <span className="hint">数值对照见 L2 校验步骤——宁可不答，不出假数。</span>
          </div>
        );
      case 'error':
        return (
          <div className="ans">
            <span className="badtext">{msg.error?.message ?? '查询失败：服务未响应'}</span>
            <button className="evbtn" onClick={() => onRetry(msg.text)}>
              重试
            </button>
          </div>
        );
      case 'interrupted':
        return (
          <div className="ans">
            <span className="badtext">连接已中断，半成品已丢弃。</span>
            <button className="evbtn" onClick={() => onRetry(msg.text)}>
              重试
            </button>
          </div>
        );
      case 'canceled':
        return (
          <div className="ans">
            已取消本次查询。
            <button className="evbtn" onClick={() => onRetry(msg.text)}>
              重试
            </button>
          </div>
        );
    }
  };

  return (
    <div className="m ai">
      <div className="bub">
        {/* L1 摘要条：生成期动态「第 n/N 步」；完成后 路径徽章 + 校验摘要 + 证据编号；点击展开/收起 L2 */}
        <div
          className="l1bar"
          onClick={() => { if (msg.steps.length > 0) setL2Open((v) => !v); }}
          title={msg.steps.length > 0 ? '点击展开/收起决策过程（L2）' : undefined}
        >
          {streaming ? (
            <span className="l1-live">{l1Live}</span>
          ) : (
            <>
              <span className={'badge path-' + (r?.path ?? 'error')}>{badge}</span>
              {status === 'success' && checks.length > 0 && <span className="oktext">{checks.length} 项校验全过</span>}
              {status === 'success_degraded' && checks.length > 0 && <span className="oktext">{checks.length} 项校验全过</span>}
              {(status === 'error' || status === 'interrupted' || status === 'canceled') && (
                <span className="badtext">{STATUS_TEXT[status]}</span>
              )}
              {r && <span className="req">{r.request_id} ⧉</span>}
            </>
          )}
          <span className="l1-right">
            {!streaming && (
              <button
                className="evbtn"
                onClick={(e) => { e.stopPropagation(); setDrawerOpen(true); }}
              >
                详情
              </button>
            )}
            {msg.steps.length > 0 && <span className="l2hint">L2 {l2Open ? '▲' : '▼'}</span>}
          </span>
        </div>

        {/* 回答区 */}
        <div className="sec">
          <h4>回答</h4>
          {answer()}
        </div>

        {/* 数据区：有 rows 必显示（§4.2）；空结果走空态文案 */}
        {(status === 'success' || status === 'success_degraded') && r && r.rows.length > 0 && (
          <div className="sec">
            <h4>返回数据</h4>
            <DataTable rows={r.rows} />
          </div>
        )}

        {/* L2 决策过程：默认收起；编号按展示序连续递增（§七.3 无跳号） */}
        {l2Open && msg.steps.length > 0 && (
          <div className="sec">
            <h4>决策过程（L2）</h4>
            <div className="steps">
              {msg.steps.map((s, i) => (
                <div className="stp" key={i}>
                  <span className={'st ' + s.status}>{s.status}</span>
                  <b>
                    {i + 1} {s.title}
                  </b>{' '}
                  {s.detail}
                  {s.sql ? <pre>{s.sql}</pre> : null}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
      {drawerOpen && <DetailDrawer msg={msg} onClose={() => setDrawerOpen(false)} />}
    </div>
  );
}
