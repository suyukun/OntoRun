// 变更历史页：git log 人话化时间线（时间 / 作者 / 改了什么 / commit 短码）。
import { useEffect, useState } from "react";
import { Button, Card, Empty, Space, Spin, Tag, Timeline, Typography } from "antd";
import { api, type HistoryPayload } from "../api";

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

function typeOf(subject: string) {
  return subject.split(":", 1)[0].split("(", 1)[0].trim();
}

function fmtTime(iso: string) {
  return iso.replace("T", " ").slice(0, 16);
}

export default function HistoryPage() {
  const [data, setData] = useState<HistoryPayload | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setError(null);
    api
      .history(50)
      .then(setData)
      .catch((e) => setError((e as Error).message));
  };
  useEffect(load, []);

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
              最近 {data.count} 次（每一次口径确认都会留痕在此）
            </Text>
            <Button size="small" onClick={load}>
              刷新
            </Button>
          </Space>
        }
      >
        <Paragraph type="secondary" style={{ marginBottom: 16 }}>
          本体管理台的所有改动（口径确认、规则调整）都走 git commit——这里是
          人话版账本：谁、什么时候、改了什么。
        </Paragraph>
        {data.commits.length === 0 ? (
          <Empty description="还没有任何提交" />
        ) : (
          <Timeline
            items={data.commits.map((c) => ({
              color: TYPE_COLOR[typeOf(c.subject)] ?? "gray",
              children: (
                <Space direction="vertical" size={0} style={{ paddingBottom: 4 }}>
                  <Space size={8} wrap>
                    <Tag>{c.author}</Tag>
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
            }))}
          />
        )}
      </Card>
    </div>
  );
}
