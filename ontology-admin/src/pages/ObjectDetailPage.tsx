// 对象详情页：头部身份卡 + 概览（属性/绑定并排）/ 口径规则 / 关系 三 Tab。
// 呈现原则：表名/字段名/表达式用代码体，旁边配人话标签，非技术人员能看懂。
import { useEffect, useState, type ReactNode } from "react";
import {
  Alert,
  Breadcrumb,
  Button,
  Card,
  Empty,
  Space,
  Spin,
  Tabs,
  Tag,
  Typography,
} from "antd";
import { api, type LineageEdge, type ObjectDetail, type ObjectKind } from "../api";
import RuleCard from "../components/RuleCard";

const { Text, Paragraph } = Typography;

const KIND_LABEL: Record<ObjectKind, string> = {
  measure: "度量",
  dimension: "维度",
  table: "数据表",
};

const KIND_COLOR: Record<ObjectKind, string> = {
  measure: "blue",
  dimension: "purple",
  table: "green",
};

const LAYER_LABEL: Record<string, string> = {
  ODS: "ODS 贴源",
  CDM: "CDM 明细/维表",
  ADS: "ADS 应用",
  DIM: "DIM 外部维表",
};

const GRID: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))",
  gap: 16,
};

function goHash(hash: string) {
  window.location.hash = hash;
}

function goObject(kind: ObjectKind, id: string) {
  window.location.hash = `#/object/${kind}/${encodeURIComponent(id)}`;
}

function goRules() {
  window.location.hash = "#/rules";
}

function scriptName(path: string) {
  return path.split("/").pop() ?? path;
}

function Code({ v }: { v: string }) {
  return (
    <Text code style={{ fontSize: 12, wordBreak: "break-all" }}>
      {v}
    </Text>
  );
}

function Field({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: ReactNode;
}) {
  return (
    <div style={{ marginBottom: 14 }}>
      <Text type="secondary" style={{ fontSize: 12 }}>
        {label}
      </Text>
      <div style={{ marginTop: 2 }}>{children}</div>
      {hint && (
        <div>
          <Text type="secondary" style={{ fontSize: 12 }}>
            {hint}
          </Text>
        </div>
      )}
    </div>
  );
}

function TableTag({ id }: { id: string }) {
  return (
    <Tag
      style={{ cursor: "pointer" }}
      title="查看这张表的详情"
      onClick={() => goObject("table", id)}
    >
      <Code v={id} />
    </Tag>
  );
}

function ObjTag({ kind, id }: { kind: "measure" | "dimension"; id: string }) {
  return (
    <Tag
      color={kind === "measure" ? "blue" : "purple"}
      style={{ cursor: "pointer" }}
      title="查看详情"
      onClick={() => goObject(kind, id)}
    >
      <Code v={id} />
    </Tag>
  );
}

function MeasureOverview({ d }: { d: ObjectDetail }) {
  const def = d.definition;
  return (
    <div style={GRID}>
      <Card size="small" title="属性（这个指标怎么定义）">
        <Field label="业务含义">{d.description}</Field>
        <Field label="计算公式" hint="{src} 是源表的别名占位，公式与数仓脚本同源">
          <Code v={def.expression ?? "-"} />
        </Field>
        <Field label="按哪个时间字段统计" hint="统计时段（按天/按周）都从它切">
          <Code v={def.time_field ?? "-"} />
        </Field>
        <Field label="先过滤哪些行（WHERE）" hint="不满足条件的行不进统计">
          {(def.filters ?? []).length === 0 ? (
            <Text type="secondary">无过滤条件</Text>
          ) : (
            (def.filters ?? []).map((f) => (
              <div key={f}>
                <Code v={f} />
              </div>
            ))
          )}
        </Field>
      </Card>
      <Card size="small" title="绑定（数从仓库哪张表来）">
        <Field label="源表" hint="点击表名看这张表的上下游与关联规则">
          <TableTag id={def.source_table ?? "-"} />
        </Field>
        <Field label="查询里的表别名" hint="公式里的 {src} 指的就是它">
          <Code v={def.source_alias ?? "-"} />
        </Field>
      </Card>
    </div>
  );
}

