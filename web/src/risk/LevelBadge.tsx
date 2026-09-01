// 中文枚举预警等级徽标（口径包§五：黄/橙/红）—— 语义色对齐 riskTheme.RISK_COLORS，
// 浅色金融风：同族淡彩底 + 深调字（替代深色主题的白字实底），对比 ≥4.5:1。
// 注意：橙=紧急用独立 ORANGE 色，不与 AntD colorWarning（黄色）混用。
import { zhWarnMeta } from './warnLevel';
import type { ZhWarnLevel } from './warnLevel';
import type { ZhWarnMeta } from './riskTheme';

export type { ZhWarnLevel } from './warnLevel';

/** 「橙色预警 · 紧急」 → 描述「紧急」（徽标内小字部分） */
function descriptor(meta: ZhWarnMeta): string {
  return meta.label.split(' · ')[1] ?? '';
}

// 徽标（缺口圆点 + 级别字 + 描述），用于帧内展示预警级别
export default function LevelBadge({
  level,
  size = 'md',
  showDesc = true,
}: {
  level: ZhWarnLevel;
  size?: 'sm' | 'md' | 'lg';
  showDesc?: boolean;
}) {
  const meta = zhWarnMeta(level);
  const pad = size === 'lg' ? '8px 14px' : size === 'sm' ? '3px 9px' : '5px 11px';
  const fontSize = size === 'lg' ? 15 : size === 'sm' ? 12 : 13;
  return (
    <span
      data-testid={'level-badge-' + level}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 6,
        background: meta.bg,
        border: '1px solid ' + meta.border,
        color: meta.color,
        borderRadius: 999,
        padding: pad,
        fontSize,
        fontWeight: 600,
        lineHeight: 1,
        letterSpacing: '0.01em',
        whiteSpace: 'nowrap',
      }}
    >
      <span
        aria-hidden
        style={{
          width: size === 'lg' ? 10 : size === 'sm' ? 7 : 8,
          height: size === 'lg' ? 10 : size === 'sm' ? 7 : 8,
          borderRadius: '50%',
          background: meta.color,
          flex: '0 0 auto',
        }}
      />
      <span>{level}</span>
      {showDesc && descriptor(meta) && (
        <span style={{ fontWeight: 400, opacity: 0.92 }}>{descriptor(meta)}</span>
      )}
    </span>
  );
}

// 简单的「黄/橙/红」小圆点指示（行内紧凑场景：排名表、状态行）
export function LevelDot({ level }: { level: ZhWarnLevel }) {
  return (
    <span
      data-testid={'level-dot-' + level}
      aria-label={'预警级别：' + level}
      style={{
        display: 'inline-block',
        width: 9,
        height: 9,
        borderRadius: '50%',
        background: zhWarnMeta(level).color,
        marginRight: 6,
      }}
    />
  );
}
