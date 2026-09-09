import { useState } from 'react';
import type { ChatMessage } from '../types';
import { DataTable } from './DataTable';

const TABS = ['决策过程', '结论依据', '返回数据'] as const;
type Tab = (typeof TABS)[number];

/** L3 详情抽屉：Tab 容器占位（脱敏 LLM 原始输出/完整 SQL/逐项耗时由 T3 精修）。 */
export function DetailDrawer({ msg, onClose }: { msg: ChatMessage; onClose: () => void }) {
  const [tab, setTab] = useState<Tab>('决策过程');
  const r = msg.result;
  return (
    <>
      <div className="drawer-mask" onClick={onClose} />
      <div className="drawer" role="dialog" aria-label="详情 L3">
        <div className="drawer-head">
          <b>详情（L3）· {msg.text}</b>
          <button className="opbtn" aria-label="关闭" onClick={onClose}>
            ×
          </button>
        </div>
        <div className="tabs">
          {TABS.map((t) => (
            <button key={t} className={t === tab ? 'on' : ''} onClick={() => setTab(t)}>
              {t}
            </button>
          ))}
        </div>
        <div className="drawer-body">
          {tab === '决策过程' && (
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
              <p className="hint">LLM 原始输出（脱敏后）/ 完整 SQL / 逐项耗时：T3 接入。</p>
            </div>
          )}
          {tab === '结论依据' && (
            <div className="basis">
              <div>
                <b>命中规则：</b>
                {r?.rule ?? '—'}
              </div>
              <div>
                <b>数据路径：</b>
                {(r?.tables ?? []).map((t) => t.layer + ' · ' + t.name).join('，') || '—'}
              </div>
              <div>
                <b>口径提示：</b>由 profile.rule_hints 装配——T3 接入。
              </div>
            </div>
          )}
          {tab === '返回数据' && (r && r.rows.length > 0 ? <DataTable rows={r.rows} /> : <p className="hint">无结果集</p>)}
        </div>
      </div>
    </>
  );
}
