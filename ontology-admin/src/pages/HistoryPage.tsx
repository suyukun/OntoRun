// 变更历史页：git log 人话化时间线（时间 / 作者 / 改了什么 / 存档编号）。
// T502（US5）：git 降级诚实标记 + 作者/类型筛选（类型/作者前端过滤，
// 规则/关联表透传 T102 后端参数 ?rule_id=&object=）。
import { useEffect, useState } from "react";
import {
  Alert,
  Button,
  Card,
  Empty,
  Select,
  Segmented,
  Space,
  Spin,
  Tag,
  Timeline,
  Typography,
} from "antd";
import { api, type CaliberRule, type HistoryCommit, type HistoryPayload } from "../api";

const { Text, Paragraph } = Typography;

// conventional commit 前缀 -> Timeline 颜色
const TYPE_COLOR: Record<string, string> = {
  feat: "green",
  fix: "red",
  docs: "blue",
  refactor: "purple",
  test: "cyan",
  chore: "gray",
  perf: "geekblue",
  ci: "gold",
  style: "gray",
};

// 记录类别（T502）。人话口径沿 T-U1：escalate=上报老板。
type RecordKind = "confirm" | "decision" | "escalate" | "other";

const KIND_LABEL: Record<RecordKind, string> = {
  confirm: "口径确认",
  decision: "分歧裁决",
  escalate: "上报老板",
  other: "其他提交",
};

const KIND_TAG_COLOR: Record<RecordKind, string | undefined> = {
  confirm: "green",
  decision: "geekblue",
  escalate: "red",
  other: undefined,
};

type KindFilter = RecordKind | "all";

const KIND_OPTIONS: { label: string; value: KindFilter }[] = [
  { label: "全部类型", value: "all" },
  { label: KIND_LABEL.confirm, value: "confirm" },
  { label: KIND_LABEL.decision, value: "decision" },
  { label: KIND_LABEL.escalate, value: "escalate" },
  { label: KIND_LABEL.other, value: "other" },
];

// 类别判据（与 confirm_store 落盘的 commit subject 格式一一对应）：
// ESCALATED = 上报老板留痕；「| <rule> verdict: 」后缀 = R8 三选一裁决；
// chore(fortune-admin): rule 前缀 = 普通确认/驳回；其余 = 开发类提交。
function kindOf(subject: string): RecordKind {
  if (subject.includes("ESCALATED")) return "escalate";
  const isRuleRecord = subject.startsWith("chore(fortune-admin): rule ");
  if (isRuleRecord && subject.includes(" verdict: ")) return "decision";
  return isRuleRecord ? "confirm" : "other";
}

