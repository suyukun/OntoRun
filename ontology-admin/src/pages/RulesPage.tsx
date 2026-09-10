// 口径确认页：R1-R4 规则卡，是非题式确认 -> POST -> toast 带 commit 短码。
import { useState } from "react";
import { Empty, Input, Typography } from "antd";
import { type Ontology } from "../api";
import RuleCard from "../components/RuleCard";

const { Text, Paragraph } = Typography;

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
