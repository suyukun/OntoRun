// 对象详情组件 —— 全属性展示 + 链接导航入口（out/in 分组）
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Button, Card, Descriptions, Space, Tag, Typography, message, Spin } from 'antd';
import { LinkOutlined, ArrowRightOutlined, ArrowLeftOutlined } from '@ant-design/icons';
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
  const { t } = useTranslation();
  const [detail, setDetail] = useState<ObjectDetailData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetchObjectDetail(meta.api_name, pk)
      .then(setDetail)
      .catch((err) => message.error(t('common.loadFailed', { msg: (err as Error).message })))
      .finally(() => setLoading(false));
  }, [meta.api_name, pk, t]);

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '40px auto' }} />;
  if (!detail) return <Card><Title level={5}>{t('common.noData')}</Title></Card>;

  const outLinks = Object.entries(detail.links.out);
  const inLinks = Object.entries(detail.links.in);

  return (
    <Card
      title={t('objects.detailTitle', { title: meta.description })}
      extra={<Button onClick={onBack}>{t('objects.backToList')}</Button>}
    >
      <Descriptions bordered column={{ xs: 1, sm: 2, md: 3 }} size="small">
        {Object.entries(detail.properties).map(([key, val]) => (
          <Descriptions.Item key={key} label={meta.properties[key]?.title || key}>
            {val === null || val === undefined ? <Tag>{t('common.empty')}</Tag> : String(val)}
          </Descriptions.Item>
        ))}
      </Descriptions>

      {/* 出向链接（本对象出发） */}
      {outLinks.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <Title level={5}>
            <ArrowRightOutlined /> {t('objects.outLinks')}
          </Title>
          <Space wrap>
            {outLinks.map(([linkName, count]) => (
              <Button
                key={'out-' + linkName}
                icon={<LinkOutlined />}
                type="dashed"
                onClick={() => onNavigateLink(meta.api_name, pk, linkName)}
              >
                {linkName} ({count})
              </Button>
            ))}
          </Space>
        </div>
      )}

      {/* 入向链接（谁引用了我） */}
      {inLinks.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <Title level={5}>
            <ArrowLeftOutlined /> {t('objects.inLinks')}
          </Title>
          <Space wrap>
            {inLinks.map(([linkName, count]) => (
              <Button
                key={'in-' + linkName}
                icon={<LinkOutlined />}
                type="dashed"
                onClick={() => onNavigateLink(meta.api_name, pk, linkName)}
              >
                {linkName} ({count})
              </Button>
            ))}
          </Space>
        </div>
      )}
    </Card>
  );
}