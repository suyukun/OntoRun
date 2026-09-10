// 口径规则卡：RulesPage 与对象详情页共用；readOnly 模式只展示+引导去确认页。
import { useState } from "react";
import { api, type CaliberRule } from "../api";
import { Button, Card, Modal, Space, Tag, Typography, message } from "antd";

const { Text, Paragraph } = Typography;

export default function RuleCard({
  rule,
  confirmer,
  onDone,
  readOnly = false,
}: {
  rule: CaliberRule;
  confirmer: string;
  onDone: () => void;
  readOnly?: boolean;
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
            {rule.id} {rule.status === "confirmed" ? "✅" : "⚠️"}
          </Text>
          {rule.status === "confirmed" ? (
            <Tag color="green">已确认</Tag>
          ) : (
            <Tag color="orange">未确认</Tag>
          )}
        </Space>
      }
      extra={
        readOnly ? undefined : (
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
        )
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
        {readOnly && (
          <Text type="secondary" style={{ fontSize: 12 }}>
            去口径确认页处理 →
          </Text>
        )}
      </Space>
      {!readOnly && (
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
      )}
    </Card>
  );
}
