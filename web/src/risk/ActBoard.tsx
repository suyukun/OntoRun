// 第 6 幕 · 闭环 + 全局督办看板帧 —— 瑞华黄档完整解除链 + 前十大集团集中度排名 + 七态分布 + 超期数。
// 真数据联动：GET /risk/dashboard（全局聚合，含天晟 10.8% / 瑞华 9.4%）。
import { Alert, Button, Spin } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import { useCallback, useEffect, useState } from 'react';
import { FrameShell } from './actFrame';
import { BOARD_CLOSING_LINE, RUIHUA_YELLOW_CASE } from './sevenAct';
import { fetchRiskDashboard, pctOf, splitGroupSeq, toZhWarnLevel } from './riskApi';
import type { RiskDashboard } from './riskApi';
import LevelBadge from './LevelBadge';
import { SIGNAL_STATUS_META_ZH, RISK_COLORS as C } from './riskTheme';

export default function ActBoard() {
  const [board, setBoard] = useState<RiskDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const d = await fetchRiskDashboard();
      setBoard(d);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <FrameShell
      actNo="第 6 幕"
      title="闭环 + 全局督办看板"
      subtitle="小额黄档完整解除关闭 + 前十大集团集中度排名 / 七态分布 / 超期督办数 / 附属机构响应时效。"
    >
      {/* 瑞华黄档闭环 */}
      <div data-testid="act6-ruihua" style={{ border: '1px solid ' + C.yellow + '66', borderRadius: 8, background: C.yellow + '0D', padding: 12, marginBottom: 14 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap', marginBottom: 8 }}>
          <LevelBadge level="黄" />
          <span style={{ fontWeight: 600, fontSize: 14 }}>{RUIHUA_YELLOW_CASE.name} · 完整解除关闭</span>
          <span className="risk-num" style={{ fontSize: 13, color: C.textDim }}>{RUIHUA_YELLOW_CASE.ratioPct}%（关注线以上 · 黄档）</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap', fontSize: 12.5, color: C.textDim }}>
          {RUIHUA_YELLOW_CASE.chain.map((s, i) => (
            <span key={i} style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
              {i > 0 && <span style={{ color: C.textFaint }}>→</span>}
              <span>{s}</span>
            </span>
          ))}
        </div>
        <div style={{ marginTop: 6, fontSize: 12, color: C.textFaint }}>{RUIHUA_YELLOW_CASE.closing}</div>
      </div>

      {loading && (
        <div data-testid="act6-loading" style={{ display: 'flex', alignItems: 'center', gap: 10, color: C.textDim, padding: '20px 0' }}>
          <Spin /> 正在从再生库聚合全局督办看板…
        </div>
      )}

      {error && !loading && (
        <div data-testid="act6-error">
          <Alert
            type="error"
            showIcon
            title="督办看板加载失败"
            description={error + '（看板为真数据联动，需后端 /risk/dashboard）'}
            action={
              <Button size="small" icon={<ReloadOutlined />} onClick={() => void load()}>
                重试
              </Button>
            }
          />
        </div>
      )}

      {board && !loading && !error && (
        <div data-testid="act6-board">
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap', marginBottom: 6 }}>
            <span style={{ fontSize: 12.5, color: C.textFaint }}>
              数据时点 {board.as_of_date} · 并表资本 {board.capital.group_consolidated_capital_yi} 亿 · 超期阈值 {board.overdue_days_threshold} 天
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1.4fr) minmax(0,1fr)', gap: 14 }}>
            {/* 前十大集团集中度排名 */}
            <div style={{ border: '1px solid ' + C.border, borderRadius: 8, background: C.surface, overflow: 'hidden' }}>
              <div style={{ padding: '10px 12px', borderBottom: '1px solid ' + C.border, background: C.panelAlt, fontSize: 13, fontWeight: 600 }}>
                前十大集团客户集中度排名
              </div>
              <table data-testid="ranking-table" style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12.5 }}>
                <thead>
                  <tr>
                    <th style={{ textAlign: 'left', padding: '8px 12px', color: C.textFaint, fontWeight: 500 }}>#</th>
                    <th style={{ textAlign: 'left', padding: '8px 12px', color: C.textFaint, fontWeight: 500 }}>集团客户</th>
                    <th style={{ textAlign: 'right', padding: '8px 12px', color: C.textFaint, fontWeight: 500 }}>归集余额</th>
                    <th style={{ textAlign: 'right', padding: '8px 12px', color: C.textFaint, fontWeight: 500 }}>集中度</th>
                    <th style={{ textAlign: 'center', padding: '8px 12px', color: C.textFaint, fontWeight: 500 }}>级别</th>
                  </tr>
                </thead>
                <tbody>
                  {board.group_concentration_ranking.map((g) => {
                    const lv = toZhWarnLevel(g.latest_warn_level);
                    return (
                      <tr key={g.rank} data-testid={'rank-row-' + g.rank} style={{ borderTop: '1px solid ' + C.borderSoft }}>
                        <td style={{ padding: '8px 12px', color: C.textFaint }}>{g.rank}</td>
                        <td style={{ padding: '8px 12px', fontWeight: 500 }}>
                          {/* F6 编号列展示：唯一后缀「（NN）」拆成独立编号元素，不再嵌在名称里像脚注 */}
                          {(() => {
                            const { base, seq } = splitGroupSeq(g.group_customer_name);
                            return (
                              <>
                                {base}
                                {seq && (
                                  <span data-testid={'group-seq-' + g.rank} style={{ marginLeft: 6, color: C.textFaint, fontSize: 11, fontWeight: 400 }}>
                                    〔{seq}〕
                                  </span>
                                )}
                              </>
                            );
                          })()}
                        </td>
                        <td className="risk-num" style={{ padding: '8px 12px', textAlign: 'right' }}>{g.consolidated_balance_yi} 亿</td>
                        <td className="risk-num" style={{ padding: '8px 12px', textAlign: 'right' }}>{pctOf(g.concentration_ratio)}</td>
                        <td style={{ padding: '8px 12px', textAlign: 'center' }}>
                          {lv ? <LevelBadge level={lv} size="sm" showDesc={false} /> : <span style={{ color: C.textFaint, fontSize: 12 }}>—</span>}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* 七态分布 + 超期数 */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div style={{ border: '1px solid ' + C.border, borderRadius: 8, background: C.surface, padding: 12 }}>
                <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 8 }}>预警信号七态分布</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {Object.entries(board.signal_status_distribution).map(([status, n]) => {
                    const meta = SIGNAL_STATUS_META_ZH[status] ?? { color: C.textFaint, label: status };
                    return (
                      <div key={status} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12.5 }}>
                        <span style={{ width: 8, height: 8, borderRadius: '50%', background: meta.color, flex: '0 0 auto' }} />
                        <span style={{ color: C.textDim, flex: 1 }}>{meta.label}</span>
                        <span className="risk-num" style={{ fontWeight: 600 }}>{n.toLocaleString('zh-CN')}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
              <div style={{ border: '1px solid ' + C.border, borderRadius: 8, background: C.surface, padding: 12 }}>
                <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 8 }}>超期督办</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6, fontSize: 12.5 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: C.textDim }}>待确认超期</span>
                    <span className="risk-num" style={{ fontWeight: 600 }}>{board.overdue.pending_confirm_overdue}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: C.textDim }}>处置中超期</span>
                    <span className="risk-num" style={{ fontWeight: 600 }}>{board.overdue.in_disposal_overdue}</span>
                  </div>
                </div>
              </div>
              <div style={{ border: '1px solid ' + C.border, borderRadius: 8, background: C.surface, padding: 12 }}>
                <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 8 }}>附属机构响应时效</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6, fontSize: 12.5 }}>
                  {board.subsidiary_response.slice(0, 5).map((s) => (
                    <div key={s.org_name} style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: C.textDim }}>{s.org_name}</span>
                      <span className="risk-num" style={{ color: C.text }}>
                        滞留 {s.avg_open_age_days} 天 · 处置均 {s.avg_disposal_days} 天
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* 结尾一句 */}
          <div
            data-testid="act6-closing"
            style={{ marginTop: 14, padding: '12px 14px', borderRadius: 8, background: C.accent + '0A', border: '1px solid ' + C.accent + '55', fontSize: 14, color: C.text, lineHeight: 1.7 }}
          >
            {BOARD_CLOSING_LINE}
          </div>
        </div>
      )}
    </FrameShell>
  );
}
