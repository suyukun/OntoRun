// T503 首页版式收口（§A2-US3 / §A3 qc1_first_screen_blocks）：
// 首页 = 待办横条（有待确认才出现，0 条不渲染）+ 域图画布 + 图例/健康度行
// （T403 DomainGraph 自带，画布底部一行），首屏 1080p 信息区块 ≤3。
// 旧表级 React Flow 图退役（表级视图由域内图 DomainDrilldown 承担）。
// 三层下钻接线（drilldown_breadcrumb 逐级可达）：
//   域图 #/graph → 点域节点 → 域内图 #/graph/{domainKey} → 点表 → 表详情 #/object/table/{id}。
// 实现注记：DomainGraph 本体（T403）未透出域节点点击回调（点击只开内部 Drawer），
// 按任务文件边界不动组件本体，这里用包装层事件委托拦截 data-testid="domain-node-{key}"
// 的点击转 hash 路由（capture 阶段 stopPropagation，内部 Drawer 不再触发）。
import type { MouseEvent } from "react";
import { Alert, Button, Space } from "antd";
import DomainGraph from "../components/DomainGraph";
import DomainDrilldown from "../components/DomainDrilldown";
import type { Ontology } from "../api";

function goHash(hash: string) {
  window.location.hash = hash;
}

// 待办横条：「钉死口径」口号仅限此处（qc11_terminology_consistency）。
function HomeTodoBar({ pending, confirmed }: { pending: number; confirmed: number }) {
  return (
    <Alert
      banner
      data-testid="home-todo-bar"
      type="warning"
      showIcon
      title={
        <Space size={12}>
          <span>
            <b>{pending}</b> 条口径待确认（已确认 {confirmed}）—— 口径没钉死，数不准
          </span>
          <Button size="small" type="primary" onClick={() => goHash("#/rules")}>
            去确认 →
          </Button>
        </Space>
      }
    />
  );
}

// 域图包装层：域节点点击 → 域内图路由（理由见文件头注记）。
function DomainGraphPanel() {
  const onClickCapture = (e: MouseEvent<HTMLDivElement>) => {
    const el = e.target as Element | null;
    const card = el?.closest?.('[data-testid^="domain-node-"]');
    if (!card) return;
    const key = card.getAttribute("data-testid")?.slice("domain-node-".length);
    if (!key) return;
    e.stopPropagation(); // 内部 Drawer 开合逻辑不触发，直接走下钻路由
    e.preventDefault();
    goHash(`#/graph/${encodeURIComponent(key)}`);
  };
  return (
    <div data-testid="home-graph-panel" onClickCapture={onClickCapture}>
      <DomainGraph />
    </div>
  );
}

export default function GraphHome({
  ontology,
  domain,
}: {
  ontology: Ontology | null;
  /** 域下钻路由参（#/graph/{domainKey}），非空 = 域内图视图 */
  domain?: string;
}) {
  if (domain) {
    return (
      <DomainDrilldown
        domainKey={domain}
        onBackToGraph={() => goHash("#/graph")}
        onOpenDomain={(key) => goHash(`#/graph/${encodeURIComponent(key)}`)}
      />
    );
  }
  const pending = ontology?.summary.pending ?? 0;
  const confirmed = ontology?.summary.confirmed ?? 0;
  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      {pending > 0 && <HomeTodoBar pending={pending} confirmed={confirmed} />}
      <div style={{ flex: 1, minHeight: 0, overflow: "auto" }}>
        <DomainGraphPanel />
      </div>
    </div>
  );
}