// 作者口径 = 确认人/裁决人（A2-US5）：确认/裁决记录从 message 的「by X」抽取，
// 不用 git 提交人——git author 恒为仓库主人，信任链要的是「谁确认的」。
function authorOf(c: HistoryCommit): string {
  const m = c.subject.match(/ by (.+?)(?: \[code:|$)/);
  return c.subject.startsWith("chore(fortune-admin): rule ") && m ? m[1] : c.author;
}

function typeOf(subject: string) {
  return subject.split(":", 1)[0].split("(", 1)[0].trim();
}

function fmtTime(iso: string) {
  return iso.replace("T", " ").slice(0, 16);
}

const VERDICT_CN: Record<string, string> = {
  confirmed: "确认",
  rejected: "驳回",
  escalated: "上报老板裁决",
};

// 降级记录（git 不可用只写 confirmations.json）：前端唯一来源是
// /api/ontology 的 last_record——后端按短码反查不到 commit 即降级记录
// （运行时 payload 不含 mode 字段，判据只能用 commit === null）。
interface DegradedEntry {
  ruleId: string;
  verdict: string;
  confirmer: string;
  time: string;
}

function degradedEntries(rules: CaliberRule[]): DegradedEntry[] {
  return rules
    .filter((r) => r.last_record !== null && r.last_record.commit === null)
    .map((r) => ({
      ruleId: r.id,
      verdict: r.last_record ? r.last_record.verdict : "",
      confirmer: r.last_record ? r.last_record.confirmer : "",
      time: r.last_record ? r.last_record.time : "",
    }))
    .sort((a, b) => (a.time < b.time ? 1 : -1));
}

const HISTORY_LIMIT = 50;

export default function HistoryPage() {
  const [data, setData] = useState<HistoryPayload | null>(null);
  const [rules, setRules] = useState<CaliberRule[]>([]);
  const [degraded, setDegraded] = useState<DegradedEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  // 筛选：类型/作者=前端过滤；规则/关联表=透传后端（T102）重新拉取。
  const [kind, setKind] = useState<KindFilter>("all");
  const [author, setAuthor] = useState<string | null>(null);
  const [ruleId, setRuleId] = useState<string | null>(null);
  const [object, setObject] = useState<string | null>(null);

  const loadOntology = () => {
    // 降级标记与筛选选项尽力而为：ontology 不可用不阻塞 git 历史主内容。
    api
      .ontology()
      .then((o) => {
        setRules(o.rules);
        setDegraded(degradedEntries(o.rules));
      })
      .catch(() => undefined);
  };

  const loadHistory = () => {
    setError(null);
    const params = new URLSearchParams({ limit: String(HISTORY_LIMIT) });
    if (ruleId) params.set("rule_id", ruleId);
    if (object) params.set("object", object);
    fetch(`/api/history?${params.toString()}`)
      .then(async (res) => {
        if (!res.ok) throw new Error(`/api/history -> HTTP ${res.status}`);
        return (await res.json()) as HistoryPayload;
      })
      .then(setData)
      .catch((e) => setError((e as Error).message));
  };

  useEffect(loadOntology, []);
  useEffect(loadHistory, [ruleId, object]);

  const commits = data ? data.commits : [];
  const visible = commits.filter(
    (c) =>
      (kind === "all" || kindOf(c.subject) === kind) &&
      (author === null || authorOf(c) === author),
  );
  // 作者选项从当前记录去重（规则/表筛选后选项随窗口收窄）
  const authors = [...new Set(commits.map(authorOf))];
  const ruleOptions = rules.map((r) => ({
    value: r.id,
    label: `${r.id}　${r.description}`,
  }));
  const objectOptions = [...new Set(rules.flatMap((r) => r.related_tables))].map(
    (t) => ({ value: t, label: t }),
  );
  const hasFilter =
    kind !== "all" || author !== null || ruleId !== null || object !== null;
  const resetFilters = () => {
    setKind("all");
    setAuthor(null);
    setRuleId(null);
    setObject(null);
  };

  if (error) {
    return (
      <div style={{ padding: 16 }}>
        <Empty description={`变更历史加载失败：${error}`} />
      </div>
    );
  }
  if (!data) {
    return (
      <div style={{ padding: 48, textAlign: "center" }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ padding: 16, overflow: "auto", height: "100%" }}>
      <Card
        title="变更历史"
        extra={
          <Space>
            <Text type="secondary" style={{ fontSize: 12 }}>
              {hasFilter
                ? `筛选出 ${visible.length} / ${commits.length} 条`
                : `最近 ${data.count} 次（每一次口径确认都会留痕在此）`}
            </Text>
            <Button
              size="small"
              onClick={() => {
                loadOntology();
                loadHistory();
              }}
            >
              刷新
            </Button>
          </Space>
        }
      >
        <Paragraph type="secondary" style={{ marginBottom: 16 }}>
          本体管理台的所有改动（口径确认、规则调整）都走 git commit——这里是
          人话版账本：谁、什么时候、改了什么。
        </Paragraph>
        {degraded.length > 0 && (
          <Alert
            type="warning"
            showIcon
            style={{ marginBottom: 16 }}
            message={
              `git 降级提醒：${degraded.length} 条规则的确认未产生存档编号（降级记录）`
            }
            description={
              <>
                <Paragraph type="secondary" style={{ marginBottom: 8 }}>
                  这些操作当时 git 不可用，只写入了本地备份文件，没有形成 git
                  历史，所以下方时间线里查不到：
                </Paragraph>
                {degraded.map((d) => (
                  <Text key={d.ruleId + d.time} style={{ display: "block" }}>
                    <Text strong>{d.ruleId}</Text>　{d.confirmer}　
                    {fmtTime(d.time)}　{VERDICT_CN[d.verdict] ?? d.verdict}
                    　—— 未产生存档编号
                  </Text>
                ))}
              </>
            }
          />
        )}
        <Space wrap style={{ marginBottom: 16 }}>
          <Segmented
            value={kind}
            onChange={(v) => setKind(v as KindFilter)}
            options={KIND_OPTIONS}
          />
          <Select
            value={author}
            onChange={(v) => setAuthor(v ?? null)}
            allowClear
            placeholder="全部作者"
            style={{ minWidth: 140 }}
            options={authors.map((a) => ({ value: a, label: a }))}
          />
          <Select
            value={ruleId}
            onChange={(v) => setRuleId(v ?? null)}
            allowClear
            placeholder="按规则查（口径规则）"
            style={{ minWidth: 220 }}
            options={ruleOptions}
          />
          <Select
            value={object}
            onChange={(v) => setObject(v ?? null)}
            allowClear
            placeholder="按关联表查"
            style={{ minWidth: 180 }}
            options={objectOptions}
          />
          {hasFilter && (
            <Button size="small" onClick={resetFilters}>
              清除筛选
            </Button>
          )}
        </Space>
        {visible.length === 0 ? (
          hasFilter ? (
            <Empty description="当前筛选下没有匹配记录">
              <Button size="small" onClick={resetFilters}>
                清除筛选
              </Button>
            </Empty>
          ) : (
            <Empty description="还没有任何提交" />
          )
        ) : (
          <Timeline
            items={visible.map((c) => {
              const k = kindOf(c.subject);
              return {
                color: TYPE_COLOR[typeOf(c.subject)] ?? "gray",
                children: (
                  <Space direction="vertical" size={0} style={{ paddingBottom: 4 }}>
                    <Space size={8} wrap>
                      {k !== "other" && (
                        <Tag color={KIND_TAG_COLOR[k]}>{KIND_LABEL[k]}</Tag>
                      )}
                      <Tag>{authorOf(c)}</Tag>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        {fmtTime(c.time)}
                      </Text>
                      <Text code style={{ fontSize: 12 }} title={c.subject}>
                        {c.short}
                      </Text>
                    </Space>
                    <Text>{c.human}</Text>
                  </Space>
                ),
              };
            })}
          />
        )}
      </Card>
    </div>
  );
}
