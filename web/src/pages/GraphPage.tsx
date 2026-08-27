// 本体图谱页（builder）：cytoscape 渲染 对象类型×链接类型 图
// 数据源 = GET /api/v1/builder/graph（聚合：内置零售段 + builder 已发布 S3 金控风险行）。
// 不经 /meta/schema —— S1 零售浏览页读 /meta/schema 零影响，图谱页能看到完整本体图。
import { useEffect, useState } from 'react';
import { Alert, Spin } from 'antd';
import { useTranslation } from 'react-i18next';
import SchemaGraph from '../components/SchemaGraph';
import { fetchOntologyGraph } from '../apiBuilder';
import type { MetaSchema } from '../types';

export default function GraphPage() {
  const { t } = useTranslation();
  const [meta, setMeta] = useState<MetaSchema | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchOntologyGraph()
      .then((data) => {
        if (!cancelled) {
          setMeta({ objects: data.objects, links: data.links, actions: [] });
          setLoading(false);
        }
      })
      .catch((err: Error) => {
        if (!cancelled) {
          setError(err.message);
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
        <Spin size="large" tip={t('common.loading')} />
      </div>
    );
  }
  if (error || !meta) {
    return (
      <div style={{ padding: 40 }}>
        <Alert type="error" message={t('common.error')} description={error || t('common.noData')} showIcon />
      </div>
    );
  }
  return <SchemaGraph meta={meta} />;
}
