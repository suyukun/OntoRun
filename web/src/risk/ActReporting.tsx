// 第 5 幕 · 监管动作帧 —— 红色预警触发监管报送初稿（大额风险暴露口径）+ 银团/联合贷款压降计划。
// 真数据联动：GET /risk/reporting/draft（天晟红色预警，2018 办法第三十七/三十四条文案来自后端同源）。
import { Alert, Button, Spin, Tag } from 'antd';
import { ReloadOutlined, SendOutlined, WarningFilled } from '@ant-design/icons';
import { useCallback, useEffect, useState } from 'react';
import { FrameShell, FrameSub } from './actFrame';
import { REPORTING_RED_WARNING_ID, REG_2018_ARTICLE_34, REG_2018_ARTICLE_37, SYNDICATED_REDUCTION_PLAN, TIANSHENG } from './sevenAct';
import { fetchReportingDraft, pctOf } from './riskApi';
import type { ReportingDraft } from './riskApi';
import LevelBadge from './LevelBadge';
import { RISK_COLORS as C } from './riskTheme';

export default function ActReporting() {
  const [draft, setDraft] = useState<ReportingDraft | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const d = await fetchReportingDraft(TIANSHENG.groupNo);
      setDraft(d);
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
      actNo="第 5 幕"
      title="监管动作：红色预警自动生成报送初稿"
      subtitle="大额风险暴露口径监管报送初稿（2018 办法第三十七/三十四条）+ 立即报告监管 + 银团/联合贷款压降计划。"
    >
      {loading && (
        <div data-testid="act5-loading" style={{ display: 'flex', alignItems: 'center', gap: 10, color: C.textDim, padding: '20px 0' }}>
          <Spin /> 正在从再生库生成监管报送初稿…
        </div>
      )}

      {error && !loading && (
        <div data-testid="act5-error">
          <Alert
            type="error"
            showIcon
            title="报送初稿加载失败"
            description={error + '（报送初稿为真数据联动，需后端 /risk/reporting/draft）'}
            action={
              <Button size="small" icon={<ReloadOutlined />} onClick={() => void load()}>
                重试
              </Button>
            }
          />
        </div>
      )}

      {draft && !loading && !error && (
        <div data-testid="act5-report">
          {/* 报送初稿头部 */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap', marginBottom: 12 }}>
            <span style={{ fontWeight: 600, fontSize: 16 }}>{draft.report_title}</span>
            <Tag style={{ background: C.red + '14', borderColor: C.red + '55', color: C.red }}>红色预警自动触发</Tag>
            <span style={{ marginLeft: 'auto', fontSize: 12, color: C.textFaint }}>预警信号 {REPORTING_RED_WARNING_ID} · 处置中 / 已督办</span>
          </div>

          {/* 大额风险暴露口径 */}
          <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1fr) minmax(0,1.2fr)', gap: 14 }}>
            <div style={{ border: '1px solid ' + C.border, borderRadius: 8, background: C.surface, padding: 14 }}>
              <div style={{ fontSize: 12, color: C.textFaint, letterSpacing: '0.1em', marginBottom: 10 }}>大额风险暴露 · 归集口径</div>
              {[
                ['集团自身归集', draft.consolidated_exposure.own_balance_yi + ' 亿'],
                ['隐性关联方（恒昌贸易）', draft.consolidated_exposure.hidden_related_party_balance_yi + ' 亿'],
                ['合计暴露', draft.consolidated_exposure.total_balance_yi + ' 亿'],
                ['集团并表资本', draft.consolidated_exposure.group_consolidated_capital_yi + ' 亿'],
                ['集中度', draft.consolidated_exposure.ratio_display],
              ].map(([k, v]) => (
                <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '7px 0', borderBottom: '1px solid ' + C.borderSoft }}>
                  <span style={{ fontSize: 12.5, color: C.textDim }}>{k}</span>
                  <span className="risk-num" style={{ fontSize: 13, fontWeight: 600 }}>{v}</span>
                </div>
              ))}
              <div style={{ marginTop: 10, display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ fontSize: 13, color: C.textDim }}>触发级别</span>
                <LevelBadge level="红" />
              </div>
            </div>

            {/* 逐家明细（单看都安全 → 合计超限） */}
            <div style={{ border: '1px solid ' + C.border, borderRadius: 8, background: C.surface, padding: 14 }}>
              <div style={{ fontSize: 12, color: C.textFaint, letterSpacing: '0.1em', marginBottom: 10 }}>联合授信台账逐家明细</div>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12.5 }}>
                <thead>
                  <tr>
                    <th style={{ textAlign: 'left', padding: '6px 8px', color: C.textFaint, fontWeight: 500 }}>机构</th>
                    <th style={{ textAlign: 'right', padding: '6px 8px', color: C.textFaint, fontWeight: 500 }}>归集余额</th>
                    <th style={{ textAlign: 'right', padding: '6px 8px', color: C.textFaint, fontWeight: 500 }}>参考线占比</th>
                    <th style={{ textAlign: 'left', padding: '6px 8px', color: C.textFaint, fontWeight: 500 }}>单看</th>
                  </tr>
                </thead>
                <tbody>
                  {draft.breakdown.map((b) => (
                    <tr key={b.org_name} style={{ borderTop: '1px solid ' + C.borderSoft }}>
                      <td style={{ padding: '6px 8px' }}>{b.org_name}</td>
                      <td className="risk-num" style={{ padding: '6px 8px', textAlign: 'right' }}>{b.balance_yi} 亿</td>
                      <td className="risk-num" style={{ padding: '6px 8px', textAlign: 'right' }}>
                        {b.org_reference_ratio != null ? pctOf(b.org_reference_ratio) : '—'}
                      </td>
                      <td style={{ padding: '6px 8px', color: C.green, fontSize: 12 }}>
                        {b.org_reference_ratio != null && b.org_reference_ratio < 0.1 ? '安全' : '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* 触发规则 + 依据条款 */}
          <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1fr) minmax(0,1fr)', gap: 14, marginTop: 14 }}>
            <div>
              <FrameSub>触发规则</FrameSub>
              {(draft.trigger_rules ?? []).map((r) => (
                <div key={r.rule} style={{ fontSize: 12.5, color: C.textDim, lineHeight: 1.7, marginBottom: 4 }}>
                  <span style={{ fontWeight: 600, color: C.text }}>{r.rule}</span> · {r.name}
                  {r.lines && <span style={{ color: C.textFaint }}>（{r.lines}）</span>}
                </div>
              ))}
            </div>
            <div>
              <FrameSub>依据条款</FrameSub>
              <div style={{ fontSize: 12.5, color: C.textDim, lineHeight: 1.7 }}>{REG_2018_ARTICLE_37}</div>
              <div style={{ fontSize: 12.5, color: C.textFaint, lineHeight: 1.7, marginTop: 6 }}>{REG_2018_ARTICLE_34}</div>
            </div>
          </div>

          {/* 监管动作面板 */}
          <div
            data-testid="act5-actions"
            style={{ marginTop: 14, border: '1px solid ' + C.accent + '55', borderRadius: 8, background: C.accent + '0A', padding: 14 }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
              <SendOutlined style={{ color: C.accent }} />
              <span style={{ fontWeight: 600, fontSize: 14 }}>监管动作 · 立即报告 + 银团压降</span>
            </div>
            <ol style={{ margin: 0, paddingLeft: 18, display: 'flex', flexDirection: 'column', gap: 6 }}>
              {SYNDICATED_REDUCTION_PLAN.steps.map((s, i) => (
                <li key={i} style={{ fontSize: 12.5, color: C.textDim, lineHeight: 1.7 }}>{s}</li>
              ))}
            </ol>
            <div style={{ marginTop: 8, display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: C.textFaint }}>
              <WarningFilled style={{ color: C.orange }} /> {SYNDICATED_REDUCTION_PLAN.note}
            </div>
          </div>
        </div>
      )}
    </FrameShell>
  );
}
