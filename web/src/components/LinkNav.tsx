// 链接导航组件 —— 展示链接遍历结果
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Button, Card, Table, Tag, message, Spin } from 'antd';
import { RollbackOutlined } from '@ant-design/icons';
import { fetchLinkTraversal } from '../api';
import type { LinkTypeMeta, ObjectItem, ObjectTypeMeta } from '../types';

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
  const { t } = useTranslation();
  const [objects, setObjects] = useState<ObjectItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [direction, setDirection] = useState<'out' | 'in'>('out');

  // 找到链接定义（name 或 inverse_name 均可定位）
  const linkDef = useMemo(
    () => links.find((l) => l.name === linkName || l.inverse_name === linkName),
    [links, linkName],
  );

  const load = useCallback(
    async (dir: string) => {
      setLoading(true);
      try {
        // TD-14 修复：请求名必须与方向匹配——out 用正向名 name、in 用反向名
        // inverse_name（后端按「名 + 方向 + 端点」严格匹配，传错组合即 404）。
        const name = linkDef
          ? dir === 'out'
            ? linkDef.name
            : linkDef.inverse_name
          : linkName;
        const data = await fetchLinkTraversal(sourceType.api_name, sourcePk, name, dir);
        setObjects(data.objects);
      } catch (err) {
        message.error(t('common.loadFailed', { msg: (err as Error).message }));
      } finally {
        setLoading(false);
      }
    },
    [t, sourcePk, linkName, sourceType.api_name, linkDef],
  );

  useEffect(() => { void load(direction); }, [load, linkName, direction]);

  const targetTypeName = linkDef ? (direction === 'out' ? linkDef.target_type : linkDef.source_type) : '';
  const targetType = objectTypes.find((x) => x.name === targetTypeName);

  const columns = targetType
    ? Object.entries(targetType.properties).map(([key, prop]) => ({
        title: prop.title || key,
        dataIndex: ['properties', key],
        key,
        render: (val: unknown) => (val === null || val === undefined ? <Tag>{t('common.empty')}</Tag> : String(val)),
      }))
    : [];

  return (
    <Card
      title={t('objects.linkTitle', { linkName }) + (linkDef ? ' (' + linkDef.description + ')' : '')}
      extra={
        <>
          <Button
            type={direction === 'out' ? 'primary' : 'default'}
            size="small"
            onClick={() => setDirection('out')}
            style={{ marginRight: 8 }}
          >
            {t('objects.forward')}
          </Button>
          <Button
            type={direction === 'in' ? 'primary' : 'default'}
            size="small"
            onClick={() => setDirection('in')}
            style={{ marginRight: 8 }}
          >
            {t('objects.reverse')}
          </Button>
          <Button icon={<RollbackOutlined />} onClick={onBack}>
            {t('common.back')}
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