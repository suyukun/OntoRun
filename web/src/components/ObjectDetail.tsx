// 对象详情组件 —— 全属性展示 + 链接导航入口
import { useEffect, useState } from 'react';
import { Button, Card, Descriptions, Space, Tag, Typography, message, Spin } from 'antd';
import { LinkOutlined } from '@ant-design/icons';
import { fetchObjectDetail } from '../api';
import type { ObjectDetailData, ObjectTypeMeta } from '../types';

const { Title } = Typography;

interface Props {
  meta: ObjectTypeMeta;
  pk: string;
  onNavigateLink: (type: string, pk: string, linkName: string) => void;
  onBack: () => void;
}

export default function ObjectDetail({ meta, pk, onNavigateLink, onBack }: Props) {
  const [detail, setDetail] = useState<ObjectDetailData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetchObjectDetail(meta.api_name, pk)
      .then(setDetail)
      .catch((err) => message.error('加载详情失败: ' + (err as Error).message))
      .finally(() => setLoading(false));
  }, [meta.api_name, pk]);

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '40px auto' }} />;
  if (!detail) return <Card><Title level={5}>无数据</Title></Card>;

  return (
    <Card
      title={meta.description + ' 详情'}
      extra={<Button onClick={onBack}>返回列表</Button>}
    >
      <Descriptions bordered column={{ xs: 1, sm: 2, md: 3 }} size="small">
        {Object.entries(detail.properties).map(([key, val]) => (
          <Descriptions.Item
            key={key}
            label={meta.properties[key]?.title || key}
          >
            {val === null || val === undefined ? <Tag>空</Tag> : String(val)}
          </Descriptions.Item>
        ))}
      </Descriptions>

      {detail.links && Object.keys(detail.links).length > 0 && (
        <>
          <Title level={5} style={{ marginTop: 16 }}>关联链接</Title>
          <Space wrap>
            {Object.entries(detail.links).map(([linkName, count]) => (
              <Button
                key={linkName}
                icon={<LinkOutlined />}
                type="dashed"
                onClick={() => onNavigateLink(meta.api_name, pk, linkName)}
              >
                {linkName} ({count})
              </Button>
            ))}
          </Space>
        </>
      )}
    </Card>
  );
}
