import type { ReactNode } from 'react';

/**
 * 零依赖内联 SVG 图标（24 viewBox / 1.5 stroke / currentColor / aria-hidden）。
 * 替代 emoji 字符作 UI 图标（UX 审查报告 §三：去 emoji 化方案）；命名对齐 lucide。
 * 文字优先原则：主操作仍以文字为主，图标仅作辅助装饰。
 */
export type IconName =
  | 'star'
  | 'pin'
  | 'pencil'
  | 'trash'
  | 'plus'
  | 'loader'
  | 'copy'
  | 'check'
  | 'x'
  | 'inbox'
  | 'square'
  | 'chevron-up'
  | 'chevron-down'
  | 'chevron-left'
  | 'archive'
  | 'rotate'
  | 'more';

const GLYPHS: Record<IconName, ReactNode> = {
  star: <path d="M12 3.2l2.6 5.4 5.9.9-4.3 4.1 1 5.9-5.2-2.8-5.2 2.8 1-5.9L3.5 9.5l5.9-.9z" />,
  pin: (
    <>
      <path d="M12 17v5" />
      <path d="M5 17h14v-1.8a2 2 0 0 0-1.1-1.8l-1.8-.9a2 2 0 0 1-1.1-1.8V6h1a2 2 0 0 0 0-4H8a2 2 0 0 0 0 4h1v5.5a2 2 0 0 1-1.1 1.8l-1.8.9A2 2 0 0 0 5 15.2Z" />
    </>
  ),
  pencil: (
    <>
      <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
      <path d="m15 5 4 4" />
    </>
  ),
  trash: (
    <>
      <path d="M3 6h18" />
      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6" />
      <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
    </>
  ),
  plus: (
    <>
      <path d="M5 12h14" />
      <path d="M12 5v14" />
    </>
  ),
  loader: <path d="M21 12a9 9 0 1 1-6.219-8.56" />,
  copy: (
    <>
      <rect width="13" height="13" x="9" y="9" rx="2" />
      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
    </>
  ),
  check: <path d="M20 6 9 17l-5-5" />,
  x: (
    <>
      <path d="M18 6 6 18" />
      <path d="m6 6 12 12" />
    </>
  ),
  inbox: (
    <>
      <polyline points="22 12 16 12 14 15 10 15 8 12 2 12" />
      <path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z" />
    </>
  ),
  square: <rect width="14" height="14" x="5" y="5" rx="2" />,
  'chevron-up': <path d="m18 15-6-6-6 6" />,
  'chevron-down': <path d="m6 9 6 6 6-6" />,
  'chevron-left': <path d="m15 18-6-6 6-6" />,
  archive: (
    <>
      <rect width="20" height="5" x="2" y="3" rx="1" />
      <path d="M4 8v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8" />
      <path d="M10 12h4" />
    </>
  ),
  rotate: (
    <>
      <path d="M21 12a9 9 0 1 1-2.64-6.36" />
      <path d="M21 3v6h-6" />
    </>
  ),
  more: (
    <>
      <circle cx="12" cy="12" r="1.4" fill="currentColor" stroke="none" />
      <circle cx="19" cy="12" r="1.4" fill="currentColor" stroke="none" />
      <circle cx="5" cy="12" r="1.4" fill="currentColor" stroke="none" />
    </>
  ),
};

interface IconProps {
  name: IconName;
  /** 渲染尺寸（px），默认 14 */
  size?: number;
  /** 实心填充（如已收藏 star、停止 square） */
  filled?: boolean;
  className?: string;
}

export function Icon({ name, size = 14, filled = false, className }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill={filled ? 'currentColor' : 'none'}
      stroke="currentColor"
      strokeWidth={1.5}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
      className={className}
      style={{ flex: 'none' }}
    >
      {GLYPHS[name]}
    </svg>
  );
}
