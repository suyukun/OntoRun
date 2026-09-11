import type { InsightItem } from '../types';

/** T-U2 主动洞察卡（UX v0.2 US2）：规则命中才渲染；无命中由页面的常用查询入口兜底（宁缺毋滥）。
 *  卡面=纯事实句（只报数字与对比，零归因——无事件日历，因果沉默=诚实铁律）。
 */

/** GET /api/insights（B3 契约）：任何失败（后端未起/非 200/结构缺失）→ 空数组 = 无命中兜底态，不打扰页开。 */
export async function loadInsights(): Promise<InsightItem[]> {
  try {
    const resp = await fetch('/api/insights');
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    const data = (await resp.json()) as { insights?: InsightItem[] };
    return Array.isArray(data.insights) ? data.insights : [];
  } catch {
    return [];
  }
}

/** 卡类型徽标文案（type 为后端机器值；未知类型回落原值显示）。 */
const TYPE_LABELS: Record<string, string> = {
  total_day_over_day: '总量突变',
  channel_day_over_day: '渠道突变',
  contribution_day_over_day: '贡献度突变',
};

function fmtDelta(pct: number): string {
  return (pct >= 0 ? '+' : '') + pct.toFixed(1) + '%';
}

/** 事实句：数字与对比全部来自结构化字段，不写任何原因词。 */
function factText(i: InsightItem): string {
  const day = i.drilldown.time.to.slice(5).replace('-', '/');
  const ch = i.channel ? `「${i.channel}」` : '';
  if (i.type === 'contribution_day_over_day') {
    return `${ch}${day} ${i.metric}占比 ${i.current}%，前一日 ${i.baseline}%（${fmtDelta(i.delta_pct)}）`;
  }
  return `${ch}${day} ${i.metric} ${i.current}，前一日 ${i.baseline}（${fmtDelta(i.delta_pct)}）`;
}

/** 「看分解」问题：由 drilldown 组装，走既有 /api/chat 关键词路由（分渠道/按日/注册），不新增契约。 */
export function drillQuestion(i: InsightItem): string {
  const month = Number(i.drilldown.time.to.slice(5, 7));
  const byChannel = i.drilldown.dimensions.includes('channel_l2');
  return `${month}月${byChannel ? '分渠道' : ''}按日${i.metric}`;
}

interface Props {
  insights: InsightItem[];
  onAsk: (q: string) => void;
}

export function InsightCard({ insights, onAsk }: Props) {
  if (insights.length === 0) return null;
  return (
    <div className="insights">
      {insights.map((i, idx) => (
        <div className="insight-card" key={`${i.type}-${i.channel ?? 'all'}-${idx}`}>
          <span className={'insight-type type-' + i.type}>{TYPE_LABELS[i.type] ?? i.type}</span>
          <span className="insight-fact">{factText(i)}</span>
          <button className="evbtn" onClick={() => onAsk(drillQuestion(i))}>
            看分解
          </button>
        </div>
      ))}
    </div>
  );
}
