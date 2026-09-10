// 对象列表页：度量 / 维度 / 口径规则 三个分区（本体目录）。
import { Tabs, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";
import type { CaliberRule, Dimension, Measure, Ontology } from "../api";

const { Text } = Typography;

function Code({ v }: { v: string }) {
  return (
    <Text code style={{ fontSize: 12, wordBreak: "break-all" }}>
      {v}
    </Text>
  );
}

export default function ObjectsPage({ ontology }: { ontology: Ontology | null }) {
  if (!ontology) return <Text>加载中…</Text>;

  const goObject = (kind: "measure" | "dimension", id: string) => {
    window.location.hash = `#/object/${kind}/${encodeURIComponent(id)}`;
  };
  const rowNav =
    (kind: "measure" | "dimension") => (row: { id: string }) => ({
      onClick: () => goObject(kind, row.id),
      style: { cursor: "pointer" as const },
      title: "查看详情",
    });

  const measureCols: ColumnsType<Measure> = [
    { title: "ID", dataIndex: "id", width: 140 },
    { title: "业务含义", dataIndex: "description" },
    {
      title: "表达式",
      dataIndex: "expression",
      render: (v: string) => <Code v={v} />,
    },
    { title: "源表", dataIndex: "source_table", render: (v) => <Code v={v} /> },
    { title: "时间字段", dataIndex: "time_field", width: 120 },
  ];

  const dimCols: ColumnsType<Dimension> = [
    { title: "ID", dataIndex: "id", width: 140 },
    { title: "业务含义", dataIndex: "description" },
    {
      title: "维表 JOIN",
      key: "join",
      render: (_, d) =>
        d.join ? (
          <span>
            <Code v={d.join.table} />
            <Text type="secondary" style={{ fontSize: 12 }}>
              {" "}
              ON {d.join.on.replace("{src}", "源表").replace("{j}", d.join.alias)} ·
              快照 {d.join.snapshot_policy}
            </Text>
          </span>
        ) : (
          <Text type="secondary">无（表达式/时间粒度）</Text>
        ),
    },
    {
      title: "表达式",
      dataIndex: "expression",
      render: (v: string) => (v ? <Code v={v} /> : "-"),
    },
  ];

  const ruleCols: ColumnsType<CaliberRule> = [
    { title: "ID", dataIndex: "id", width: 80 },
    { title: "口径规则（人话）", dataIndex: "description" },
    {
      title: "出处脚本",
      dataIndex: "source_script",
      render: (v: string) => <Code v={v} />,
    },
    {
      title: "状态",
      dataIndex: "status",
      width: 100,
      render: (s: string) =>
        s === "confirmed" ? (
          <Tag color="green">已确认</Tag>
        ) : (
          <Tag color="orange">未确认</Tag>
        ),
    },
  ];

  return (
    <div style={{ padding: 16 }}>
      <Tabs
        items={[
          {
            key: "measures",
            label: `度量（${ontology.measures.length}）`,
            children: (
              <Table
                rowKey="id"
                columns={measureCols}
                dataSource={ontology.measures}
                pagination={false}
                size="middle"
                onRow={(m) => rowNav("measure")(m)}
              />
            ),
          },
          {
            key: "dimensions",
            label: `维度（${ontology.dimensions.length}）`,
            children: (
              <Table
                rowKey="id"
                columns={dimCols}
                dataSource={ontology.dimensions}
                pagination={false}
                size="middle"
                onRow={(d) => rowNav("dimension")(d)}
              />
            ),
          },
          {
            key: "rules",
            label: `口径规则（${ontology.rules.length} · 未确认 ${ontology.summary.pending}）`,
            children: (
              <Table
                rowKey="id"
                columns={ruleCols}
                dataSource={ontology.rules}
                pagination={false}
                size="middle"
                onRow={() => ({
                  onClick: () => {
                    window.location.hash = "#/rules";
                  },
                  style: { cursor: "pointer" },
                  title: "去口径确认页",
                })}
              />
            ),
          },
        ]}
      />
    </div>
  );
}
