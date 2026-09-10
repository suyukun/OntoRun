// 壳：顶栏导航（图谱首页 / 对象列表 / 口径确认 / 变更历史）+ hash 路由 + 全局数据装载。
// 对象详情页不入导航：从列表行 / 图谱节点进入（#/object/{kind}/{id}）。
import { useCallback, useEffect, useState } from "react";
import { Badge, Layout, Menu, Typography } from "antd";
import { api, type Lineage, type ObjectKind, type Ontology } from "./api";
import GraphHome from "./pages/GraphHome";
import HistoryPage from "./pages/HistoryPage";
import ObjectDetailPage from "./pages/ObjectDetailPage";
import ObjectsPage from "./pages/ObjectsPage";
import RulesPage from "./pages/RulesPage";

const { Header, Content } = Layout;
const { Text } = Typography;

type Page = "graph" | "objects" | "rules" | "history";
type Route = { page: Page } | { page: "object"; kind: ObjectKind; id: string };

function isObjectKind(v: string): v is ObjectKind {
  return v === "measure" || v === "dimension" || v === "table";
}

function routeFromHash(): Route {
  const raw = window.location.hash.replace(/^#\/?/, "");
  const parts = raw.split("/").filter(Boolean).map(decodeURIComponent);
  if (parts[0] === "object" && parts[1] !== undefined && isObjectKind(parts[1]) && parts[2] !== undefined) {
    return { page: "object", kind: parts[1], id: parts[2] };
  }
  if (parts[0] === "history") return { page: "history" };
  if (parts[0] === "objects") return { page: "objects" };
  if (parts[0] === "rules") return { page: "rules" };
  return { page: "graph" };
}

export function go(page: Page) {
  window.location.hash = `#/${page}`;
}

export default function App() {
  const [route, setRoute] = useState<Route>(routeFromHash);
  const [ontology, setOntology] = useState<Ontology | null>(null);
  const [lineage, setLineage] = useState<Lineage | null>(null);

  const reload = useCallback(() => {
    api.ontology().then(setOntology).catch((e) => console.error(e));
    api.lineage().then(setLineage).catch((e) => console.error(e));
  }, []);
  useEffect(reload, [reload]);

  useEffect(() => {
    const onHash = () => setRoute(routeFromHash());
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);

  const pending = ontology?.summary.pending ?? 0;
  const selectedKey = route.page === "object" ? "objects" : route.page;

  return (
    <Layout style={{ height: "100vh" }}>
      <Header
        style={{
          display: "flex",
          alignItems: "center",
          gap: 24,
          background: "#fff",
          borderBottom: "1px solid #f0f0f0",
          padding: "0 24px",
        }}
      >
        <Text strong style={{ fontSize: 16, whiteSpace: "nowrap" }}>
          OntoRun 本体管理台
        </Text>
        <Menu
          mode="horizontal"
          selectedKeys={[selectedKey]}
          style={{ flex: 1, minWidth: 320, borderBottom: "none" }}
          items={[
            { key: "graph", label: "图谱首页" },
            { key: "objects", label: "对象列表" },
            {
              key: "rules",
              label: (
                <span>
                  口径确认{" "}
                  <Badge count={pending} size="small" offset={[4, -2]} />
                </span>
              ),
            },
            { key: "history", label: "变更历史" },
          ]}
          onClick={(e) => go(e.key as Page)}
        />
        <Text type="secondary" style={{ fontSize: 12, whiteSpace: "nowrap" }}>
          财富广场语义层 · 数据源：registry + lineage（真实数据）
        </Text>
      </Header>
      <Content style={{ overflow: "hidden" }}>
        {route.page === "graph" && (
          <GraphHome
            lineage={lineage}
            ontology={ontology}
            onGoRules={() => go("rules")}
            reload={reload}
          />
        )}
        {route.page === "objects" && <ObjectsPage ontology={ontology} />}
        {route.page === "rules" && <RulesPage ontology={ontology} reload={reload} />}
        {route.page === "history" && <HistoryPage />}
        {route.page === "object" && (
          <ObjectDetailPage kind={route.kind} id={route.id} />
        )}
      </Content>
    </Layout>
  );
}
