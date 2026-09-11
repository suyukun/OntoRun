// 口径确认页（US1 确认队列，T101）：未确认置顶 + 页头计数 + 筛选（出处脚本/所属对象）+ 单列纵排。
// 排队时长只认现状 payload（无注册/创建时间字段，不造数），取法见 queueStart 注释；
// 卡片内「排队 N 天」元信息归 RuleCard（T205 L1），页面只负责排序。
import { useMemo, useState } from "react";
import { Button, Empty, Input, Select, Typography } from "antd";
import { type CaliberRule, type Ontology } from "../api";
import RuleCard from "../components/RuleCard";

const { Text, Paragraph } = Typography;

// 排队起点毫秒值（现状数据如实取法）：
// - 待确认且有 last_record：取 last_record.time —— 最近一次驳回/留痕把规则送回队列的时刻；
// - 待确认且无 last_record：payload 没有注册时间，起点不可知；但任何确认记录必晚于规则注册，
//   此类规则排队时长必然 ≥ 一切可计算时长，按「最早排队」处理（排待确认组最前）；
// - 已确认：不在排队中，返回 null。
// 时间不可解析视同无数据（null），不为脏数据猜时刻。
function queueStart(rule: CaliberRule): number | null {
  if (rule.status !== "unverified" || !rule.last_record) return null;
  const t = Date.parse(rule.last_record.time);
  return Number.isNaN(t) ? null : t;
}

// rules_page_sort_and_count：待确认置顶、已确认沉底；待确认组内排队时长降序
// （起点越早 = 等越久 = 越靠前），起点同档按 id 稳定排序。
function compareRules(a: CaliberRule, b: CaliberRule): number {
  if (a.status !== b.status) return a.status === "unverified" ? -1 : 1;
  if (a.status === "unverified") {
    const sa = queueStart(a);
    const sb = queueStart(b);
    if (sa !== sb) {
      if (sa === null) return -1;
      if (sb === null) return 1;
      return sa - sb;
    }
  }
  return a.id.localeCompare(b.id);
}

export default function RulesPage({
  ontology,
  reload,
}: {
  ontology: Ontology | null;
  reload: () => void;
}) {
  const [confirmer, setConfirmer] = useState("");
  const [scriptFilter, setScriptFilter] = useState<string | undefined>(undefined);
  const [tableFilter, setTableFilter] = useState<string | undefined>(undefined);

  // 筛选选项从当前 payload 去重生成，不引入 payload 之外的候选值
  const scriptOptions = useMemo(
    () =>
      ontology
        ? [...new Set(ontology.rules.map((r) => r.source_script).filter(Boolean))]
            .sort()
            .map((s) => ({ value: s, label: s }))
        : [],
    [ontology],
  );
  const tableOptions = useMemo(
    () =>
      ontology
        ? [...new Set(ontology.rules.flatMap((r) => r.related_tables))]
            .sort()
            .map((s) => ({ value: s, label: s }))
        : [],
    [ontology],
  );

  if (!ontology) return <Empty description="加载中…" />;

  const shown = ontology.rules
    .filter(
      (r) =>
        (!scriptFilter || r.source_script === scriptFilter) &&
        (!tableFilter || r.related_tables.includes(tableFilter)),
    )
    .sort(compareRules);
  // 页头计数随筛选与确认状态走：数「当前筛选下」的待确认条数，不取全量 summary
  const pendingShown = shown.filter((r) => r.status === "unverified").length;

  const clearFilters = () => {
    setScriptFilter(undefined);
    setTableFilter(undefined);
  };

  return (
    <div style={{ padding: 24, overflow: "auto", height: "100%" }}>
      <Paragraph className="page-intro" type="secondary">
        这里列出系统里所有数字的计算规则。没核对过的排前面——看懂了就在上方填上名字，
        点卡上的「对，就这样算」确认；拿不准的选「上报老板」，都会存档留痕、随时可查。
        当前待确认 {pendingShown} 条 / 列表共 {shown.length} 条。
      </Paragraph>
      <div
        style={{
          marginTop: 16,
          display: "flex",
          alignItems: "center",
          gap: 8,
          flexWrap: "wrap",
        }}
      >
        <Text strong>确认人：</Text>
        <Input
          placeholder="你的名字（确认记录会写上它，如：王工）"
          value={confirmer}
          onChange={(e) => setConfirmer(e.target.value)}
          style={{ width: 280 }}
          allowClear
        />
        <Select
          allowClear
          placeholder="出处脚本"
          value={scriptFilter}
          onChange={(v) => setScriptFilter(v)}
          options={scriptOptions}
          style={{ width: 240 }}
        />
        <Select
          allowClear
          placeholder="所属对象"
          value={tableFilter}
          onChange={(v) => setTableFilter(v)}
          options={tableOptions}
          style={{ width: 220 }}
        />
        {!confirmer.trim() && (
          <Text type="warning" style={{ fontSize: 12 }}>
            未填名不能确认——身份是确认的一部分
          </Text>
        )}
      </div>
      {/* 单列纵排（设计稿 §5.1：双列网格退役）；间距档：区块间 32、卡间距 16（容器 padding 24） */}
      <div
        data-testid="rules-queue"
        style={{
          marginTop: 32,
          display: "flex",
          flexDirection: "column",
          alignItems: "stretch",
          gap: 16,
        }}
      >
        {shown.length === 0 ? (
          <Empty description="当前筛选下没有匹配的计算规则——换个筛选条件试试">
            <Button onClick={clearFilters}>清除筛选，看全部</Button>
          </Empty>
        ) : (
          shown.map((r) => (
            <RuleCard key={r.id} rule={r} confirmer={confirmer} onDone={reload} />
          ))
        )}
      </div>
    </div>
  );
}
