import { useState } from 'react';
import { DataTable } from './DataTable';

/**
 * D7 viz 契约渲染器：bar=分类柱状（纯 SVG 手写，零 npm 依赖）/ kpi=大数字指标卡。
 * 数据源 = 同一 rows（与表格同源，禁止另算）；数据不满足图表形态时回退 DataTable。
 * 配色沿用 index.css 设计 token（--acc/--ink/--sub/--line），不另起样式体系。
 */

type ChartViz = 'bar' | 'kpi';

interface Props {
  viz: ChartViz;
  rows: Record<string, unknown>[];
}

/** 列推导约定（与 DataTable 同一首行键）：label=首个非数值列，value=首个数值列；kpi 仅需数值列。 */
function pickColumns(rows: Record<string, unknown>[]): { labelCol: string; valueCol: string } | null {
  const first = rows[0];
  if (!first) return null;
  const cols = Object.keys(first);
  const labelCol = cols.find((c) => typeof first[c] !== 'number');
  const valueCol = cols.find((c) => typeof first[c] === 'number');
  return labelCol !== undefined && valueCol !== undefined ? { labelCol, valueCol } : null;
}

function firstNumericCol(first: Record<string, unknown>): string | undefined {
  return Object.keys(first).find((c) => typeof first[c] === 'number');
}

const fmt = (n: number): string => n.toLocaleString('en-US');
const trunc = (s: string): string => (s.length > 6 ? s.slice(0, 5) + '…' : s);

/* bar：viewBox 逻辑坐标等比缩放，柱上数值常显 + <title> hover 提示，hover 时其余柱降透明 */
const BAR_W = 560;
const BAR_H = 190;
const PAD = { l: 12, r: 12, t: 26, b: 30 };

function BarChart({ rows }: { rows: Record<string, unknown>[] }) {
  const [hover, setHover] = useState(-1);
  const cols = pickColumns(rows);
  if (!cols) return <DataTable rows={rows} />;
  const items = rows.map((r) => ({ label: String(r[cols.labelCol]), value: Number(r[cols.valueCol]) }));
  const max = Math.max(...items.map((d) => d.value));
  const plotH = BAR_H - PAD.t - PAD.b;
  const slot = (BAR_W - PAD.l - PAD.r) / items.length;
  const bw = Math.min(slot * 0.55, 64);
  const scale = max > 0 ? plotH / max : 0;
  return (
    <svg
      viewBox={'0 0 ' + BAR_W + ' ' + BAR_H}
      role="img"
      aria-label={'柱状图：' + cols.valueCol + ' 按 ' + cols.labelCol}
      style={{ width: '100%', height: 'auto', display: 'block' }}
    >
      <line x1={PAD.l} y1={BAR_H - PAD.b} x2={BAR_W - PAD.r} y2={BAR_H - PAD.b} stroke="var(--line)" />
      {items.map((d, i) => {
        const h = Math.max(d.value * scale, 2);
        const x = PAD.l + slot * i + (slot - bw) / 2;
        const y = BAR_H - PAD.b - h;
        const cx = PAD.l + slot * i + slot / 2;
        return (
          <g key={d.label + i} onMouseEnter={() => setHover(i)} onMouseLeave={() => setHover(-1)}>
            <title>{d.label + '：' + fmt(d.value)}</title>
            <rect x={x} y={y} width={bw} height={h} rx={3} fill="var(--acc)" opacity={hover === -1 ? 0.8 : hover === i ? 1 : 0.45} />
            <text x={cx} y={y - 5} textAnchor="middle" fontSize={11} fill="var(--sub)">{fmt(d.value)}</text>
            <text x={cx} y={BAR_H - PAD.b + 15} textAnchor="middle" fontSize={11} fill="var(--sub)">{trunc(d.label)}</text>
          </g>
        );
      })}
    </svg>
  );
}

/* kpi：首行首个数值列 = 大数字，指标名列名做注脚（不做任何另算/换算） */
function KpiCard({ rows }: { rows: Record<string, unknown>[] }) {
  const valueCol = rows[0] ? firstNumericCol(rows[0]) : undefined;
  const value = valueCol !== undefined ? Number(rows[0][valueCol]) : NaN;
  if (valueCol === undefined || !Number.isFinite(value)) return <DataTable rows={rows} />;
  return (
    <div style={{
      display: 'inline-flex', flexDirection: 'column', gap: 2, padding: '10px 18px',
      background: '#fbfcfe', border: '1px solid var(--line)', borderRadius: 8,
    }}>
      <span style={{
        fontSize: 30, fontWeight: 700, lineHeight: 1.2, color: 'var(--ink)',
        fontFamily: 'Menlo, monospace', fontVariantNumeric: 'tabular-nums',
      }}>{fmt(value)}</span>
      <span style={{ fontSize: 11, color: 'var(--sub)' }}>{valueCol}</span>
    </div>
  );
}

/** 数据区图表入口：MessageCard 按 final.result.viz 分支调用；非 bar/kpi 由调用方回落 DataTable。 */
export function Chart({ viz, rows }: Props) {
  return viz === 'bar' ? <BarChart rows={rows} /> : <KpiCard rows={rows} />;
}