// 口径规则卡 v2（三问自足确认卡）：① 是什么数（人话标题首行，禁裸 ID 打头）
// ② 怎么算的（试算证据行，端点失败灰条降级、不阻塞确认）③ 确认后影响谁。
// 技术细节（registry 表达式原文 / 出处脚本 / 历史确认）默认折叠；行动区常驻
// 「确认后可驳回，全程留痕」小字。RulesPage 与对象详情页共用；readOnly 只展示。
import { useEffect, useState } from "react";
import { api, type CaliberRule, type TrialResult } from "../api";
import { Button, Card, Collapse, Modal, Space, Tag, Typography, message } from "antd";
import DivergenceCard from "./DivergenceCard";

const { Text, Paragraph } = Typography;

// 默认试算月 = 当前月（YYYY-MM）。MVP 只出固定试算月，「换个月份」留后续。
function currentMonth(): string {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
}

// 2026-08 -> 2026 年 8 月（非标准格式原样显示，不造数据）。
function formatMonth(ym: string): string {
  const m = /^(\d{4})-(\d{2})$/.exec(ym);
  return m ? `${m[1]} 年 ${Number(m[2])} 月` : ym;
}

export default function RuleCard({
  rule,
  confirmer,
  onDone,
  readOnly = false,
  expression,
}: {
  rule: CaliberRule;
  confirmer: string;
  onDone: () => void;
  readOnly?: boolean;
  /** registry 表达式原文（可选，调用方从对象详情等现状数据传入；规则 payload 不带） */
  expression?: string;
}) {
  const [loading, setLoading] = useState<string | null>(null);
  const [rejecting, setRejecting] = useState(false);
  const [trial, setTrial] = useState<TrialResult | null>(null);
  const [trialFailed, setTrialFailed] = useState(false);

  // 试算证据行：端点并行开发中（可能 404/503），失败必须优雅降级且绝不阻塞确认
  // 主流程（trial_failure_nonblocking）。
  useEffect(() => {
    let alive = true;
    fetch(`/api/trial/${rule.id}?month=${currentMonth()}`)
      .then((res) =>
        res.ok ? res.json() : Promise.reject(new Error(String(res.status)))
      )
      .then((data: TrialResult) => {
        if (alive) setTrial(data);
      })
      .catch(() => {
        if (alive) setTrialFailed(true);
      });
    return () => {
      alive = false;
    };
  }, [rule.id]);

  const submit = async (verdict: "confirmed" | "rejected") => {
    if (!confirmer.trim()) {
      message.warning("请先在页首填写确认人（确认要落身份，进 git 历史）");
      return;
    }
    setLoading(verdict);
    try {
      const res = await api.confirmRule(rule.id, verdict, confirmer.trim());
      message.success(`${res.message}（commit ${res.record.commit ?? "无"}）`, 5);
      setRejecting(false);
      onDone();
    } catch (e) {
      message.error(`确认失败：${(e as Error).message}`);
    } finally {
      setLoading(null);
    }
  };

  const last = rule.last_record;
  const nameMissing = !confirmer.trim();

  const techDetails = (
    <Space direction="vertical" size={4} style={{ width: "100%" }}>
      {expression ? (
        <Text code style={{ fontSize: 12, wordBreak: "break-all" }}>
          {expression}
        </Text>
      ) : (
        <Text type="secondary" style={{ fontSize: 12 }}>
          registry 表达式原文：见对应度量/维度的对象详情
        </Text>
      )}
      <Text type="secondary" style={{ fontSize: 12 }}>
        📎 出处：
      </Text>
      <Text code style={{ fontSize: 12, wordBreak: "break-all" }}>
        {rule.source_script}
      </Text>
      <Text type="secondary" style={{ fontSize: 12 }}>
        上次确认：
        {last
          ? `${last.confirmer} ${last.time.replace("T", " ").slice(0, 16)}（${last.verdict === "confirmed" ? "确认" : "驳回"}，commit ${last.commit ?? "-"}）`
          : "无"}
      </Text>
    </Space>
  );

  return (
    <Card
      title={
        <Space size={8}>
          {rule.status === "confirmed" ? (
            <Tag color="green">已确认</Tag>
          ) : (
            <Tag color="orange">待确认</Tag>
          )}
          {/* 问① 是什么数：人话标题首行，规则号只作右侧元信息（qc4_plain_first_line） */}
          <Text strong>{rule.description}</Text>
        </Space>
      }
      extra={
        <Text type="secondary" code style={{ fontSize: 12 }}>
          {rule.id}
        </Text>
      }
      style={{
        borderColor: rule.status === "confirmed" ? "#b7eb8f" : "#ffd591",
        height: "100%",
      }}
    >
      {/* 问② 怎么算的 + 试算证据（数字是唯一能拿去对账的东西） */}
      <Text type="secondary" style={{ fontSize: 12 }}>
        ② 怎么算的 + 证据
      </Text>
      <div style={{ margin: "4px 0 8px" }}>
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
        ) : trial ? (
          <Text>
            📊 试算：按此口径跑 {formatMonth(trial.month)} = {trial.value}
            {trial.unit}
          </Text>
        ) : (
          <Text type="secondary" style={{ fontSize: 12 }}>
            试算加载中…
          </Text>
        )}
      </div>

      {/* 问③ 确认后影响谁：关联表/对象（表名只在此处出现，定位用） */}
      <Text type="secondary" style={{ fontSize: 12 }}>
        ③ 确认后影响谁
      </Text>
      <div style={{ margin: "4px 0 8px" }}>
        {rule.related_tables.length > 0 ? (
          rule.related_tables.map((t) => <Tag key={t}>{t}</Tag>)
        ) : (
          <Text type="secondary" style={{ fontSize: 12 }}>
            暂无登记关联表
          </Text>
        )}
      </div>

      {/* 技术细节默认折叠（qc3_default_collapsed）：表达式原文可展开（expression_expandable） */}
      <Collapse
        ghost
        items={[{ key: "tech", label: "技术细节", children: techDetails }]}
      />

      {readOnly ? (
        <Text type="secondary" style={{ fontSize: 12 }}>
          去口径确认页处理 →
        </Text>
      ) : rule.divergence && rule.divergence.length > 0 && rule.status === "unverified" ? (
        // R8 分歧裁决（T203）：有双口径对照且未决时，行动区换成裁决卡而非是非题按钮；
        // 已确认（三选一落定）后回到普通卡走「可驳回」流，escalate 后仍待确认可再次裁决
        <DivergenceCard rule={rule} confirmer={confirmer} onDone={onDone} />
      ) : (
        <>
          <Space wrap style={{ marginTop: 8 }}>
            <Button
              type="primary"
              disabled={nameMissing}
              loading={loading === "confirmed"}
              onClick={() => submit("confirmed")}
            >
              ✓ 对，就这样算
            </Button>
            <Button danger disabled={nameMissing} onClick={() => setRejecting(true)}>
              ✗ 不对，有问题
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
              确认后可驳回，全程留痕
            </Text>
          </div>
        </>
      )}

      {!readOnly && (
        <Modal
          title={`驳回 ${rule.id}？`}
          open={rejecting}
          onCancel={() => setRejecting(false)}
          onOk={() => submit("rejected")}
          confirmLoading={loading === "rejected"}
          okText={`驳回（以 ${confirmer.trim() || "未填名"} 记录，回到待确认）`}
          cancelText="取消"
        >
          <Paragraph type="secondary">
            驳回会回到待确认队列并留痕（新 commit）。确认人取页首填写：
            <Text strong>{confirmer.trim() || "（未填）"}</Text>
          </Paragraph>
        </Modal>
      )}
    </Card>
  );
}
