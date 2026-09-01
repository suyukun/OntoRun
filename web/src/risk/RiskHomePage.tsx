// 风险预警演示主页（/）—— Agent 对话 = 唯一一级入口（口径包§六：对象/链接/图谱降为对话证据链展开态）。
// 上半屏：Agent 对话（一句话归集）；下半屏：七幕剧本演示（处长 5 分钟）。
// 数据浏览 / 图谱 / DES 撤出门面菜单，仅作为本页页脚次级入口保留路由。
import { useNavigate } from 'react-router-dom';
import { ClusterOutlined, DatabaseOutlined, LineChartOutlined, RobotOutlined } from '@ant-design/icons';
import RiskChatPanel from './RiskChatPanel';
import ActWalkthrough from './ActWalkthrough';
import { RISK_COLORS as C } from './riskTheme';

const EYEBROW = '安平金控集团 · 风险管理部 · 风险预警系统';
const FOOTER_LINKS = [
  { to: '/risk/browse', icon: <DatabaseOutlined />, label: '数据工作台（数据浏览）' },
  { to: '/risk/overview', icon: <LineChartOutlined />, label: '价值总览' },
  { to: '/des', icon: <ClusterOutlined />, label: '企业模拟（DES）' },
  { to: '/browse', icon: <RobotOutlined />, label: '零售供应链演示（S1）' },
];

export default function RiskHomePage() {
  const navigate = useNavigate();

  return (
    <div data-testid="risk-home" style={{ minHeight: '100vh', background: C.ink, color: C.text }}>
      {/* ---------- Hero ---------- */}
      <section style={{ maxWidth: 1180, margin: '0 auto', padding: '52px 40px 28px' }}>
        <span
          style={{
            display: 'inline-flex', alignItems: 'center', gap: 8, fontSize: 12, letterSpacing: '0.14em',
            color: C.textDim, border: '1px solid ' + C.border, padding: '6px 12px', borderRadius: 6, background: C.surface,
          }}
        >
          {EYEBROW}
        </span>
        <h1 style={{ fontSize: 38, lineHeight: 1.15, fontWeight: 600, letterSpacing: '-0.01em', margin: '20px 0 12px', maxWidth: 620 }}>
          用一句话，做一周的归集
        </h1>
        <p style={{ fontSize: 15.5, color: C.textDim, margin: 0, maxWidth: 640, lineHeight: 1.75 }}>
          Agent 对话是唯一入口：自然语言问风险问题、执行真实处置，每条结论附证据链（哪张表、哪条规则、哪个分母）。
          下方七幕剧本演示一遍走完「现状对照 → 揭示 → 升级 → 双签 → 监管报送 → 全局督办」。
        </p>
      </section>

      {/* ---------- Agent 对话（唯一一级入口） ---------- */}
      <section className="risk-home-chat" style={{ maxWidth: 1180, margin: '0 auto', padding: '0 40px' }}>
        <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: 10, flexWrap: 'wrap', gap: 8 }}>
          <h2 style={{ fontSize: 20, margin: 0, fontWeight: 600, letterSpacing: '-0.01em' }}>
            <RobotOutlined style={{ color: C.accent, marginRight: 8 }} />
            风险对话 · 人机双签
          </h2>
          <span style={{ fontSize: 12.5, color: C.textFaint }}>对话即查、对话即办 · 每一步人确认 · 全程审计</span>
        </div>
        <div
          className="risk-home-chat-box"
          data-testid="home-chat"
          style={{
            border: '1px solid ' + C.border,
            borderRadius: 10,
            overflow: 'hidden',
            background: C.surface,
            height: 600,
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <RiskChatPanel />
        </div>
      </section>

      {/* ---------- 七幕剧本演示 ---------- */}
      <section className="risk-home-script" style={{ maxWidth: 1180, margin: '0 auto', padding: '44px 40px 8px' }}>
        <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: 4, flexWrap: 'wrap', gap: 8 }}>
          <h2 style={{ fontSize: 20, margin: 0, fontWeight: 600, letterSpacing: '-0.01em' }}>七幕剧本演示</h2>
          <span style={{ fontSize: 12.5, color: C.textFaint }}>数据真联动 · 证据链可点开 · 处置人确认 · 全程留痕</span>
        </div>
        <div style={{ fontSize: 13, color: C.textDim, lineHeight: 1.7, margin: '4px 0 18px', maxWidth: 760 }}>
          面向处长 5 分钟验收：逐幕推进，看「单看都安全、合起来踩线」如何被穿透识别，AI 提议如何被专业地拦住。
        </div>
        <ActWalkthrough />
      </section>

      {/* ---------- 页脚（次级入口 + 价值一句） ---------- */}
      <footer style={{ borderTop: '1px solid ' + C.border, marginTop: 40, background: C.surface }}>
        <div style={{ maxWidth: 1180, margin: '0 auto', padding: '20px 40px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
          <span style={{ color: C.textFaint, fontSize: 12.5 }}>
            语义接口层：LLM 经业务本体理解与操作，不直接碰库 · 数据浏览/图谱/DES 已撤出门面，随证据链展开态与页脚入口进入
          </span>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {FOOTER_LINKS.map((l) => (
              <button
                key={l.to}
                onClick={() => navigate(l.to)}
                style={{ background: 'transparent', border: '1px solid ' + C.border, color: C.textDim, borderRadius: 6, padding: '6px 12px', cursor: 'pointer', fontSize: 12.5, display: 'inline-flex', alignItems: 'center', gap: 6 }}
              >
                {l.icon}
                {l.label}
              </button>
            ))}
          </div>
        </div>
      </footer>
    </div>
  );
}
