import { afterEach, describe, expect, it } from 'vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { Chart } from '../components/Chart';
import { MessageCard } from '../components/MessageCard';
import type { ChatMessage, FinalResult } from '../types';

/** T6 viz 契约渲染：bar/kpi 纯 SVG 渲染器 + MessageCard 数据区分支（D7：图表与表格同源同一 rows）。 */

afterEach(() => cleanup());

const BAR_ROWS = [
  { channel: 'APP', cnt: 1240 },
  { channel: '小程序', cnt: 987 },
  { channel: '官网', cnt: 456 },
];

function successMsg(over: Partial<FinalResult>): ChatMessage {
  return {
    id: 1, role: 'ai', text: 'q', steps: [], streamedText: '',
    phase: 'done', endedBy: 'final', error: null,
    result: {
      request_id: 'R', started_at: '', question: 'q', rule: 'REG_X', path: 'hot',
      answer: 'a', sql: null, rows: [], tables: [], steps: [],
      ...over,
    },
  };
}

const noop = () => undefined;

describe('Chart 渲染器（D7 viz 契约，数据源 = 同一 rows）', () => {
  it('bar：每行一柱，标签+数值可见（与 rows 同源），hover 突出当前柱 + title 提示', () => {
    const { container } = render(<Chart viz="bar" rows={BAR_ROWS} />);
    expect(container.querySelector('svg')).toBeTruthy();
    expect(container.querySelectorAll('rect')).toHaveLength(BAR_ROWS.length);
    expect(screen.getByText('APP')).toBeTruthy(); // 分类标签
    expect(screen.getByText('1,240')).toBeTruthy(); // 柱上数值（rows.cnt 千分位）
    const rects = container.querySelectorAll('rect');
    const g = rects[0].closest('g');
    expect(g).toBeTruthy();
    fireEvent.mouseEnter(g as Element);
    expect(rects[0].getAttribute('opacity')).toBe('1'); // 当前柱突出
    expect(rects[1].getAttribute('opacity')).toBe('0.45'); // 其余柱降透明
    expect(container.querySelector('title')?.textContent).toContain('APP：1,240');
  });

  it('kpi：首行数值 = 大数字指标卡，指标名列名做注脚，不另算', () => {
    const { container } = render(<Chart viz="kpi" rows={[{ total: 2893 }]} />);
    expect(screen.getByText('2,893')).toBeTruthy();
    expect(screen.getByText('total')).toBeTruthy();
    expect(container.querySelector('svg')).toBeNull();
  });

  it('回退：rows 空 / 无数值列 → 回退 DataTable，不渲染空图表', () => {
    const empty = render(<Chart viz="bar" rows={[]} />);
    expect(empty.container.querySelector('table')).toBeTruthy();
    expect(empty.container.querySelector('svg[role="img"]')).toBeNull(); // 空数据：无图表 svg
    const noNum = render(<Chart viz="kpi" rows={[{ channel: 'APP' }]} />);
    expect(noNum.container.querySelector('table')).toBeTruthy();
  });
});

describe('MessageCard 数据区分支（final.result.viz → 渲染器）', () => {
  it('viz=bar → SVG 柱状；viz=kpi → 指标卡；viz 缺省 → DataTable', () => {
    const bar = render(
      <MessageCard msg={successMsg({ viz: 'bar', rows: BAR_ROWS })} pathLabels={{}} onRetry={noop} onFollowUp={noop} />,
    );
    expect(bar.container.querySelector('svg')).toBeTruthy();
    expect(bar.container.querySelector('table')).toBeNull();

    const kpi = render(
      <MessageCard msg={successMsg({ viz: 'kpi', rows: [{ total: 2893 }] })} pathLabels={{}} onRetry={noop} onFollowUp={noop} />,
    );
    expect(kpi.container.textContent).toContain('2,893');
    expect(kpi.container.querySelector('table')).toBeNull();

    const tbl = render(
      <MessageCard msg={successMsg({ rows: BAR_ROWS })} pathLabels={{}} onRetry={noop} onFollowUp={noop} />,
    );
    expect(tbl.container.querySelector('table')).toBeTruthy();
  });

  it('viz=pie（P0 未支持）→ 回退 DataTable；空数据 → 数据区空态，不渲染图表', () => {
    const pie = render(
      <MessageCard msg={successMsg({ viz: 'pie', rows: BAR_ROWS })} pathLabels={{}} onRetry={noop} onFollowUp={noop} />,
    );
    expect(pie.container.querySelector('table')).toBeTruthy();
    expect(pie.container.querySelector('svg[role="img"]')).toBeNull(); // 回退 DataTable：无图表 svg

    const empty = render(
      <MessageCard msg={successMsg({ viz: 'bar', rows: [] })} pathLabels={{}} onRetry={noop} onFollowUp={noop} />,
    );
    expect(empty.container.querySelector('svg[role="img"]')).toBeNull(); // 空数据：无图表 svg
    expect(empty.container.textContent).toContain('空结果集');
  });
});