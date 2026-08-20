// 动作页（运行时）：/meta/actions 渲染动作详情与参数表单，POST /actions/{name}（X-Actor: api）
import { useTranslation } from 'react-i18next';
import { Alert, Empty, Spin, Typography } from 'antd';
import { useMetaContext } from '../context/MetaContext';
import ActionForm from '../components/ActionForm';

const { Title } = Typography;

export default function ActionsPage() {
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

  return (
    <div>
      <Title level={4}>{t('actions.title')}（{meta.actions.length}）</Title>
      {meta.actions.length === 0 ? (
        <Empty description={t('common.noData')} />
      ) : (
        meta.actions.map((action) => <ActionForm key={action.name} action={action} onDone={() => undefined} />)
      )}
    </div>
  );
}
