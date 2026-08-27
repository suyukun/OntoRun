/// <reference types="vitest/globals" />
// risk.css <1280px 断点「样式规则存在性」轻断言。
// 项目只有 jsdom（无真实布局引擎），无法测视觉与布局；按任务约定只锁关键规则存在，
// 真实观感走人工验收清单（见回报）。raw 导入由 vite ?raw 提供。
import { describe, it, expect } from 'vitest';
import rawCss from './risk.css?raw';

describe('risk.css <1280px 断点样式规则存在性', () => {
  it('存在 <1280px 上下堆叠断点（max-width: 1279px）', () => {
    expect(rawCss).toContain('@media (max-width: 1279px)');
    expect(rawCss).toContain('.risk-workbench { flex-direction: column; height: auto; }');
  });

  it('窄屏右栏高度为视口自适应 max(420px, 60vh)（不再固定 560px）', () => {
    expect(rawCss).toContain('.risk-workbench-chat { flex: 0 0 auto; width: 100%; height: max(420px, 60vh); border-left: 0; border-top: 1px solid #e5e8ee; }');
  });

  it('桌面分屏右栏仍固定 420px，窄屏分支不影响桌面', () => {
    expect(rawCss).toContain('.risk-workbench-chat {');
    expect(rawCss).toContain('flex: 0 0 420px;');
  });

  it('左栏窗格带 min-width: 0 防溢出护栏（窄屏分组不横向撑破）', () => {
    expect(rawCss).toContain('.risk-workbench-pane {');
    expect(rawCss).toContain('min-width: 0;');
  });
});
