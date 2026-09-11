// R8 分歧裁决卡（T203，非是非题）：两口径并列对读（label/证据数字/适用场景，
// 人话优先），裁决四选项——账户/用户/双口径并存（推荐，NC-Q2，默认预选）/
// 升级老板裁决。前三项走正常确认流（confirm+commit，toast 含版本短码）；
// escalate 只留痕不翻转状态（王工走查修订5：toast「已留痕并通知负责人（线下）」，
// 卡仍待确认、可再次裁决）。本组件只做裁决交互区，嵌在 RuleCard 行动区位置。
import { useState } from "react";
import { api, type CaliberRule, type DecisionOptionKey } from "../api";
import { Button, Radio, Space, Tag, Typography, message } from "antd";

const { Text } = Typography;

// 四选项是固定契约（DecisionOptionKey，A8/PC-3 逃生口）；两口径的人话全称
// 在上方对照区（来自 payload），此处用短标签避免重复长句。
const VERDICT_OPTIONS: { key: DecisionOptionKey; label: string }[] = [
  { key: "account", label: "按账户计数" },
  { key: "user", label: "按用户去重" },
  { key: "both", label: "双口径并存" },
  { key: "escalate", label: "升级老板裁决" },
];

export default function DivergenceCard({
  rule,
  confirmer,
  onDone,
}: {
  rule: CaliberRule;
  confirmer: string;
  onDone: () => void;
}) {
  // NC-Q2 双口径并存是推荐解：默认预选 both
  const [option, setOption] = useState<DecisionOptionKey>("both");
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    if (!confirmer.trim()) {
      message.warning("请先在页首填写确认人（确认要落身份，进 git 历史）");
      return;
    }
    setLoading(true);
    try {
      if (option === "escalate") {
        // 逃生口（A4-7）：只留痕不改状态——后端保持待确认，前端不触发刷新，
        // 卡留在原位可再次裁决。文案精确匹配王工走查修订第 5 条。
        await api.confirmRule(rule.id, "confirmed", confirmer.trim(), {
          option_key: "escalate",
        });
        message.success("已留痕并通知负责人（线下）", 5);
      } else {
        // 三选一：正常确认流，toast 带后端返回的版本短码
        const res = await api.confirmRule(rule.id, "confirmed", confirmer.trim(), {
          option_key: option,
        });
        message.success(`${res.message}（commit ${res.record.commit ?? "无"}）`, 5);
        onDone();
      }
    } catch (e) {
      message.error(`裁决失败：${(e as Error).message}`);
    } finally {
      setLoading(false);
    }
  };

  const nameMissing = !confirmer.trim();
  const options = rule.divergence ?? [];

  return (
    <div>
      {/* 对照区：两口径并列，数字证据是唯一能拿去对账的东西 */}
      <Text type="secondary" style={{ fontSize: 12 }}>
        ⚖ 两口径对照——这不是是非题，先对数再裁决
      </Text>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 4 }}>
        {options.map((opt) => (
          <div
            key={opt.key}
            style={{
              flex: "1 1 240px",
              border: "1px solid #f0f0f0",
              borderRadius: 4,
              padding: 8,
            }}
          >
            <Text strong>{opt.label}</Text>
            <div>
              <Text>{opt.value_evidence}</Text>
            </div>
            <div>
              <Text type="secondary" style={{ fontSize: 12 }}>
                适用场景：{opt.applies_to}
              </Text>
            </div>
          </div>
        ))}
      </div>

      {/* 裁决四选项（RadioGroup），both 推荐且默认预选 */}
      <div style={{ marginTop: 8 }}>
        <Radio.Group
          value={option}
          onChange={(e) => setOption(e.target.value as DecisionOptionKey)}
          style={{ display: "flex", flexDirection: "column", gap: 4 }}
        >
          {VERDICT_OPTIONS.map(({ key, label }) => (
            <Radio key={key} value={key}>
              {label}
              {key === "both" && (
                <Tag color="green" style={{ marginLeft: 8 }}>
                  推荐
                </Tag>
              )}
            </Radio>
          ))}
        </Radio.Group>
      </div>

      <Space wrap style={{ marginTop: 8 }}>
        <Button
          type="primary"
          loading={loading}
          disabled={nameMissing}
          onClick={submit}
        >
          ✓ 提交裁决
        </Button>
      </Space>
      {nameMissing && (
        <div>
          <Text type="warning" style={{ fontSize: 12 }}>
            未填名不能确认——身份是确认的一部分
          </Text>
        </div>
      )}
      <div>
        <Text type="secondary" style={{ fontSize: 12 }}>
          裁决落 git 留痕，确认后可驳回；升级裁决只留痕不改状态，可再次裁决
        </Text>
      </div>
    </div>
  );
}
