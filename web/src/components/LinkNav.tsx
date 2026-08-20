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
  // 当前对象在该链接的哪一侧（决定请求名与另一端类型）：
  // source 侧：out=name / in=inverse_name；target 侧：out=inverse_name / in=name。
  const isSource = linkDef ? linkDef.source_type === sourceType.name : null;

  const load = useCallback(
    async (dir: string) => {
      setLoading(true);
      try {
        // TD-14 修复：请求名必须与「方向 + 当前对象所在侧」匹配，否则后端 404
        // （后端按「名 + 方向 + 端点」严格匹配：out=name+source / inverse+target，
        //   in=inverse+source / name+target）。
        let name = linkName;
        if (linkDef && isSource !== null) {
          const forward = isSource ? linkDef.name : linkDef.inverse_name;
          const backward = isSource ? linkDef.inverse_name : linkDef.name;
          name = dir === 'out' ? forward : backward;
        }
        const data = await fetchLinkTraversal(sourceType.api_name, sourcePk, name, dir);
        setObjects(data.objects);
      } catch (err) {
        message.error(t('common.loadFailed', { msg: (err as Error).message }));
      } finally {
        setLoading(false);
      }
    },
    [t, sourcePk, linkName, sourceType.api_name, linkDef, isSource, sourceType.name],
  );

  useEffect(() => { void load(direction); }, [load, linkName, direction]);

  // 另一端对象类型：与方向无关，只取决于当前对象在链接的哪一侧
  const targetTypeName =
    linkDef && isSource !== null ? (isSource ? linkDef.target_type : linkDef.source_type) : '';
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