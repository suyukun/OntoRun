// S3 M4 风险预警演示 —— 共享主题令牌（金融风控"指挥中心"质感）
// 单一品牌强调色：信号琥珀；红/黄/蓝仅作预警等级语义色（functional，非装饰）。
// 形状系统：圆角统一 6px（偏锋利、命令台）；数据数字用等宽字体。
import type { ThemeConfig } from 'antd';

export const RISK_COLORS = {
  // 底色（深藏青 → 面板）
  ink: '#0A0F1C',
  surface: '#0F172A',
  panel: '#151F36',
  panelAlt: '#1B2743',
  border: '#26324F',
  borderSoft: 'rgba(148, 163, 184, 0.16)',
  // 文本
  text: '#E6EDF7',
  textDim: '#8FA3C0',
  textFaint: '#5C6F8F',
  // 品牌强调色（单一琥珀）
  accent: '#F2B04C',
  accentText: '#0A0F1C',
  // 预警等级语义色（functional）
  red: '#F0524D',
  yellow: '#F7C948',
  blue: '#4C8DFF',
  green: '#3DDC97',
  // 琥珀光环（hero 雷达等）
  glow: 'rgba(242, 176, 76, 0.35)',
} as const;

// AntD 暗色算法定制（仅作用于风险演示分支，不影响 S1 零售浅色界面）
export const riskDarkTheme: ThemeConfig = {
  algorithm: undefined, // 由页面用 darkAlgorithm 组合
  token: {
    colorPrimary: RISK_COLORS.accent,
    colorBgBase: RISK_COLORS.ink,
    colorBgContainer: RISK_COLORS.surface,
    colorBgElevated: RISK_COLORS.panel,
    colorBorder: RISK_COLORS.border,
    colorBorderSecondary: RISK_COLORS.borderSoft,
    colorText: RISK_COLORS.text,
    colorTextSecondary: RISK_COLORS.textDim,
    colorTextTertiary: RISK_COLORS.textFaint,
    colorError: RISK_COLORS.red,
    colorWarning: RISK_COLORS.yellow,
    colorSuccess: RISK_COLORS.green,
    colorInfo: RISK_COLORS.blue,
    borderRadius: 6,
    fontFamily:
      "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif",
  },
};

// 共享行内样式助手（避免每个页面重复写同一套深色样式对象）
export const R = {
  page: {
    minHeight: '100vh',
    background: RISK_COLORS.ink,
    color: RISK_COLORS.text,
  },
  panel: {
    background: RISK_COLORS.panel,
    border: '1px solid ' + RISK_COLORS.border,
    borderRadius: 6,
  },
  panelHover: {
    background: RISK_COLORS.panelAlt,
    borderColor: RISK_COLORS.accent,
  },
  mono: {
    fontFamily: "'SF Mono', 'JetBrains Mono', ui-monospace, Menlo, Consolas, monospace",
  },
} as const;

export const WARN_LEVEL_META: Record<string, { color: string; label: string }> = {
  RED: { color: RISK_COLORS.red, label: '红色预警' },
  YELLOW: { color: RISK_COLORS.yellow, label: '黄色预警' },
  BLUE: { color: RISK_COLORS.blue, label: '蓝色预警' },
};

export const SIGNAL_STATUS_META: Record<string, { color: string; label: string }> = {
  GENERATED: { color: RISK_COLORS.textFaint, label: '待确认' },
  CONFIRMED: { color: RISK_COLORS.blue, label: '确认中' },
  GRADED: { color: RISK_COLORS.yellow, label: '已确认' },
  IN_DISPOSAL: { color: RISK_COLORS.red, label: '处置中' },
  CLOSED: { color: RISK_COLORS.textDim, label: '已关闭' },
  REJECTED_AS_FALSE: { color: RISK_COLORS.textFaint, label: '已撤销' },
};
