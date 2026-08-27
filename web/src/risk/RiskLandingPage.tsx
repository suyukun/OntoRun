// 价值 Landing 页（/）—— 安平金控风险管理部 · 风险预警系统
// 深色金融风控"指挥中心"质感：雷达预警隐喻 + 真实数据 + 三大入口 + 语义接口价值锚定。
// 数据全部来自物化快照（ap_anping 同源），不写假数字。
import { Button, Spin, Tag } from 'antd';
import {
  ArrowRightOutlined,
  AuditOutlined,
  ClusterOutlined,
  DatabaseOutlined,
  MessageOutlined,
  SafetyCertificateOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import './risk.css';
import { RISK_COLORS } from './riskTheme';
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

function RadarMotif() {
  return (
    <div className="risk-radar" aria-hidden>
      <div className="risk-radar-sweep" />
      <div className="risk-radar-blink" />
      <div className="risk-radar-blink amber" />
    </div>
  );
}

export default function RiskLandingPage() {
  const navigate = useNavigate();
  const { data, loading } = useRiskSnapshot();
  const stats = useStats(data);

  const go = (to: string) => navigate(to);

  return (
    <div className="risk-bg" style={{ minHeight: '100vh', color: RISK_COLORS.text }}>
      {/* ---------- Hero（左文右雷达，非居中模板） ---------- */}
      <section
        style={{
          position: 'relative',
          overflow: 'hidden',
          padding: '64px 48px 40px',
          maxWidth: 1180,
          margin: '0 auto',
        }}
      >
        <div className="risk-bg-grid" style={{ position: 'absolute', inset: 0 }} />
        <div style={{ position: 'relative', display: 'flex', alignItems: 'center', gap: 56, flexWrap: 'wrap' }}>
          <div style={{ flex: '1 1 460px', minWidth: 300 }}>
            <div className="risk-fade-up">
              <span
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 8,
                  fontSize: 12,
                  letterSpacing: '0.18em',
                  color: RISK_COLORS.textDim,
                  textTransform: 'uppercase',
                  border: '1px solid ' + RISK_COLORS.border,
                  padding: '6px 12px',
                  borderRadius: 4,
                  background: 'rgba(242,176,76,0.06)',
                }}
              >
                <span className="risk-dot" /> {EYEBROW}
              </span>
            </div>
            <h1
              className="risk-fade-up d1"
              style={{
                fontSize: 44,
                lineHeight: 1.12,
                fontWeight: 700,
                letterSpacing: '-0.02em',
                margin: '20px 0 16px',
                maxWidth: 520,
              }}
            >
              风险预警系统
              <br />
              <span className="risk-gradient-text">本体驱动 · 人机双签 · 全程可审计</span>
            </h1>
            <p className="risk-fade-up d2" style={{ fontSize: 17, color: RISK_COLORS.textDim, margin: '0 0 28px', maxWidth: 520, lineHeight: 1.7 }}>
              {ONE_LINER}
            </p>
            <div className="risk-fade-up d3" style={{ display: 'flex', gap: 14, flexWrap: 'wrap', alignItems: 'center' }}>
              <Button
                type="primary"
                size="large"
                icon={<ThunderboltOutlined />}
                style={{ height: 46, paddingInline: 26, fontWeight: 600, background: RISK_COLORS.accent, borderColor: RISK_COLORS.accent, color: RISK_COLORS.accentText }}
                onClick={() => go('/risk/chat')}
              >
                开始演示
              </Button>
              <Button
                size="large"
                icon={<ArrowRightOutlined />}
                style={{ height: 46, paddingInline: 22, background: 'transparent', borderColor: RISK_COLORS.border, color: RISK_COLORS.text }}
                onClick={() => go('/risk/browse')}
              >
                浏览风险数据
              </Button>
            </div>
          </div>
          <div className="risk-fade-up d4" style={{ flex: '0 0 auto', margin: '0 auto' }}>
            <RadarMotif />
            <div style={{ textAlign: 'center', marginTop: 14, color: RISK_COLORS.textFaint, fontSize: 12, letterSpacing: '0.1em' }}>
              实时风险监测 · 2026
            </div>
          </div>
        </div>
      </section>

      {/* ---------- 真实数据带（同源计数，非手写） ---------- */}
      <section style={{ borderTop: '1px solid ' + RISK_COLORS.border, borderBottom: '1px solid ' + RISK_COLORS.border, background: RISK_COLORS.surface }}>
        <div style={{ maxWidth: 1180, margin: '0 auto', padding: '22px 48px', display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', gap: 18 }}>
          {stats.map((s) => (
            <div key={s.label} style={{ minWidth: 150 }}>
              <div style={{ fontSize: 11, color: RISK_COLORS.textFaint, marginBottom: 6, letterSpacing: '0.08em' }}>{s.label}</div>
              <div className="risk-num" style={{ fontSize: 26, fontWeight: 700, color: RISK_COLORS.accent }}>
                {loading || s.value == null ? <Spin size="small" /> : formatCount(s.value)}
                <span style={{ fontSize: 13, color: RISK_COLORS.textDim, marginLeft: 4, fontWeight: 400 }}>{s.unit}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ---------- 演示入口（问问题为大卡，数据/操作/DES 地基并排） ---------- */}
      <section style={{ maxWidth: 1180, margin: '0 auto', padding: '52px 48px 16px' }}>
        <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: 22 }}>
          <div>
            <div style={{ fontSize: 13, color: RISK_COLORS.accent, letterSpacing: '0.12em', marginBottom: 6 }}>演示入口</div>
            <h2 style={{ fontSize: 26, margin: 0, fontWeight: 700 }}>能问、能办、能追</h2>
          </div>
          <div style={{ color: RISK_COLORS.textFaint, fontSize: 13 }}>AI 只经业务本体理解与操作，不直接碰库</div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1.35fr 1fr 1fr 1fr', gap: 18, gridAutoRows: 'minmax(150px, auto)' }}>
          <button
            className="risk-entry-card"
            onClick={() => go('/risk/chat')}
            style={{
              ...panel(),
              textAlign: 'left', cursor: 'pointer', padding: 24,
              borderTop: '2px solid ' + RISK_COLORS.accent,
            }}
            aria-label="问问题：自然语言精准问答与动作双签"
          >
            <div style={{ fontSize: 30, marginBottom: 12 }}><MessageOutlined style={{ color: RISK_COLORS.accent }} /></div>
            <div style={{ fontSize: 19, fontWeight: 700, marginBottom: 8 }}>问问题 · 双签执行</div>
            <div style={{ color: RISK_COLORS.textDim, fontSize: 13.5, lineHeight: 1.7 }}>
              用自然语言精准问答："本月红色预警几条？中科智造集团集中度多少？"
              高风险动作只提议不擅动，参数卡片 + 人机双签后才执行，全程留痕。
            </div>
            <div style={{ marginTop: 14, color: RISK_COLORS.accent, fontSize: 13 }}>
              进入对话窗口 <ArrowRightOutlined style={{ fontSize: 11 }} />
            </div>
          </button>
          <button
            className="risk-entry-card"
            onClick={() => go('/risk/browse')}
            style={{ ...panel(), textAlign: 'left', cursor: 'pointer', padding: 24, borderTop: '2px solid ' + RISK_COLORS.blue }}
            aria-label="看数据：按业务对象浏览真实风险数据"
          >
            <div style={{ fontSize: 30, marginBottom: 12 }}><DatabaseOutlined style={{ color: RISK_COLORS.blue }} /></div>
            <div style={{ fontSize: 19, fontWeight: 700, marginBottom: 8 }}>看数据</div>
            <div style={{ color: RISK_COLORS.textDim, fontSize: 13.5, lineHeight: 1.7 }}>
              客户、集团、预警、处置、审批、风险项目全链路浏览，按链接一路点下去，无孤岛。
            </div>
            <div style={{ marginTop: 14, color: RISK_COLORS.blue, fontSize: 13 }}>
              浏览数据 <ArrowRightOutlined style={{ fontSize: 11 }} />
            </div>
          </button>
          <button
            className="risk-entry-card"
            onClick={() => go('/risk/chat')}
            style={{ ...panel(), textAlign: 'left', cursor: 'pointer', padding: 24, borderTop: '2px solid ' + RISK_COLORS.red }}
            aria-label="执行操作：真实写回与审计"
          >
            <div style={{ fontSize: 30, marginBottom: 12 }}><SafetyCertificateOutlined style={{ color: RISK_COLORS.red }} /></div>
            <div style={{ fontSize: 19, fontWeight: 700, marginBottom: 8 }}>
              执行操作 <Tag color="volcano" style={{ marginLeft: 6 }}>双签</Tag>
            </div>
            <div style={{ color: RISK_COLORS.textDim, fontSize: 13.5, lineHeight: 1.7 }}>
              确认预警、调整等级、提交处置、推进审批——动作真实写回源数据并落审计，出问题可追溯。
            </div>
            <div style={{ marginTop: 14, color: RISK_COLORS.red, fontSize: 13 }}>
              试一次处置 <ArrowRightOutlined style={{ fontSize: 11 }} />
            </div>
          </button>
          <button
            className="risk-entry-card"
            onClick={() => go('/des')}
            style={{ ...panel(), textAlign: 'left', cursor: 'pointer', padding: 24, borderTop: '2px solid ' + RISK_COLORS.green }}
            aria-label="看地基：DES 企业模拟总览"
          >
            <div style={{ fontSize: 30, marginBottom: 12 }}><ClusterOutlined style={{ color: RISK_COLORS.green }} /></div>
            <div style={{ fontSize: 19, fontWeight: 700, marginBottom: 8 }}>看地基 · 企业模拟</div>
            <div style={{ color: RISK_COLORS.textDim, fontSize: 13.5, lineHeight: 1.7 }}>
              整家企业的客户、风险、审批数据都由 DES 确定性流水线模拟生成——画像、业务域、流程、规则到数据。看清数据地基与生成锚点。
            </div>
            <div style={{ marginTop: 14, color: RISK_COLORS.green, fontSize: 13 }}>
              进入企业模拟总览 <ArrowRightOutlined style={{ fontSize: 11 }} />
            </div>
          </button>
        </div>
      </section>

      {/* ---------- 语义接口价值锚定（本体驱动 UI） ---------- */}
      <section style={{ maxWidth: 1180, margin: '0 auto', padding: '56px 48px 40px' }}>
        <div style={panel()}>
          <div style={{ padding: 28, display: 'flex', gap: 40, flexWrap: 'wrap' }}>
            <div style={{ flex: '1 1 380px', minWidth: 280 }}>
              <div style={{ fontSize: 13, color: RISK_COLORS.accent, letterSpacing: '0.12em', marginBottom: 8 }}>研究价值锚定</div>
              <h2 style={{ fontSize: 24, margin: '0 0 14px', fontWeight: 700 }}>语义接口层：AI 与业务之间的一层"业务语义"</h2>
              <p style={{ color: RISK_COLORS.textDim, fontSize: 14.5, lineHeight: 1.8, margin: 0 }}>
                系统先建一层业务本体（对象 / 链接 / 动作）。AI 问什么、做什么，都通过这层语义理解——
                所以答得准（可表达集内精准）、做得稳（动作参数白名单校验）、留得住（每一步写审计）。
                换个数据源、换个系统，本体不变，界面跟着变。
              </p>
            </div>
            <div style={{ flex: '1 1 420px', minWidth: 300 }}>
              <div style={{ fontSize: 13, color: RISK_COLORS.textDim, marginBottom: 12 }}>一条可追溯的处置链路</div>
              {[
                ['集团客户', '中科智造产业发展集团', '中科智造产业发展集团 · GRP-2026-000001'],
                ['预警信号', '押品贬值 → 黄色预警', '确认 → 定级'],
                ['处置 + 审批', '追加担保 · 压降敞口', '风险预警管理岗 → 部门 → 集团'],
                ['审计留痕', '动作写回源数据', '审计号可追溯 · 出问题能追责'],
              ].map(([t, a, b], i) => (
                <div key={t} style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 10 }}>
                  <div
                    style={{
                      width: 34, height: 34, borderRadius: 6, display: 'flex', alignItems: 'center', justifyContent: 'center',
                      background: i === 3 ? 'rgba(61,220,151,0.12)' : 'rgba(242,176,76,0.10)',
                      border: '1px solid ' + (i === 3 ? RISK_COLORS.green : RISK_COLORS.accent),
                      color: i === 3 ? RISK_COLORS.green : RISK_COLORS.accent, fontSize: 12, flex: '0 0 auto',
                    }}
                  >
                    {i + 1}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 13.5, fontWeight: 600 }}>{t} <span style={{ color: RISK_COLORS.textFaint, fontWeight: 400 }}>· {b}</span></div>
                    <div style={{ fontSize: 12.5, color: RISK_COLORS.textDim }}>{a}</div>
                  </div>
                  {i < 3 && <ArrowRightOutlined style={{ color: RISK_COLORS.textFaint, fontSize: 12 }} />}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ---------- 页脚（价值一句话 + 零售入口） ---------- */}
      <footer style={{ borderTop: '1px solid ' + RISK_COLORS.border, padding: '26px 48px', color: RISK_COLORS.textFaint, fontSize: 12.5, maxWidth: 1180, margin: '0 auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 10, alignItems: 'center' }}>
          <span>
            <AuditOutlined style={{ marginRight: 6, color: RISK_COLORS.accent }} />
            语义接口层：LLM 经业务本体理解与操作，不直接碰库
          </span>
          <button
            onClick={() => go('/browse')}
            style={{ background: 'transparent', border: '1px solid ' + RISK_COLORS.border, color: RISK_COLORS.textDim, borderRadius: 4, padding: '6px 12px', cursor: 'pointer', fontSize: 12.5 }}
          >
            零售供应链演示（S1）
          </button>
        </div>
      </footer>
    </div>
  );
}

function panel() {
  return {
    background: RISK_COLORS.panel,
    border: '1px solid ' + RISK_COLORS.border,
    borderRadius: 6,
  };
}
