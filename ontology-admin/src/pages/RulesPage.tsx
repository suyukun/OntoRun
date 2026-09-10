// 口径确认页：R1-R4 规则卡，是非题式确认 -> POST -> toast 带 commit 短码。
import { useState } from "react";
import { Button, Card, Empty, Input, Modal, Space, Tag, Typography, message } from "antd";
import { api, type CaliberRule, type Ontology } from "../api";

const { Text, Paragraph } = Typography;

function RuleCard({
  rule,
  confirmer,
  onDone,
}: {
  rule: CaliberRule;
  confirmer: string;
  onDone: () => void;
}) {
  const [loading, setLoading] = useState<string | null>(null);
  const [rejecting, setRejecting] = useState(false);

  const submit = async (verdict: "confirmed" | "rejected") => {
    if (!confirmer.trim()) {
      message.warning("请先在页首填写确认人（确认要落身份，进 git 历史）");
      return;
    }
    setLoading(verdict);
    try {
      const res = await api.confirmRule(rule.id, verdict, confirmer.trim());
      message.success(
        `${res.message}（commit ${res.record.commit ?? "无"}）`,
        5
      );
      setRejecting(false);
      onDone();
    } catch (e) {
      message.error(`确认失败：${(e as Error).message}`);
    } finally {
      setLoading(null);
    }
  };

  const last = rule.last_record;
  return (
    <Card
      title={
        <Space>
          <Text strong>
            {rule.id}{" "}
            {rule.status === "confirmed" ? "✅" : "⚠️"}
          </Text>
          {rule.status === "confirmed" ? (
            <Tag color="green">已确认</Tag>
          ) : (
            <Tag color="orange">未确认</Tag>
          )}
        </Space>
      }
      extra={
        <Space>
          <Button
            type="primary"
            disabled={rule.status === "confirmed"}
            loading={loading === "confirmed"}
            onClick={() => submit("confirmed")}
          >
            ✓ 对，仍生效
          </Button>
          <Button danger onClick={() => setRejecting(true)}>
            ✗ 不再生效
          </Button>
        </Space>
      }
      style={{
        borderColor: rule.status === "confirmed" ? "#b7eb8f" : "#ffd591",
        height: "100%",
      }}
    >
      <Paragraph strong>{rule.description}</Paragraph>
      <Space direction="vertical" size={4} style={{ width: "100%" }}>
        <Text type="secondary" style={{ fontSize: 12 }}>
          📎 出处：
        </Text>
        <Text code style={{ fontSize: 12, wordBreak: "break-all" }}>
          {rule.source_script}
        </Text>
        <div>
          <Text type="secondary" style={{ fontSize: 12 }}>
            影响表：
          </Text>
          {rule.related_tables.map((t) => (
            <Tag key={t}>{t}</Tag>
          ))}
        </div>
        <Text type="secondary" style={{ fontSize: 12 }}>
          上次确认：
          {last
            ? `${last.confirmer} ${last.time.replace("T", " ").slice(0, 16)}（${last.verdict === "confirmed" ? "确认" : "驳回"}，commit ${last.commit ?? "-"}）`
            : "无"}
        </Text>
      </Space>
      <Modal
        title={`驳回 ${rule.id}？`}
        open={rejecting}
        onCancel={() => setRejecting(false)}
        onOk={() => submit("rejected")}
        confirmLoading={loading === "rejected"}
        okText={`驳回（以 ${confirmer.trim() || "未填名"} 记录，回到未确认）`}
        cancelText="取消"
      >
        <Paragraph type="secondary">
          驳回会回到未确认队列并留痕（新 commit）。确认人取页首填写：
          <Text strong>{confirmer.trim() || "（未填）"}</Text>
        </Paragraph>
      </Modal>
    </Card>
  );
}

export default function RulesPage({
  ontology,
  reload,
}: {
  ontology: Ontology | null;
  reload: () => void;
}) {
  const [confirmer, setConfirmer] = useState("");
  if (!ontology) return <Empty description="加载中…" />;
  const sorted = [...ontology.rules].sort((a, b) =>
    a.status === b.status ? a.id.localeCompare(b.id) : a.status === "unverified" ? -1 : 1
  );
  return (
    <div style={{ padding: 16, overflow: "auto", height: "100%" }}>
      <Paragraph type="secondary">
        每张卡是一个是非题：这条口径现在还成立吗？确认 = 一次带身份的 git commit，
        版本可追溯。待确认 {ontology.summary.pending} 条。
      </Paragraph>
      <div style={{ marginBottom: 16, display: "flex", alignItems: "center", gap: 8 }}>
        <Text strong>确认人：</Text>
        <Input
          placeholder="你的名字（落 git 历史，如：王工）"
          value={confirmer}
          onChange={(e) => setConfirmer(e.target.value)}
          style={{ maxWidth: 280 }}
          allowClear
        />
        {!confirmer.trim() && (
          <Text type="warning" style={{ fontSize: 12 }}>
            未填名不能确认——身份是确认的一部分
          </Text>
        )}
      </div>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(420px, 1fr))",
          gap: 16,
        }}
      >
        {sorted.map((r) => (
          <RuleCard key={r.id} rule={r} confirmer={confirmer} onDone={reload} />
        ))}
      </div>
    </div>
  );
}
