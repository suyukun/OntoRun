// 「数字与口径」数字目录（T501/US4）：页面主体 = 数字卡网格，每卡一个数字——
// 首行人话名（catalog_plain_names：禁裸 ID/表名前缀打头）+ 一句话含义 + 算式人话版 +
// 版本行（口径状态摘要）+ 可信度徽章（qc11：已确认绿/待确认橙）+ 所属域人话徽标（无域不显示）+
// 试算入口（「试一下」→ GET /api/trial/{口径锚规则}?month=当月，失败灰条「试算暂不可用」，
// T205 同款容错）。维度列表降为默认收起的速查折叠，原 Tabs 退役。文案跟随 T-U1 人话基线。
import { useState } from "react";
import { Button, Card, Collapse, Space, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";
import type { Dimension, Measure, Ontology, TrialResult } from "../api";

const { Text } = Typography;

function Code({ v }: { v: string }) {
  return (
    <Text code style={{ fontSize: 12, wordBreak: "break-all" }}>
      {v}
    </Text>
  );
}

// 默认试算月 = 当前月（YYYY-MM），与 RuleCard 试算行同口径。
function currentMonth(): string {
  const now = new Date();
  return now.getFullYear() + "-" + String(now.getMonth() + 1).padStart(2, "0");
}

// 描述「注册用户数：注册 KPI 明细去重用户数（…）」→ 冒号前段作首行人话名，
// 余下作一句话含义（现值人话化）；无冒号整句作名、含义中性留白（不编造）。
function splitPlainName(description: string): { name: string; meaning: string } {
  const sep = description.indexOf("：");
  if (sep <= 0) return { name: description.trim(), meaning: "" };
  return {
    name: description.slice(0, sep).trim(),
    meaning: description.slice(sep + 1).trim(),
  };
}

// 算式人话版：只翻认识的聚合模式（COUNT(DISTINCT {src}.col) → 按 col 去重计数）；
// 写不出返回 null，调用方显示表达式原文小字（不硬翻、不编造）。
function plainExpression(expression: string): string | null {
  const distinct = /^COUNT\(DISTINCT \{src\}\.(\w+)\)$/i.exec(expression.trim());
  return distinct ? "按 " + distinct[1] + " 去重计数" : null;
}

function formatTime(iso: string): string {
  return iso.replace("T", " ").slice(0, 16);
}

// 版本行（口径状态摘要）：已确认 → 存档编号+确认人+时间；待确认 → 标记，
// 有历史记录注明最近记录（含驳回，不冒充确认）；无关联规则如实说明。
function CaliberVersionLine({ measure }: { measure: Measure }) {
  const c = measure.caliber;
  if (!c) {
    return (
      <Text type="secondary" style={{ fontSize: 12 }}>
        待确认 · 该数字暂无登记的口径规则
      </Text>
    );
  }
  if (c.status === "confirmed") {
    return (
      <Text type="secondary" style={{ fontSize: 12 }}>
        {"已确认 · 存档编号 " + (c.commit ?? c.code ?? "无")}
        {c.confirmer ? " · " + c.confirmer : ""}
        {c.time ? " · " + formatTime(c.time) : ""}
      </Text>
    );
  }
  const lastNote =
    c.confirmer && c.time
      ? "最近记录：" +
        c.confirmer +
        " " +
        formatTime(c.time) +
        (c.verdict === "rejected" ? "（驳回）" : "")
      : "暂无确认记录";
  return (
    <Text type="secondary" style={{ fontSize: 12 }}>
      {"待确认 · " + lastNote}
    </Text>
  );
}

function MeasureCard({ measure }: { measure: Measure }) {
  const [trial, setTrial] = useState<TrialResult | null>(null);
  const [trialFailed, setTrialFailed] = useState(false);
  const [trying, setTrying] = useState(false);
  const { name, meaning } = splitPlainName(measure.description);
  const plain = plainExpression(measure.expression);
  const confirmed = measure.caliber?.status === "confirmed";

  // 试算入口：任何失败 → 灰条「试算暂不可用」（T205 同款容错），不阻塞浏览。
  const runTrial = () => {
    if (!measure.caliber || trying) return;
    setTrying(true);
    fetch("/api/trial/" + measure.caliber.rule_id + "?month=" + currentMonth())
      .then((res) =>
        res.ok ? res.json() : Promise.reject(new Error(String(res.status)))
      )
      .then((data: TrialResult) => setTrial(data))
      .catch(() => setTrialFailed(true))
      .finally(() => setTrying(false));
  };

  return (
    <Card
      size="small"
      title={
        <Space size={8}>
          {confirmed ? (
            <Tag color="green">已确认</Tag>
          ) : (
            <Tag color="orange">待确认</Tag>
          )}
          <Text strong>{name}</Text>
        </Space>
      }
      extra={
        <Text type="secondary" code style={{ fontSize: 12 }}>
          {measure.id}
        </Text>
      }
      style={{ height: "100%" }}
    >
      <Space direction="vertical" size={6} style={{ width: "100%" }}>
        <Text>{meaning || "含义暂无登记，待补一句话说明"}</Text>
        <div>
          <Text type="secondary" style={{ fontSize: 12 }}>
            怎么算的：
          </Text>
          {plain ? (
            <Text>{plain}</Text>
          ) : (
            <Text code style={{ fontSize: 12, wordBreak: "break-all" }}>
              {measure.expression}
            </Text>
          )}
        </div>
        <CaliberVersionLine measure={measure} />
        <Space wrap size={8}>
          {measure.domain_name ? <Tag color="blue">{measure.domain_name}</Tag> : null}
          {measure.caliber ? (
            <Button size="small" loading={trying} onClick={runTrial}>
              试一下
            </Button>
          ) : null}
        </Space>
        {trialFailed ? (
          <div
            style={{
              background: "#fafafa",
              border: "1px solid #f0f0f0",
              borderRadius: 4,
              padding: "4px 8px",
              fontSize: 12,
              color: "#8c8c8c",
            }}
          >
            试算暂不可用
          </div>
        ) : null}
        {trial ? (
          <Text>
            {"📊 试算：" + trial.month + " = " + trial.value + " " + trial.unit}
          </Text>
        ) : null}
        <div>
          <a href={"#/object/measure/" + encodeURIComponent(measure.id)}>
            查看详情 →
          </a>
        </div>
      </Space>
    </Card>
  );
}

export default function ObjectsPage({ ontology }: { ontology: Ontology | null }) {
  if (!ontology) return <Text>加载中…</Text>;

  const dimRowNav = (row: { id: string }) => ({
    onClick: () => {
      window.location.hash = "#/object/dimension/" + encodeURIComponent(row.id);
    },
    style: { cursor: "pointer" as const },
    title: "查看详情",
  });

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

  return (
    <div style={{ padding: 16 }}>
      <Space direction="vertical" size={16} style={{ width: "100%" }}>
        <div>
          <Typography.Title level={5} style={{ marginBottom: 4 }}>
            数字与口径 · 数字目录
          </Typography.Title>
          <Text type="secondary">
            这里是全部数字的名册：每个数字是什么意思、怎么算、谁确认过，一眼看明白。
            点「试一下」当场算给你看；要确认或改口径，去「口径确认」页。
          </Text>
        </div>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
            gap: 16,
          }}
        >
          {ontology.measures.map((m) => (
            <MeasureCard key={m.id} measure={m} />
          ))}
        </div>
        {/* 维度降折叠速查（原 Tabs 退役）：默认收起，点开即完整维度表 */}
        <Collapse
          items={[
            {
              key: "dimensions",
              label: "维度速查（" + ontology.dimensions.length + "）",
              children: (
                <Table
                  rowKey="id"
                  columns={dimCols}
                  dataSource={ontology.dimensions}
                  pagination={false}
                  size="middle"
                  onRow={dimRowNav}
                />
              ),
            },
          ]}
        />
      </Space>
    </div>
  );
}