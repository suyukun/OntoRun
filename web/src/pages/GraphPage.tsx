// 本体图谱页（builder）：cytoscape 渲染 对象类型×链接类型 图（/meta/schema 驱动）
import { Alert, Spin } from 'antd';
import { useTranslation } from 'react-i18next';
import { useMetaContext } from '../context/MetaContext';
import SchemaGraph from '../components/SchemaGraph';

export default function GraphPage() {
  const { meta, loading, error } = useMetaContext();
  const { t } = useTranslation();

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
