// chart 块 —— 各机构占比 vs 预警线（docs/chat-ux-spec-v1.md §5.3）
// 颜色语义映射自 riskTheme（§0.4：废弃原型临时色 React默认蓝/AntD默认橙/原型绿）；数据与 TABLE_ROWS 同源，不手写数字。
import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { Modal } from 'antd';
import { DownloadOutlined, FileSearchOutlined, ZoomInOutlined } from '@ant-design/icons';
import type { EChartsOption } from 'echarts';
import * as echarts from 'echarts';
import { TABLE_ROWS } from '../../proto/fakeData';
import { RISK_COLORS, WARN_TAG_TINTS } from '../../risk/riskTheme';
import type { ChartSeriesItem } from '../chatApi';

/** 数据色语义映射（§5.3）：达标 #067647 / 触达 #b54708 / 预警 #c2410c / 危急 #b42318 */
const LEVEL_COLOR: Record<string, string> = {
  安全: RISK_COLORS.green,
  触达: RISK_COLORS.yellow,
  橙色预警: RISK_COLORS.orange,
  危急: RISK_COLORS.red,
};

/**
 * live 柱色（批 3）：集团归集柱对照 R1a 三线（9 黄/10 橙/12 红，来自 rules_hits.computed 真实值）；
 * 机构柱用中性色——载荷未带各机构参考线（org_reference_ratio 是本机构当前占比，非参考线），
 * 不在前端臆测色语义，达线明细由正文与证据抽屉承载。
 */
function liveColor(item: ChartSeriesItem): string {
  if (item.isGroup) {
    if (item.ratio > 12) return LEVEL_COLOR['危急'];
    if (item.ratio >= 10) return LEVEL_COLOR['橙色预警'];
    if (item.ratio >= 9) return LEVEL_COLOR['触达'];
    return LEVEL_COLOR['安全'];
  }
  return RISK_COLORS.textFaint;
}

function buildOption(series?: ChartSeriesItem[]): EChartsOption {
  if (series?.length) {
    return {
      animationDuration: 300,
      animationEasing: 'cubicOut',
      legend: { show: false },
      tooltip: {
        trigger: 'axis',
        transitionDuration: 0,
        backgroundColor: '#ffffff',
        borderWidth: 1,
        borderColor: RISK_COLORS.borderSoft,
        borderRadius: 6,
        extraCssText: 'box-shadow: 0 1px 2px rgba(16, 24, 40, 0.06);',
        textStyle: { color: RISK_COLORS.text, fontSize: 12 },
        valueFormatter: (v) => `${v}%`,
      },
      grid: { left: 40, right: 16, top: 30, bottom: 28 },
      xAxis: {
        type: 'category',
        data: series.map((s) => s.org),
        // 类目多时自动抽稀防重叠（假数据 4 类目 interval 0 不受影响；live 行数不定）
        axisLabel: { interval: 'auto', hideOverlap: true, fontSize: 11, color: RISK_COLORS.textFaint },
        axisLine: { lineStyle: { color: RISK_COLORS.borderSoft } },
        axisTick: { show: false },
      },
      yAxis: {
        type: 'value',
        axisLabel: { formatter: '{value}%', fontSize: 11, color: RISK_COLORS.textFaint },
        splitLine: { lineStyle: { color: RISK_COLORS.borderSoft, type: 'solid' } },
      },
      series: [
        {
          type: 'bar',
          name: '占比',
          barWidth: 28,
          data: series.map((s) => ({ value: s.ratio, itemStyle: { color: liveColor(s) } })),
          markLine: {
            silent: true,
            symbol: 'none',
            lineStyle: { color: RISK_COLORS.orange, type: 'dashed', width: 1.5 },
            label: {
              formatter: '预警线 10%',
              fontSize: 11,
              color: RISK_COLORS.orange,
              backgroundColor: WARN_TAG_TINTS.ORANGE.bg,
              padding: [2, 6],
              borderRadius: 4,
            },
            data: [{ yAxis: 10 }],
          },
        },
      ],
    };
  }
  return {
    animationDuration: 300, // 入场 300ms 仅一次（§5.3）
    animationEasing: 'cubicOut',
    legend: { show: false }, // 类目即 x 轴，图例默认关
    tooltip: {
      trigger: 'axis',
      transitionDuration: 0, // 无动画
      backgroundColor: '#ffffff',
      borderWidth: 1,
      borderColor: RISK_COLORS.borderSoft,
      borderRadius: 6,
      extraCssText: 'box-shadow: 0 1px 2px rgba(16, 24, 40, 0.06);',
      textStyle: { color: RISK_COLORS.text, fontSize: 12 },
    },
    grid: { left: 40, right: 16, top: 30, bottom: 28 },
    xAxis: {
      type: 'category',
      data: TABLE_ROWS.map((r) => r.org.replace('（R1a）', '')),
      axisLabel: { interval: 0, hideOverlap: false, fontSize: 11, color: RISK_COLORS.textFaint },
      axisLine: { lineStyle: { color: RISK_COLORS.borderSoft } },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      axisLabel: { formatter: '{value}%', fontSize: 11, color: RISK_COLORS.textFaint },
      splitLine: { lineStyle: { color: RISK_COLORS.borderSoft, type: 'solid' } }, // 禁虚线网格（§5.3）
    },
    series: [
      {
        type: 'bar',
        name: '占比',
        barWidth: 28,
        data: TABLE_ROWS.map((r) => ({
          value: Number.parseFloat(r.ratio),
          itemStyle: { color: LEVEL_COLOR[r.level] ?? RISK_COLORS.textFaint },
        })),
        markLine: {
          silent: true,
          symbol: 'none',
          lineStyle: { color: RISK_COLORS.orange, type: 'dashed', width: 1.5 },
          label: {
            formatter: '预警线 10%',
            fontSize: 11,
            color: RISK_COLORS.orange,
            backgroundColor: WARN_TAG_TINTS.ORANGE.bg,
            padding: [2, 6],
            borderRadius: 4,
          },
          data: [{ yAxis: 10 }],
        },
      },
    ],
  };
}

