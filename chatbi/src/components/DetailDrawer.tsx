import { useState } from 'react';
import { BUSINESS_PATH_LABELS } from './labels';
import type { ChatMessage } from '../types';
import { DataTable } from './DataTable';
import { StepList } from './StepList';

const TABS = ['决策过程全记录', '结论依据', '返回数据全量'] as const;
type Tab = (typeof TABS)[number];

function Meta({ msg }: { msg: ChatMessage }) {
  const r = msg.result;
  return (
    <div className="meta">
      <div><b>证据编号</b><span>{r?.request_id ?? '—'}</span></div>
      <div><b>发起时间</b><span>{r?.started_at || '—'}</span></div>
      <div><b>数据路径</b><span>{(r?.tables ?? []).map((t) => t.layer + ' · ' + t.name).join('，') || '—'}</span></div>
    </div>
  );
}

/** L3 详情抽屉（§3.2 #5）：决策过程全记录 / 结论依据 / 返回数据全量；与消息卡同源同数据。 */
export function DetailDrawer({ msg, onClose }: { msg: ChatMessage; onClose: () => void }) {
  const [tab, setTab] = useState<Tab>('决策过程全记录');
  const r = msg.result;
  const caliber = msg.steps.find((s) => s.title === '口径声明')?.detail;
  const validations = msg.steps.filter((s) => s.title.includes('校验'));

  return (
    <>
      <div className="drawer-mask" onClick={onClose} />
      <div className="drawer" role="dialog" aria-label="详情 L3">
        <div className="drawer-head">
          <b>详情（L3）· {msg.text}</b>
          <button className="opbtn" aria-label="关闭" onClick={onClose}>×</button>
        </div>
        <div className="tabs">
          {TABS.map((t) => (
            <button key={t} className={t === tab ? 'on' : ''} onClick={() => setTab(t)}>{t}</button>
          ))}
        </div>
        <div className="drawer-body">
          {tab === '决策过程全记录' && (
            <>
              <Meta msg={msg} />
              {msg.steps.length > 0 ? (
                <StepList steps={msg.steps} />
              ) : (
                <p className="hint">无步骤记录（流提前终止）。</p>
              )}
              <p className="hint">
                LLM 原始输出经系统脱敏后展示（防系统提示词/密钥泄露）；耗时为该步实测。判断文字未经事实校验。
              </p>
            </>
          )}
          {tab === '结论依据' && (
            <div className="basis">
              <div>
                <b>口径说明：</b>{caliber ?? '—'}
              </div>
              <div>
                <b>命中规则：</b>{r?.rule ?? '—'}
                {r && <span className="basis-path">（{BUSINESS_PATH_LABELS[r.path] ?? r.path}）</span>}
              </div>
              <div>
                <b>数据路径：</b>
                {(r?.tables ?? []).map((t) => t.layer + ' · ' + t.name).join('，') || '—'}
              </div>
              <div className="basis-checks">
                <b>校验记录：</b>
                {validations.length > 0 ? (
                  <ul>
                    {validations.map((s, i) => (
                      <li key={i} className={s.status === 'ok' ? 'vok' : 'vbad'}>
                        {s.status === 'ok' ? '✓' : '✗'} {s.detail.replace(/^[✓✗]\s*/, '')}
                      </li>
                    ))}
                  </ul>
                ) : (
                  '—'
                )}
              </div>
            </div>
          )}
          {tab === '返回数据全量' &&
            (r && r.rows.length > 0 ? <DataTable rows={r.rows} /> : <p className="hint">无结果集</p>)}
        </div>
      </div>
    </>
  );
}
