// 空态 —— 问候 + 6 建议 chips（点击直接发送）+ 模拟数据声明（docs/chat-ux-spec-v1.md §3）
import type { ReactNode } from 'react';
import {
  AlertOutlined,
  BarChartOutlined,
  CalculatorOutlined,
  FileTextOutlined,
  QuestionCircleOutlined,
  SafetyOutlined,
  TableOutlined,
} from '@ant-design/icons';
import { SUGGESTION_CHIPS, type ChipIcon } from './scriptData';
import { RISK_COLORS } from '../risk/riskTheme';

const ICONS: Record<ChipIcon, ReactNode> = {
  alert: <AlertOutlined />,
  question: <QuestionCircleOutlined />,
  calc: <CalculatorOutlined />,
  chart: <BarChartOutlined />,
  report: <FileTextOutlined />,
  table: <TableOutlined />,
};

export default function EmptyState({ onAsk }: { onAsk: (q: string) => void }) {
  return (
    <div style={{ minHeight: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ paddingTop: '38vh', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div
          style={{
            width: 48,
            height: 48,
            borderRadius: 10,
            background: RISK_COLORS.accent,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <SafetyOutlined style={{ color: '#fff', fontSize: 24 }} />
        </div>
        <h1 style={{ margin: '20px 0 0', fontSize: 20, lineHeight: '30px', fontWeight: 600 }}>今天要看什么风险？</h1>
        <p style={{ margin: '8px 0 0', fontSize: 14, lineHeight: '22px', color: RISK_COLORS.textDim, maxWidth: 520, textAlign: 'center' }}>
          我可以按监管口径查预警、拆计算过程、起草处置提议——每个数字都带证据链。
        </p>
        <div
          className="chat-chip-grid"
          style={{ marginTop: 32, width: '100%', display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 12 }}
        >
          {SUGGESTION_CHIPS.map((c) => (
            <button key={c.key} className="chat-chip" onClick={() => onAsk(c.text)}>
              <span style={{ color: RISK_COLORS.textFaint, fontSize: 16, display: 'inline-flex', flexShrink: 0 }}>{ICONS[c.icon]}</span>
              <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{c.text}</span>
            </button>
          ))}
        </div>
      </div>
      <div style={{ flex: 1 }} />
      {/* 模拟数据声明：空态常驻（§3.1-5） */}
      <div style={{ paddingBottom: 24, textAlign: 'center', fontSize: 12, lineHeight: '20px', color: RISK_COLORS.textFaint }}>
        演示环境 · 数据为模拟金控剧本 · 安平集团口径 v0.3
      </div>
    </div>
  );
}