function DimensionOverview({ d }: { d: ObjectDetail }) {
  const def = d.definition;
  const j = def.join;
  return (
    <div style={GRID}>
      <Card size="small" title="属性（这个维度怎么取值）">
        <Field label="业务含义">{d.description}</Field>
        {def.expression ? (
          <Field label="取值表达式" hint="{j} 是维表的别名占位">
            <Code v={def.expression} />
          </Field>
        ) : null}
        {def.grains ? (
          <Field label="时间粒度表达式" hint="{t} 是度量的时间字段占位">
            {Object.entries(def.grains).map(([g, expr]) => (
              <div key={g}>
                <Tag>{g}</Tag>
                <Code v={expr} />
              </div>
            ))}
          </Field>
        ) : null}
      </Card>
      <Card size="small" title="绑定（名字从哪张维表来）">
        {j ? (
          <>
            <Field label="维表（字典表）" hint="点击表名看这张表的上下游">
              <TableTag id={j.table} />
            </Field>
            <Field label="JOIN 别名" hint="表达式里的 {j} 指的就是它">
              <Code v={j.alias} />
            </Field>
            <Field label="关联条件（JOIN ON）" hint="{src}=源表，{j}=维表：两边怎么对上号">
              <Code v={j.on} />
            </Field>
            <Field label="从维表取哪些列">
              <Space size={4} wrap>
                {j.select_columns.map((c) => (
                  <Code key={c} v={c} />
                ))}
              </Space>
            </Field>
            <Field
              label="维表快照策略"
              hint={`按 ${j.snapshot_column} 取最新分区（${j.snapshot_policy}）——不挑分区会把历史记录重复算进来`}
            >
              <Code v={j.snapshot_policy} />
            </Field>
          </>
        ) : (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="不绑定维表（时间粒度维度，基于度量时间字段切）"
          />
        )}
      </Card>
    </div>
  );
}

function TableOverview({ d }: { d: ObjectDetail }) {
  const def = d.definition;
  const ms = def.bound_measures ?? [];
  const ds = def.bound_dimensions ?? [];
  return (
    <div style={GRID}>
      <Card size="small" title="表档案">
        <Field label="数仓分层">
          <Tag color="geekblue">{LAYER_LABEL[d.layer ?? ""] ?? d.layer ?? "-"}</Tag>
        </Field>
        <Field label="血缘规模" hint="见「关系」Tab">
          <Text>
            上游 {d.upstream.length} 张 · 下游 {d.downstream.length} 张
          </Text>
        </Field>
        <Field label="关联口径规则">
          {d.rules.length === 0 ? (
            <Text type="secondary">无</Text>
          ) : (
            <Space size={4} wrap>
              {d.rules.map((r) => (
                <Tag key={r.id} color={r.status === "confirmed" ? "green" : "orange"}>
                  {r.id} {r.status === "confirmed" ? "已确认" : "未确认"}
                </Tag>
              ))}
            </Space>
          )}
        </Field>
      </Card>
      <Card size="small" title="绑定本表的语义对象（谁在用这张表）">
        {ms.length === 0 && ds.length === 0 ? (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="还没有度量/维度绑定这张表"
          />
        ) : (
          <>
            <Field label="绑定的度量" hint="点击可看指标口径详情">
              {ms.length === 0 ? (
                <Text type="secondary">无</Text>
              ) : (
                ms.map((m) => (
                  <div key={m.id} title={m.description}>
                    <ObjTag kind="measure" id={m.id} />
                  </div>
                ))
              )}
            </Field>
            <Field label="绑定的维度" hint="点击可看维度取值与维表绑定">
              {ds.length === 0 ? (
                <Text type="secondary">无</Text>
              ) : (
                ds.map((x) => (
                  <div key={x.id} title={x.description}>
                    <ObjTag kind="dimension" id={x.id} />
                  </div>
                ))
              )}
            </Field>
          </>
        )}
      </Card>
    </div>
  );
}

function RulesTab({ d }: { d: ObjectDetail }) {
  if (d.rules.length === 0) return <Empty description="该对象没有关联的口径规则" />;
  return (
    <div>
      <Paragraph type="secondary">
        点卡片去口径确认页处理——确认是一次落身份的 git commit，可追溯。
      </Paragraph>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(380px, 1fr))",
          gap: 16,
        }}
      >
        {d.rules.map((r) => (
          <div key={r.id} style={{ cursor: "pointer" }} title="去口径确认页" onClick={goRules}>
            <RuleCard rule={r} confirmer="" onDone={() => undefined} readOnly />
          </div>
        ))}
      </div>
    </div>
  );
}

function EdgeList({ edges, side }: { edges: LineageEdge[]; side: "up" | "down" }) {
  if (edges.length === 0) return <Text type="secondary">无</Text>;
  return (
    <Space direction="vertical" size={8} style={{ width: "100%" }}>
      {edges.map((e, i) => {
        const other = side === "up" ? e.source : e.target;
        return (
          <div
            key={`${other}#${i}`}
            style={{
              border: `1px solid ${e.unconfirmed ? "#ffccc7" : "#f0f0f0"}`,
              borderRadius: 6,
              padding: "6px 10px",
            }}
          >
            <TableTag id={other} />
            <div>
              <Text
                type="secondary"
                style={{ fontSize: 12 }}
                title={e.via_script}
              >
                {side === "up" ? "产出本表" : "使用本表"} · 经脚本{" "}
                {scriptName(e.via_script)}
              </Text>
            </div>
            {e.unconfirmed && (
              <Text type="danger" style={{ fontSize: 12 }}>
                ⚠ 关联未确认口径
              </Text>
            )}
          </div>
        );
      })}
    </Space>
  );
}

