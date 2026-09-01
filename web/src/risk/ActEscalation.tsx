// 第 2 幕 · 升级识别帧（第二个 money shot）—— 三线索汇聚 → 隐性一致行动人恒昌贸易 → 12.8% 红。
// 三条线索各一张证据卡；「点开证据链」真数据联动（/risk/reporting/draft 返回的 relation_clues =
// ap_customer_relation_tree.clear_remark_* 再生库实测值）。纳入归集后 AI 起草上调红色建议，人工确认生效。
import { Button, Spin, Tag } from 'antd';
import { CheckCircleFilled, DownOutlined, LinkOutlined, SafetyCertificateOutlined } from '@ant-design/icons';
import { useState } from 'react';
import { FrameShell, FrameSub } from './actFrame';
import { HENGCHANG_CLUES, HENGCHANG_TRADE, TIANSHENG, TIANSHENG_ESCALATED } from './sevenAct';
import { fetchReportingDraft } from './riskApi';
import type { HiddenRelatedParty, ReportingDraft } from './riskApi';
import LevelBadge from './LevelBadge';
import { RISK_COLORS as C } from './riskTheme';

export default function ActEscalation() {
  const [chainOpen, setChainOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [draft, setDraft] = useState<ReportingDraft | null>(null);

  const openChain = async () => {
    if (draft) {
      setChainOpen(true);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const d = await fetchReportingDraft(TIANSHENG.groupNo);
      setDraft(d);
      setChainOpen(true);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const hidden = draft?.hidden_related_parties?.find((h) => h.customer_name === HENGCHANG_TRADE.name);

  return (
    <FrameShell
      actNo="第 2 幕"
      title="升级识别：三线索交叉 → 隐性一致行动人恒昌贸易"
      subtitle="AI 交叉股权代持 / 交叉担保链 / 资金往来异动，识别出传统关联交易表里查不出来的隐性一致行动人。"
    >
      {/* 三线索证据卡 */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0,1fr))', gap: 12 }}>
        {HENGCHANG_CLUES.map((clue, i) => (
          <div
            key={clue.key}
            data-testid={'clue-card-' + clue.key}
            style={{ border: '1px solid ' + C.border, borderRadius: 8, background: C.surface, padding: 14 }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
              <span
                style={{
                  width: 24, height: 24, borderRadius: 6, flex: '0 0 auto',
                  display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                  background: C.accent + '14', border: '1px solid ' + C.accent + '44', color: C.accent, fontSize: 12, fontWeight: 600,
                }}
              >
                {i + 1}
              </span>
              <span style={{ fontWeight: 600, fontSize: 13.5 }}>{clue.title}</span>
            </div>
            <div style={{ fontSize: 12, color: C.textFaint, marginBottom: 6 }}>{clue.source}</div>
            <div style={{ fontSize: 12.5, color: C.textDim, lineHeight: 1.7 }}>{clue.text}</div>
          </div>
        ))}
      </div>

      {/* 证据链展开态（真数据联动） */}
      <div style={{ marginTop: 14 }}>
        <Button
          type="default"
          icon={chainOpen ? <DownOutlined rotate={180} /> : <LinkOutlined />}
          loading={loading}
          onClick={() => void openChain()}
          data-testid="open-evidence-chain"
        >
          点开证据链 · 看认定依据（ap_customer_relation_tree）
        </Button>
        {error && (
          <div data-testid="evidence-chain-error" style={{ marginTop: 10, fontSize: 12.5, color: C.red, background: C.red + '0D', border: '1px solid ' + C.red + '44', borderRadius: 6, padding: 10 }}>
            证据链加载失败：{error}（证据链为真数据联动，需后端 /risk/reporting/draft）
          </div>
        )}
        {chainOpen && !error && (
          <div
            data-testid="evidence-chain"
            className="risk-fade-up"
            style={{ marginTop: 10, border: '1px solid ' + C.accent + '55', borderRadius: 8, background: C.accent + '0A', padding: 14 }}
          >
            {loading ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, color: C.textDim, fontSize: 13 }}>
                <Spin size="small" /> 正在从再生库拉取关系树证据…
              </div>
            ) : (
              <EvidenceChain hidden={hidden} draft={draft} />
            )}
          </div>
        )}
      </div>

      {/* 纳入归集 → 12.8% 红 */}
      <FrameSub>纳入归集 · 重算集中度</FrameSub>
      <div
        data-testid="escalation-total"
        style={{ border: '1px solid ' + C.red + '66', borderRadius: 8, background: C.red + '0D', padding: 14 }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
          <span style={{ fontSize: 14, color: C.textDim }}>
            {TIANSHENG.consolidatedYi} 亿（天晟自身）+ {HENGCHANG_TRADE.balanceYi} 亿（恒昌）=
          </span>
          <span className="risk-num" style={{ fontSize: 22, fontWeight: 600 }}>{TIANSHENG_ESCALATED.consolidatedYi} 亿</span>
          <span style={{ color: C.textFaint }}>÷ 800 亿 =</span>
          <span className="risk-num" style={{ fontSize: 22, fontWeight: 600 }}>{TIANSHENG_ESCALATED.ratioPct}%</span>
          <LevelBadge level={TIANSHENG_ESCALATED.level} />
        </div>
        <div style={{ marginTop: 8, fontSize: 12.5, color: C.textDim, lineHeight: 1.7 }}>
          {TIANSHENG_ESCALATED.ratioPct}% &gt; 内部限额 12% → 红色预警；{TIANSHENG_ESCALATED.ruleBasis}
        </div>
        <div style={{ marginTop: 8, fontSize: 12.5, color: C.textFaint, lineHeight: 1.7 }}>{TIANSHENG_ESCALATED.note}</div>

        {/* AI 起草上调红色建议（人工确认生效） */}
        <div
          data-testid="escalation-proposal"
          style={{ marginTop: 12, border: '1px solid ' + C.border, borderRadius: 8, background: C.surface, padding: 12 }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
            <SafetyCertificateOutlined style={{ color: C.accent }} />
            <span style={{ fontWeight: 600, fontSize: 13.5 }}>AI 起草 · 上调红色建议</span>
            <Tag style={{ marginLeft: 'auto', background: C.red + '14', borderColor: C.red + '55', color: C.red }}>待风险管理部人工确认</Tag>
          </div>
          <div style={{ fontSize: 12.5, color: C.textDim, lineHeight: 1.7 }}>
            动作 adjust_warning_level · 预警信号 WS-2026-90000002 · 新等级 红 · 理由：纳入隐性关联方后归集集中度 12.8% 突破内部限额
          </div>
          <div style={{ marginTop: 8, display: 'flex', alignItems: 'center', gap: 6, fontSize: 12.5, color: C.green }}>
            <CheckCircleFilled /> 人工确认后生效——AI 只提议，不直接改数据。
          </div>
        </div>
      </div>
    </FrameShell>
  );
}

function EvidenceChain({ hidden, draft }: { hidden?: HiddenRelatedParty; draft: ReportingDraft | null }) {
  return (
    <div style={{ fontSize: 13, color: C.text }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
        <span style={{ fontWeight: 600, fontSize: 14 }}>{hidden?.customer_name ?? HENGCHANG_TRADE.name}</span>
        <span style={{ color: C.textFaint, fontSize: 12 }}>
          {HENGCHANG_TRADE.relationTreeIds.join(' / ')} · {HENGCHANG_TRADE.relationTreeTable}
        </span>
      </div>
      {hidden && (
        <div style={{ marginBottom: 10, fontSize: 12.5, color: C.textDim }}>
          归集余额（联合授信台账 × 客户关系树）：
          <span className="risk-num" style={{ fontWeight: 600, color: C.text }}>{hidden.balance_yi} 亿</span>
        </div>
      )}
      <FrameSub>关系线索（clear_remark_1/2/3 · 真数据）</FrameSub>
      <ul style={{ margin: 0, paddingLeft: 18, display: 'flex', flexDirection: 'column', gap: 6 }}>
        {(hidden?.relation_clues ?? []).map((c, i) => (
          <li key={i} style={{ fontSize: 12.5, color: C.textDim, lineHeight: 1.7 }}>{c}</li>
        ))}
      </ul>
      <FrameSub>触发规则</FrameSub>
      {(draft?.trigger_rules ?? []).map((r) => (
        <div key={r.rule} style={{ fontSize: 12.5, color: C.textDim, lineHeight: 1.7 }}>
          <span style={{ fontWeight: 600, color: C.text }}>{r.rule}</span> · {r.name} —— {r.basis}
          {r.lines && <span style={{ color: C.textFaint }}>（{r.lines}）</span>}
        </div>
      ))}
    </div>
  );
}

