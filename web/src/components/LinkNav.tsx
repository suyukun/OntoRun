// 链接导航组件 —— 展示链接遍历结果
import { useEffect, useState } from 'react';
import { Button, Card, Table, Tag, Typography, message, Spin } from 'antd';
import { RollbackOutlined } from '@ant-design/icons';
import { fetchLinkTraversal } from '../api';
import type { LinkTypeMeta, ObjectItem, ObjectTypeMeta } from '../types';

const { Title } = Typography;

interface Props {
  sourceType: ObjectTypeMeta;
  sourcePk: string;
  linkName: string;
  links: LinkTypeMeta[];
  objectTypes: ObjectTypeMeta[];
  onSelectObject: (type: string, pk: string) => void;
  onBack: () => void;
}

export default function LinkNav({
  sourceType,
  sourcePk,
  linkName,
  links,
  objectTypes,
  onSelectObject,
  onBack,
}: Props) {
  const [objects, setObjects] = useState<ObjectItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [direction, setDirection] = useState<'out' | 'in'>('out');

  // 找到链接定义
  const linkDef = links.find(
    (l) => l.name === linkName || l.inverse_name === linkName,
  );

  const load = async (dir: string) => {
    setLoading(true);
    try {
      const data = await fetchLinkTraversal(
        sourceType.api_name,
        sourcePk,
        linkName,
        dir,
      );
      setObjects(data.objects);
    } catch (err) {
      message.error('链接遍历失败: ' + (err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(direction); }, [linkName, direction]);

  const targetTypeName = linkDef
    ? direction === 'out'
      ? linkDef.target_type
      : linkDef.source_type
    : '';
  const targetType = objectTypes.find((t) => t.name === targetTypeName);

  const columns = targetType
    ? Object.entries(targetType.properties).map(([key, prop]) => ({
        title: prop.title || key,
        dataIndex: ['properties', key],
        key,
        render: (val: unknown) => (val === null || val === undefined ? <Tag>空</Tag> : String(val)),
      }))
    : [];

  return (
    <Card
      title={
        '链接: ' + linkName +
        (linkDef ? ' (' + linkDef.description + ')' : '')
      }
      extra={
        <>
          <Button
            type={direction === 'out' ? 'primary' : 'default'}
            size="small"
            onClick={() => setDirection('out')}
            style={{ marginRight: 8 }}
          >
            正向
          </Button>
          <Button
            type={direction === 'in' ? 'primary' : 'default'}
            size="small"
            onClick={() => setDirection('in')}
            style={{ marginRight: 8 }}
          >
            反向
          </Button>
          <Button icon={<RollbackOutlined />} onClick={onBack}>
            返回
          </Button>
        </>
      }
    >
      {loading ? (
        <Spin style={{ display: 'block', margin: '20px auto' }} />
      ) : (
        <Table
          columns={columns}
          dataSource={objects}
          rowKey={(r) => r.pk}
          size="small"
          pagination={false}
          onRow={(record) => ({
            onClick: () => {
              if (targetType) onSelectObject(targetType.api_name, record.pk);
            },
            style: { cursor: 'pointer' },
          })}
        />
      )}
    </Card>
  );
}
