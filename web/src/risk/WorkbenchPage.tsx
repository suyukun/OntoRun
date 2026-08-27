// 数据工作台（/risk/browse）—— 分屏组合：左=数据浏览（DataExplorer），右=风险对话·人机双签。
// 组合层不持有主题（主题由 RiskShell 统一提供）；分屏/堆叠与独立滚动见 risk.css 的 .risk-workbench*。
import DataExplorer from '../components/DataExplorer';
import RiskChatPanel from './RiskChatPanel';

export default function WorkbenchPage() {
  return (
    <div className="risk-workbench" data-testid="risk-workbench">
      {/* 页面级 h1（视觉隐藏）：为屏幕阅读器提供页面定位；可见层级由左栏列表标题承担 */}
      <h1 className="risk-sr-only">数据工作台 · 风险预警</h1>
      <div className="risk-workbench-pane" data-testid="workbench-explorer">
        <DataExplorer />
      </div>
      <aside className="risk-workbench-chat" data-testid="workbench-chat" aria-label="风险对话">
        <RiskChatPanel />
      </aside>
    </div>
  );
}
