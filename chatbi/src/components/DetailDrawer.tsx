import { useEffect, useRef, useState } from 'react';
import { Icon } from './Icon';
import { BUSINESS_PATH_LABELS, REQ_ID_HINT, copyText } from './labels';
import type { ChatMessage } from '../types';

const COPIED_RESET_MS = 1600;

/**
 * 详情抽屉 = 审计视图（UX 2026-09-09 重定位）：回答「凭什么信/怎么复现」。
 * 决策步骤已在消息卡思考区展示，此处不再重复；这里收口径与校验、SQL、证据编号与元信息。
 */
export function DetailDrawer({ msg, onClose }: { msg: ChatMessage; onClose: () => void }) {
  const r = msg.result;
  const [copied, setCopied] = useState<boolean | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Esc 关闭（P2-7 抽屉键盘可达性）
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [onClose]);

  useEffect(() => () => {
    if (timer.current) clearTimeout(timer.current);
  }, []);

  const copyRequestId = () => {
    if (!r) return;
    void copyText(r.request_id).then((ok) => {
      setCopied(ok);
      if (timer.current) clearTimeout(timer.current);
      timer.current = setTimeout(() => setCopied(null), COPIED_RESET_MS);
    });
  };

  const caliber = msg.steps.find((s) => s.title === '口径声明')?.detail;
  const validations = msg.steps.filter((s) => s.title.includes('校验'));
  const pathText = (r?.tables ?? []).map((t) => t.layer + ' · ' + t.name).join('，') || '—';

  return (
    <>
      <div className="drawer-mask" onClick={onClose} />
      <div className="drawer" role="dialog" aria-label="查询详情">
        <div className="drawer-head">
          <b>查询详情 · {(msg.text || '').slice(0, 24)}{(msg.text || '').length > 24 ? '…' : ''}</b>
          <button className="opbtn" aria-label="关闭" onClick={onClose}><Icon name="x" size={14} /></button>
        </div>
        <div className="drawer-body">
          <div className="meta">
            <div>
              <b>证据编号</b>
              <span>
                {r?.request_id ?? '—'}
                {r && (
                  <button className="meta-copy" title={REQ_ID_HINT} onClick={copyRequestId}>
                    <Icon name={copied === true ? 'check' : 'copy'} size={11} />
                    {copied === true ? '已复制' : copied === false ? '未复制' : '复制'}
                  </button>
                )}
              </span>
            </div>
            <div><b>发起时间</b><span>{r?.started_at || '—'}</span></div>
            {r?.total_ms != null && <div><b>总耗时</b><span>{(r.total_ms / 1000).toFixed(2)}s</span></div>}
            <div><b>数据路径</b><span>{pathText}</span></div>
          </div>

          <div className="basis">
            <div>
              <b>口径说明：</b>{caliber ?? '—'}
            </div>
            <div>
              <b>命中规则：</b>{r?.rule ?? '—'}
              {r && r.path && <span className="basis-path">（{BUSINESS_PATH_LABELS[r.path] ?? r.path}）</span>}
            </div>
            <div className="basis-checks">
              <b>校验记录：</b>
              {validations.length > 0 ? (
                <ul>
                  {validations.map((s, i) => (
                    <li key={i} className={s.status === 'ok' ? 'vok' : 'vbad'}>
                      <Icon name={s.status === 'ok' ? 'check' : 'x'} size={11} /> {s.detail.replace(/^[✓✗]\s*/, '')}
                    </li>
                  ))}
                </ul>
              ) : (
                '—'
              )}
            </div>
          </div>

          {r?.sql && (
            <div className="basis-sql">
              <b>执行 SQL（规则模板确定性编译，LLM 未参与）：</b>
              <pre className="sql">{r.sql}</pre>
            </div>
          )}

          <p className="hint">
            证据编号可完整复现本次过程与结果（报障/审计时报此编号）。LLM 原始输出经系统脱敏后记录；判断文字未经事实校验。
          </p>
        </div>
      </div>
    </>
  );
}
