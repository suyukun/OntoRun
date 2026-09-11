// 壳：顶栏导航（首页 / 数字与口径 / 口径确认 / 变更历史）+ hash 路由 + 全局数据装载 + 顶栏全局搜索（T301）。
// 对象详情页不入导航：从列表行 / 图谱节点进入（#/object/{kind}/{id}）。
// T503 域图下钻路由：#/graph（域图）→ #/graph/{domainKey}（域内图，drilldown_breadcrumb 第二级）。
import { useCallback, useEffect, useMemo, useState } from "react";
import { AutoComplete, Badge, Layout, Menu, Typography } from "antd";
import { api, type ObjectKind, type Ontology } from "./api";
import GraphHome from "./pages/GraphHome";
import HistoryPage from "./pages/HistoryPage";
import ObjectDetailPage from "./pages/ObjectDetailPage";
import ObjectsPage from "./pages/ObjectsPage";
import RulesPage from "./pages/RulesPage";

const { Header, Content } = Layout;
const { Text } = Typography;

type Page = "graph" | "objects" | "rules" | "history";
type Route =
  | { page: Page; domain?: string }
  | { page: "object"; kind: ObjectKind; id: string };

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
  if (parts[0] === "graph" && parts[1] !== undefined) {
    return { page: "graph", domain: parts[1] };
  }
  return { page: "graph" };
}

export function go(page: Page) {
  window.location.hash = `#/${page}`;
}

// ---- 顶栏全局搜索（T301/US4）----
// 来源=当前 /api/ontology payload（measures/rules/related_tables），纯前端过滤，不建新后端。
const SEARCH_PLACEHOLDER = "搜数字、规则或表名";

function matchKeyword(kw: string, ...texts: string[]): boolean {
  return texts.some((t) => t.toLowerCase().includes(kw));
}

// 分组建议；value 编码 kind:id（kind ∈ measure/rule/table）保证唯一，选中后按它路由。
function buildSearchOptions(ontology: Ontology | null, keyword: string) {
  const kw = keyword.trim().toLowerCase();
  if (!ontology || !kw) return [];
  const groups: { label: string; options: { value: string; label: string }[] }[] = [];
  const measures = ontology.measures.filter((m) => matchKeyword(kw, m.id, m.description));
  if (measures.length > 0) {
    groups.push({
      label: "数字",
      options: measures.map((m) => ({
        value: `measure:${m.id}`,
        label: `${m.id}　${m.description}`,
      })),
    });
  }
  const rules = ontology.rules.filter((r) => matchKeyword(kw, r.id, r.description));
  if (rules.length > 0) {
    groups.push({
      label: "规则",
      options: rules.map((r) => ({
        value: `rule:${r.id}`,
        label: `${r.id}　${r.description}`,
      })),
    });
  }
  const tables = [...new Set(ontology.rules.flatMap((r) => r.related_tables))].filter((t) =>
    matchKeyword(kw, t),
  );
  if (tables.length > 0) {
    groups.push({ label: "表", options: tables.map((t) => ({ value: `table:${t}`, label: t })) });
  }
  return groups;
}

export default function App() {
  const [route, setRoute] = useState<Route>(routeFromHash);
  const [ontology, setOntology] = useState<Ontology | null>(null);

  // T503 后首页域图/域内图组件自取 /api/lineage，App 只装 ontology。
  const reload = useCallback(() => {
    api.ontology().then(setOntology).catch((e) => console.error(e));
  }, []);
  useEffect(reload, [reload]);

  useEffect(() => {
    const onHash = () => setRoute(routeFromHash());
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);

  const pending = ontology?.summary.pending ?? 0;
  const selectedKey = route.page === "object" ? "objects" : route.page;

  const [searchKey, setSearchKey] = useState("");
  const searchOptions = useMemo(
    () => buildSearchOptions(ontology, searchKey),
    [ontology, searchKey],
  );

  // search_direct_hit：数字/表直达对象详情（#/object/{kind}/{id}）；
  // 规则页无路由参数（T301 不动 RulesPage），直达口径确认页即最小直达。
  const onSearchSelect = (value: string) => {
    const sep = value.indexOf(":");
    if (sep < 0) return;
    const kind = value.slice(0, sep);
    const id = value.slice(sep + 1);
    if (kind === "rule") go("rules");
    else window.location.hash = `#/object/${kind}/${encodeURIComponent(id)}`;
    setSearchKey("");
  };

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
            { key: "graph", label: "首页" },
            { key: "objects", label: "数字与口径" },
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
        <AutoComplete
          options={searchOptions}
          value={searchKey}
          onSearch={(v) => {
            // 选项值（kind:id）不作关键词回填：选中后清空输入框，防选中回放值污染
            if (!v.includes(":")) setSearchKey(v);
          }}
          onSelect={onSearchSelect}
          filterOption={false}
          notFoundContent={
            <Text type="secondary" style={{ fontSize: 12 }}>
              没找到？换个词试试——可以用数字名、计算规则或表名
            </Text>
          }
          style={{ width: 280 }}
          placeholder={SEARCH_PLACEHOLDER}
          allowClear
        />
        <Text type="secondary" style={{ fontSize: 12, whiteSpace: "nowrap" }}>
          财富广场 · 数字与计算规则均来自真实数据，有据可查
        </Text>
      </Header>
      <Content style={{ overflow: "hidden" }}>
        {route.page === "graph" && (
          <GraphHome ontology={ontology} domain={route.domain} />
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