function RelationsTab({ d }: { d: ObjectDetail }) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
        gap: 16,
      }}
    >
      <Card size="small" title={`上游（${d.upstream.length}）—— 谁产出了它`}>
        <EdgeList edges={d.upstream} side="up" />
      </Card>
      <Card size="small" title="本对象">
        <div style={{ textAlign: "center" }}>
          <Tag color={KIND_COLOR[d.kind]}>{KIND_LABEL[d.kind]}</Tag>
          <div style={{ marginTop: 6 }}>
            <Code v={d.id} />
          </div>
          {d.layer && (
            <div style={{ marginTop: 6 }}>
              <Tag color="geekblue">{LAYER_LABEL[d.layer] ?? d.layer}</Tag>
            </div>
          )}
        </div>
      </Card>
      <Card size="small" title={`下游（${d.downstream.length}）—— 它喂给了谁`}>
        <EdgeList edges={d.downstream} side="down" />
      </Card>
    </div>
  );
}

export default function ObjectDetailPage({
  kind,
  id,
}: {
  kind: ObjectKind;
  id: string;
}) {
  const [detail, setDetail] = useState<ObjectDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    setDetail(null);
    setError(null);
    api
      .objectDetail(kind, id)
      .then((d) => {
        if (alive) setDetail(d);
      })
      .catch((e) => {
        if (alive) setError((e as Error).message);
      });
    return () => {
      alive = false;
    };
  }, [kind, id]);

  if (error) {
    return (
      <div style={{ padding: 16 }}>
        <Alert
          type="error"
          showIcon
          message="对象详情加载失败"
          description={`${error}——可能对象不存在，回列表重选。`}
          action={
            <Button onClick={() => goHash("#/objects")}>← 回对象列表</Button>
          }
        />
      </div>
    );
  }
  if (!detail) {
    return (
      <div style={{ padding: 48, textAlign: "center" }}>
        <Spin size="large" />
      </div>
    );
  }

  const confirmedCnt = detail.rules.filter((r) => r.status === "confirmed").length;
  const pendingCnt = detail.rules.length - confirmedCnt;
  const desc =
    detail.description ||
    `数仓表（${LAYER_LABEL[detail.layer ?? ""] ?? detail.layer ?? "未知分层"}）· 上游 ${detail.upstream.length} 张 · 下游 ${detail.downstream.length} 张`;
  const overview =
    detail.kind === "measure" ? (
      <MeasureOverview d={detail} />
    ) : detail.kind === "dimension" ? (
      <DimensionOverview d={detail} />
    ) : (
      <TableOverview d={detail} />
    );

  return (
    <div
      style={{
        padding: 16,
        overflow: "auto",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        gap: 12,
      }}
    >
      <Breadcrumb
        items={[
          { title: <a onClick={() => goHash("#/objects")}>对象列表</a> },
          { title: <Text code>{detail.id}</Text> },
        ]}
      />
      <Card>
        <Space direction="vertical" size={6}>
          <Space size={8} wrap>
            <Text code style={{ fontSize: 18 }}>
              {detail.id}
            </Text>
            <Tag color={KIND_COLOR[detail.kind]}>{KIND_LABEL[detail.kind]}</Tag>
            {detail.layer && (
              <Tag color="geekblue">{LAYER_LABEL[detail.layer] ?? detail.layer}</Tag>
            )}
            {detail.unconfirmed && <Tag color="red">⚠ 血缘上有未确认口径</Tag>}
          </Space>
          <div>
            {detail.rules.length === 0 ? (
              <Tag>无关联口径规则</Tag>
            ) : pendingCnt === 0 ? (
              <Tag color="green">✅ 口径全部已确认（{confirmedCnt} 条）</Tag>
            ) : (
              <Tag color="orange">
                ⚠ {pendingCnt}/{detail.rules.length} 条口径待确认
              </Tag>
            )}
          </div>
          <Paragraph type="secondary" style={{ marginBottom: 0 }}>
            {desc}
          </Paragraph>
        </Space>
      </Card>
      <Tabs
        defaultActiveKey="overview"
        items={[
          { key: "overview", label: "概览", children: overview },
          {
            key: "rules",
            label: `口径规则（${detail.rules.length}）`,
            children: <RulesTab d={detail} />,
          },
          {
            key: "relations",
            label: `关系（上 ${detail.upstream.length} / 下 ${detail.downstream.length}）`,
            children: <RelationsTab d={detail} />,
          },
        ]}
      />
    </div>
  );
}