function ChartCanvas({ option, height, onReady }: { option: EChartsOption; height: number; onReady?: (c: echarts.ECharts) => void }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!ref.current) return;
    const chart = echarts.init(ref.current);
    chart.setOption(option);
    onReady?.(chart);
    const onResize = () => chart.resize();
    window.addEventListener('resize', onResize);
    return () => {
      window.removeEventListener('resize', onResize);
      chart.dispose();
    };
    // onReady 由父组件 useCallback 提供稳定引用；option 为 useMemo 常量，均不随渲染变化
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [option]);
  return <div ref={ref} style={{ width: '100%', height }} />;
}

function IconBtn({ title, onClick, children }: { title: string; onClick: () => void; children: ReactNode }) {
  return (
    <button className="chat-icon-btn" title={title} onClick={onClick} style={{ marginLeft: 4 }}>
      {children}
    </button>
  );
}

export default function BlockChart({ onEvidence, series }: { onEvidence: () => void; series?: ChartSeriesItem[] }) {
  const [zoom, setZoom] = useState(false);
  const option = useMemo(() => buildOption(series), [series]);
  const chartRef = useRef<echarts.ECharts | null>(null);
  const handleReady = useCallback((c: echarts.ECharts) => {
    chartRef.current = c;
  }, []);

  const downloadPng = () => {
    const url = chartRef.current?.getDataURL({ type: 'png', pixelRatio: 2 });
    if (!url) return;
    const a = document.createElement('a');
    a.href = url;
    a.download = '各机构占比与预警线.png';
    a.click();
  };

  return (
    <div style={{ background: '#fff', border: `1px solid ${RISK_COLORS.borderSoft}`, borderRadius: 8, padding: 12 }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', marginBottom: 8 }}>
        <div>
          <div style={{ fontSize: 13, lineHeight: '20px', fontWeight: 600 }}>各机构占比 vs 预警线</div>
          <div style={{ marginTop: 2, fontSize: 12, lineHeight: '20px', color: RISK_COLORS.textFaint }}>
            口径：归集集中度 = 归集敞口 ÷ 并表资本
          </div>
        </div>
        <span style={{ flex: 1 }} />
        <IconBtn title="放大" onClick={() => setZoom(true)}>
          <ZoomInOutlined />
        </IconBtn>
        <IconBtn title="下载 PNG" onClick={downloadPng}>
          <DownloadOutlined />
        </IconBtn>
        <IconBtn title="查看依据" onClick={onEvidence}>
          <FileSearchOutlined />
        </IconBtn>
      </div>
      <ChartCanvas option={option} height={260} onReady={handleReady} />
      <Modal
        open={zoom}
        width={720}
        title="各机构占比 vs 预警线"
        onCancel={() => setZoom(false)}
        footer={null}
        styles={{ body: { paddingTop: 12 } }}
      >
        {zoom && <ChartCanvas option={option} height={430} />}
      </Modal>
    </div>
  );
}