// 价值 Landing 页（/）—— 安平金控风险管理部 · 风险预警系统
// 浅色专业金融风（方向 A）：左对齐版式；安静的统计强调替代雷达 motif；
// 单一 CTA「开始演示」直达数据工作台；数据全部来自物化快照（ap_anping 同源），不写假数字。
import { Button, Spin } from 'antd';
import {
  ArrowRightOutlined,
  AuditOutlined,
  BarChartOutlined,
  ClusterOutlined,
  DatabaseOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import './risk.css';
import { RISK_COLORS as C } from './riskTheme';
import { useRiskSnapshot } from './riskData';
import type { RiskSnapshot } from './riskData';

const EYEBROW = '安平金控集团 · 风险管理部 · 风险预警系统';
const ONE_LINER = '用自然语言问风险问题、执行真实处置，全程本体驱动、可审计';

function useStats(snapshot: RiskSnapshot | null) {
  const t = snapshot?.totals ?? null;
  return [
    { label: '预警信号', value: t ? t.warning_signal : null, unit: '条' },
    { label: '风险客户', value: t ? t.risk_customer : null, unit: '户' },
    { label: '集团客户', value: t ? t.group_customer : null, unit: '家' },
    { label: '处置审批链路', value: t ? (t.approve_order ?? 0) + (t.disposal ?? 0) : null, unit: '条' },
    { label: '风控动作', value: snapshot ? snapshot.meta.actions.length : null, unit: '类' },
    { label: '实时可答域', value: t ? t.metric : null, unit: '行指标' },
  ] as { label: string; value: number | null; unit: string }[];
}

function formatCount(n: number | null | undefined): string {
  if (n == null) return '—';
  return n >= 10000 ? (n / 10000).toFixed(n % 10000 === 0 ? 0 : 1) + '万' : n.toLocaleString('zh-CN');
}

export default function RiskLandingPage() {
  const navigate = useNavigate();
  const { data, loading } = useRiskSnapshot();
  const stats = useStats(data);

  const go = (to: string) => navigate(to);
  const scrollToStats = () => {
    document.getElementById('risk-stats')?.scrollIntoView();
  };

  return (
    <div style={{ minHeight: '100vh', background: C.ink, color: C.text }}>
      {/* ---------- Hero（左对齐；文案不动） ---------- */}
      <section style={{ position: 'relative', overflow: 'hidden', maxWidth: 1180, margin: '0 auto', padding: '72px 48px 48px' }}>
        <span className="risk-fade-up" style={heroBadge()}>
          {EYEBROW}
        </span>
        <h1
          className="risk-fade-up d1"
          style={{ fontSize: 44, lineHeight: 1.12, fontWeight: 600, letterSpacing: '-0.01em', margin: '22px 0 16px', maxWidth: 560 }}
        >
          风险预警系统
          <br />
          本体驱动 · 人机双签 · 全程可审计
        </h1>
        <p className="risk-fade-up d2" style={{ fontSize: 17, color: C.textDim, margin: '0 0 28px', maxWidth: 520, lineHeight: 1.7 }}>
          {ONE_LINER}
        </p>
        {/* 单一 CTA：直达数据工作台 */}
        <div className="risk-fade-up d3">
          <Button
            type="primary"
            size="large"
            icon={<ThunderboltOutlined />}
            style={{ height: 46, paddingInline: 26, fontWeight: 600 }}
            onClick={() => go('/risk/browse')}
            aria-label="开始演示"
          >
            开始演示
          </Button>
        </div>
      </section>

      {/* ---------- 统计强调带（大数字 + 细分隔线；格子数=真实内容数，同源计数） ---------- */}
      <section id="risk-stats" style={{ borderTop: '1px solid ' + C.border, borderBottom: '1px solid ' + C.border, background: C.surface }}>
        <div style={{ maxWidth: 1180, margin: '0 auto', padding: '26px 48px', display: 'flex', flexWrap: 'wrap' }}>
          {stats.map((s, i) => (
            <div key={s.label} style={{ minWidth: 150, flex: '1 1 150px', paddingLeft: i > 0 ? 24 : 0, borderLeft: i > 0 ? '1px solid ' + C.border : undefined, paddingTop: 4, paddingBottom: 4 }}>
              <div style={{ fontSize: 11, color: C.textFaint, marginBottom: 8, letterSpacing: '0.08em' }}>{s.label}</div>
              <div className="risk-num" style={{ fontSize: 30, fontWeight: 600, letterSpacing: '-0.01em', color: C.text }}>
                {loading || s.value == null ? <Spin size="small" /> : formatCount(s.value)}
                <span style={{ fontSize: 13, color: C.textDim, marginLeft: 6, fontWeight: 400 }}>{s.unit}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ---------- 演示入口（三张卡：工作台 / 价值锚点 / 企业模拟） ---------- */}
      <section style={{ maxWidth: 1180, margin: '0 auto', padding: '52px 48px 16px' }}>
        <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: 22, flexWrap: 'wrap', gap: 8 }}>
          <div>
            <h2 style={{ fontSize: 26, margin: 0, fontWeight: 600, letterSpacing: '-0.01em' }}>能问、能办、能追</h2>
          </div>
          <div style={{ color: C.textFaint, fontSize: 13 }}>AI 只经业务本体理解与操作，不直接碰库</div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(220px, 1fr))', gap: 18, gridAutoRows: 'minmax(170px, auto)' }}>
          <button className="risk-entry-card" onClick={() => go('/risk/browse')} style={{ ...panel(), textAlign: 'left', cursor: 'pointer', padding: 24 }} aria-label="数据工作台：自然语言问答与风险数据浏览双栏">
            <div style={{ fontSize: 28, marginBottom: 12 }}><DatabaseOutlined style={{ color: C.accent }} /></div>
            <div style={{ fontSize: 18, fontWeight: 600, marginBottom: 8, letterSpacing: '-0.01em' }}>数据工作台 · 对话</div>
            <div style={{ color: C.textDim, fontSize: 13.5, lineHeight: 1.7 }}>
              左侧按业务对象浏览客户、集团、预警、处置全链路，沿链接一路点下去；右侧直接向系统提问并完成人机双签动作。
            </div>
            <div style={{ marginTop: 14, color: C.accent, fontSize: 13 }}>进入工作台 <ArrowRightOutlined style={{ fontSize: 11 }} /></div>
          </button>
          <button className="risk-entry-card" onClick={scrollToStats} style={{ ...panel(), textAlign: 'left', cursor: 'pointer', padding: 24 }} aria-label="价值统计锚点：回到本页顶部真实数据统计">
            <div style={{ fontSize: 28, marginBottom: 12 }}><BarChartOutlined style={{ color: C.accent }} /></div>
            <div style={{ fontSize: 18, fontWeight: 600, marginBottom: 8, letterSpacing: '-0.01em' }}>价值锚点 · 同源数据</div>
            <div style={{ color: C.textDim, fontSize: 13.5, lineHeight: 1.7 }}>
              上方统计带每个大数字都来自演示快照的真实计数——浏览页表格、对话回答与其完全同源，可以逐一对账。
            </div>
            <div style={{ marginTop: 14, color: C.accent, fontSize: 13 }}>回到统计带 <ArrowRightOutlined style={{ fontSize: 11 }} /></div>
          </button>
          <button className="risk-entry-card" onClick={() => go('/des')} style={{ ...panel(), textAlign: 'left', cursor: 'pointer', padding: 24 }} aria-label="看地基：DES 企业模拟总览">
            <div style={{ fontSize: 28, marginBottom: 12 }}><ClusterOutlined style={{ color: C.accent }} /></div>
            <div style={{ fontSize: 18, fontWeight: 600, marginBottom: 8, letterSpacing: '-0.01em' }}>看地基 · 企业模拟</div>
            <div style={{ color: C.textDim, fontSize: 13.5, lineHeight: 1.7 }}>
              整家企业的客户、风险、审批数据由 DES 确定性流水线模拟生成——画像、业务域、流程、规则到数据。
            </div>
            <div style={{ marginTop: 14, color: C.accent, fontSize: 13 }}>进入企业模拟总览 <ArrowRightOutlined style={{ fontSize: 11 }} /></div>
          </button>
        </div>
      </section>

      {/* ---------- 语义接口价值锚定（本体驱动 UI） ---------- */}
      <section style={{ maxWidth: 1180, margin: '0 auto', padding: '56px 48px 40px' }}>
        <div style={panel()}>
          <div style={{ padding: 28, display: 'flex', gap: 40, flexWrap: 'wrap' }}>
            <div style={{ flex: '1 1 380px', minWidth: 280 }}>
              <div style={{ fontSize: 12, color: C.textFaint, letterSpacing: '0.12em', marginBottom: 10 }}>研究价值锚定</div>
              <h2 style={{ fontSize: 24, margin: '0 0 14px', fontWeight: 600, letterSpacing: '-0.01em' }}>语义接口层：AI 与业务之间的一层"业务语义"</h2>
              <p style={{ color: C.textDim, fontSize: 14.5, lineHeight: 1.8, margin: 0 }}>
                系统先建一层业务本体（对象 / 链接 / 动作）。AI 问什么、做什么，都通过这层语义理解——
                所以答得准（可表达集内精准）、做得稳（动作参数白名单校验）、留得住（每一步写审计）。
                换个数据源、换个系统，本体不变，界面跟着变。
              </p>
            </div>
            <div style={{ flex: '1 1 420px', minWidth: 300 }}>
              <div style={{ fontSize: 13, color: C.textDim, marginBottom: 12 }}>一条可追溯的处置链路</div>
              {[
                ['集团客户', '中科智造产业发展集团', '中科智造产业发展集团 · GRP-2026-000001'],
                ['预警信号', '押品贬值 → 黄色预警', '确认 → 定级'],
                ['处置 + 审批', '追加担保 · 压降敞口', '风险预警管理岗 → 部门 → 集团'],
                ['审计留痕', '动作写回源数据', '审计号可追溯 · 出问题能追责'],
              ].map(([t, a, b], i) => (
                <div key={t} style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 10 }}>
                  <div
                    style={{
                      width: 34, height: 34, borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center',
                      background: C.accent + '14',
                      border: '1px solid ' + (i === 3 ? C.green : C.accent) + '66',
                      color: i === 3 ? C.green : C.accent, fontSize: 12, flex: '0 0 auto',
                    }}
                  >
                    {i + 1}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 13.5, fontWeight: 600 }}>{t} <span style={{ color: C.textFaint, fontWeight: 400 }}>· {b}</span></div>
                    <div style={{ fontSize: 12.5, color: C.textDim }}>{a}</div>
                  </div>
                  {i < 3 && <ArrowRightOutlined style={{ color: C.textFaint, fontSize: 12 }} />}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ---------- 页脚（价值一句话 + 零售入口） ---------- */}
      <footer style={{ borderTop: '1px solid ' + C.border, padding: '26px 48px', color: C.textFaint, fontSize: 12.5, maxWidth: 1180, margin: '0 auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 10, alignItems: 'center' }}>
          <span>
            <AuditOutlined style={{ marginRight: 6, color: C.accent }} />
            语义接口层：LLM 经业务本体理解与操作，不直接碰库
          </span>
          <button
            onClick={() => go('/browse')}
            style={{ background: 'transparent', border: '1px solid ' + C.border, color: C.textDim, borderRadius: 6, padding: '6px 12px', cursor: 'pointer', fontSize: 12.5 }}
          >
            零售供应链演示（S1）
          </button>
        </div>
      </footer>
    </div>
  );
}

function heroBadge(): React.CSSProperties {
  return {
    display: 'inline-flex', alignItems: 'center', gap: 8, fontSize: 12, letterSpacing: '0.14em',
    color: C.textDim, border: '1px solid ' + C.border, padding: '6px 12px', borderRadius: 6, background: C.surface,
  };
}

function panel() {
  return {
    background: C.panel,
    border: '1px solid ' + C.border,
    borderRadius: 8,
    boxShadow: '0 1px 2px rgba(16, 24, 40, 0.06)',
  };
}
