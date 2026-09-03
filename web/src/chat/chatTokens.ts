// chat 专属视觉 token（docs/chat-ux-spec-v1.md §9.6：仅 4 项，必须由 RISK_COLORS / WARN_TAG_TINTS 派生或注明来源）
import { RISK_ACCENT, WARN_TAG_TINTS } from '../risk/riskTheme';

// 1) 等宽字体栈（§9.2）：表名/参数名/表达式/审计号/时间戳（spec 定值，非色板派生）
export const chatFontMono = "'SF Mono', 'JetBrains Mono', Menlo, Consolas, monospace";

// 2) 用户气泡底（§4.2）= WARN_TAG_TINTS.BLUE.bg（与 accent 同族的唯一浅底）
export const chatUserBubbleBg = WARN_TAG_TINTS.BLUE.bg;

// 3) 输入区 focus 外圈（§7.1）= rgba(42, 80, 206, 0.08)，由 RISK_ACCENT 派生
export function accentAlpha(alpha: number): string {
  const hex = RISK_ACCENT.replace('#', '');
  const rgb = [0, 2, 4].map((i) => parseInt(hex.slice(i, i + 2), 16)).join(', ');
  return `rgba(${rgb}, ${alpha})`;
}
export const chatFocusRing = accentAlpha(0.08);

// 4) 预警命中行底（§5.2）= #fdf1ea（ORANGE tint 60% 不透明等效，spec 定值）
export const chatHitRowBg = '#fdf1ea';
