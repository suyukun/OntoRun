// 壳：顶栏导航（图谱首页 / 对象列表 / 口径确认）+ hash 路由 + 全局数据装载。
import { useCallback, useEffect, useState } from "react";
import { Badge, Layout, Menu, Typography } from "antd";
import { api, type Lineage, type Ontology } from "./api";
import GraphHome from "./pages/GraphHome";
import ObjectsPage from "./pages/ObjectsPage";
import RulesPage from "./pages/RulesPage";

const { Header, Content } = Layout;
const { Text } = Typography;

type Route = "graph" | "objects" | "rules";

function routeFromHash(): Route {
  const h = window.location.hash.replace("#/", "");
  return h === "objects" || h === "rules" ? h : "graph";
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

  const go = (r: Route) => {
    window.location.hash = `/#/${r}`;
    setRoute(r);
  };

  const pending = ontology?.summary.pending ?? 0;

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
          selectedKeys={[route]}
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
          ]}
          onClick={(e) => go(e.key as Route)}
        />
        <Text type="secondary" style={{ fontSize: 12, whiteSpace: "nowrap" }}>
          财富广场语义层 · 数据源：registry + lineage（真实数据）
        </Text>
      </Header>
      <Content style={{ overflow: "hidden" }}>
        {route === "graph" && (
          <GraphHome
            lineage={lineage}
            ontology={ontology}
            onGoRules={() => go("rules")}
            reload={reload}
          />
        )}
        {route === "objects" && <ObjectsPage ontology={ontology} />}
        {route === "rules" && <RulesPage ontology={ontology} reload={reload} />}
      </Content>
    </Layout>
  );
}
