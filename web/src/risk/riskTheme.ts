// S3 风险预警演示 —— 共享主题令牌（浅色专业金融风，方向 A）
// 单一品牌强调色：克制深蓝（colorPrimary 在 #2a4dc2~#2f54eb 区间取值，白字对比过 WCAG AA ≥4.5:1）。
// 红/橙/黄/绿仅作预警等级与状态语义色；灰阶统一冷灰一族（#e5e8ee 分隔线家族）。
// 形状系统：卡片/表格容器 8px、按钮/输入 6px（AntD token 定死）；数字 tabular-nums，不换字体。
import type { ThemeConfig } from 'antd';

// 品牌强调色：#2a50ce（白字对比约 6.6:1，AA 通过；介于 geekblue 与更深的金融蓝之间）
export const RISK_ACCENT = '#2a50ce';

export const RISK_COLORS = {
  // 底色层级：页面底 → 容器 → 面板（全站冷灰一族）
  ink: '#f5f6f8', // 页面底 #f5f6f8
  surface: '#ffffff', // 一级容器
  panel: '#ffffff', // 卡片/面板
  panelAlt: '#f0f3f9', // 嵌套底 / 悬停底
  border: '#e5e8ee',
  borderSoft: '#eef1f6',
  // 文本（冷灰深色系）
  text: '#101828',
  textDim: '#475467',
  // textFaint 由 #98a2b3(白底 2.58:1) 加深为 #636d80 —— 11px~13px 小字在 #fff 5.21:1 / #f0f3f9 4.69:1，
  // 满足 WCAG AA 4.5:1；仍是同族冷灰最浅一级，层级不变（axe jsdom 无法判定对比度，按实测值人工核验）。
  textFaint: '#636d80',
  // 品牌强调色（唯一装饰性颜色）
  accent: RISK_ACCENT,
  accentText: '#ffffff',
  // 预警等级语义色（按浅底可读性取深调，均可作 Tag 文字或白字底色，对比 ≥4.5:1）
  red: '#b42318',
  yellow: '#b54708', // 黄=关注（琥珀深调，浅底可读；纯黄在白底不可读）
  orange: '#c2410c', // 橙=紧急（独立于黄/红的暖橙，浅底可读，与 colorWarning 不混用）
  blue: '#175cd3',
  green: '#067647',
} as const;

/** 预警等级标签的浅底配色（同族淡彩底 + 深调字，替代深色主题的白字实底） */
export const WARN_TAG_TINTS = {
  RED: { bg: '#fceceb', border: '#efb3ae' },
  YELLOW: { bg: '#fdf3e3', border: '#ecc89a' },
  ORANGE: { bg: '#fdeae1', border: '#f2bda1' },
  BLUE: { bg: '#e7f0ff', border: '#aacbf5' },
} as const;

// 中文枚举预警等级（口径包§五/§八：黄/橙/红，存储即所见）——语义色对齐 RISK_COLORS，
// 与 AntD colorWarning（黄色）显式区分：橙=紧急用独立 ORANGE 色，绝不与 warning 混用。
export interface ZhWarnMeta {
  color: string;
  label: string;
  bg: string;
  border: string;
}
export const ZH_WARN_META: Record<'黄' | '橙' | '红', ZhWarnMeta> = {
  黄: { color: RISK_COLORS.yellow, label: '黄色预警 · 关注', ...WARN_TAG_TINTS.YELLOW },
  橙: { color: RISK_COLORS.orange, label: '橙色预警 · 紧急', ...WARN_TAG_TINTS.ORANGE },
  红: { color: RISK_COLORS.red, label: '红色预警 · 危急', ...WARN_TAG_TINTS.RED },
};

// 预警生命周期七态（口径包§四：待确认/确认中/已确认/处置中/已关闭/已撤销/已排除）
export const SIGNAL_STATUS_META_ZH: Record<string, { color: string; label: string }> = {
  待确认: { color: RISK_COLORS.textFaint, label: '待确认' },
  确认中: { color: RISK_COLORS.blue, label: '确认中' },
  已确认: { color: RISK_COLORS.yellow, label: '已确认' },
  处置中: { color: RISK_COLORS.red, label: '处置中' },
  已关闭: { color: RISK_COLORS.green, label: '已关闭' },
  已撤销: { color: RISK_COLORS.textDim, label: '已撤销' },
  已排除: { color: RISK_COLORS.textFaint, label: '已排除' },
};

// AntD 浅色算法定制（仅作用于风险演示分支与 DES 页，不影响 S1 零售界面）
export const riskLightTheme: ThemeConfig = {
  algorithm: undefined, // 默认 lightAlgorithm
  token: {
    colorPrimary: RISK_COLORS.accent,
    colorBgBase: RISK_COLORS.ink,
    colorBgContainer: RISK_COLORS.surface,
    colorBgElevated: RISK_COLORS.surface,
    colorBgLayout: RISK_COLORS.ink,
    colorBorder: RISK_COLORS.border,
    colorBorderSecondary: RISK_COLORS.borderSoft,
    colorText: RISK_COLORS.text,
    colorTextSecondary: RISK_COLORS.textDim,
    colorTextTertiary: RISK_COLORS.textFaint,
    colorError: RISK_COLORS.red,
    colorWarning: RISK_COLORS.yellow,
    colorSuccess: RISK_COLORS.green,
    colorInfo: RISK_COLORS.blue,
    borderRadius: 6, // 按钮/输入
    borderRadiusLG: 8, // 卡片/表格容器
    boxShadow: '0 1px 2px rgba(16, 24, 40, 0.06)',
    boxShadowSecondary: '0 2px 6px rgba(16, 24, 40, 0.08)',
    fontWeightStrong: 600,
    fontFamily:
      "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif",
  },
};

// 共享行内样式助手（避免每个页面重复写同一套浅色样式对象）
export const R = {
  page: {
    minHeight: '100vh',
    background: RISK_COLORS.ink,
    color: RISK_COLORS.text,
  },
  panel: {
    background: RISK_COLORS.panel,
    border: '1px solid ' + RISK_COLORS.border,
    borderRadius: 8,
  },
  panelHover: {
    background: RISK_COLORS.panelAlt,
    borderColor: RISK_COLORS.accent,
  },
  num: {
    fontVariantNumeric: 'tabular-nums' as const,
  },
} as const;

export const WARN_LEVEL_META: Record<string, { color: string; label: string; bg?: string; border?: string }> = {
  RED: { color: RISK_COLORS.red, label: '红色预警', ...WARN_TAG_TINTS.RED },
  YELLOW: { color: RISK_COLORS.yellow, label: '黄色预警', ...WARN_TAG_TINTS.YELLOW },
  BLUE: { color: RISK_COLORS.blue, label: '蓝色预警', ...WARN_TAG_TINTS.BLUE },
};

export const SIGNAL_STATUS_META: Record<string, { color: string; label: string }> = {
  GENERATED: { color: RISK_COLORS.textFaint, label: '待确认' },
  CONFIRMED: { color: RISK_COLORS.blue, label: '确认中' },
  GRADED: { color: RISK_COLORS.yellow, label: '已确认' },
  IN_DISPOSAL: { color: RISK_COLORS.red, label: '处置中' },
  CLOSED: { color: RISK_COLORS.textDim, label: '已关闭' },
  REJECTED_AS_FALSE: { color: RISK_COLORS.textFaint, label: '已撤销' },
};
