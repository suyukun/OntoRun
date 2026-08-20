// 数据浏览（运行时）：对象类型侧栏 → 对象列表 → 详情（属性+链接 out/in）→ 链接遍历
// 完全由 /meta/schema 驱动，不硬编码业务字段。
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Alert, Layout, Menu, Spin, Typography } from 'antd';
import { useMetaContext } from '../context/MetaContext';
import ObjectList from '../components/ObjectList';
import ObjectDetail from '../components/ObjectDetail';
import LinkNav from '../components/LinkNav';
import type { ObjectTypeMeta } from '../types';

const { Sider, Content } = Layout;
const { Title, Paragraph } = Typography;

type View =
  | { kind: 'object-list'; type: ObjectTypeMeta }
  | { kind: 'object-detail'; type: ObjectTypeMeta; pk: string }
  | { kind: 'link-nav'; sourceType: ObjectTypeMeta; sourcePk: string; linkName: string };

export default function BrowsePage() {
  const { meta, loading, error } = useMetaContext();
  const { t } = useTranslation();
  const [view, setView] = useState<View | null>(null);
  const [selectedKey, setSelectedKey] = useState<string | null>(null);

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

  const findType = (type: string) => meta.objects.find((o) => o.api_name === type || o.name === type);

  const handleSelectObject = (type: string, pk: string) => {
    const objType = findType(type);
    if (objType) setView({ kind: 'object-detail', type: objType, pk });
  };

  const handleNavigateLink = (type: string, pk: string, linkName: string) => {
    const objType = findType(type);
    if (objType) setView({ kind: 'link-nav', sourceType: objType, sourcePk: pk, linkName });
  };

  const renderView = () => {
    if (!view) {
      return (
        <div style={{ textAlign: 'center', padding: 80 }}>
          <Title level={3}>OntoRun · {t('nav.browse')}</Title>
          <Paragraph type="secondary">{t('app.tagline')}</Paragraph>
          <Paragraph>{t('graph.desc')}</Paragraph>
        </div>
      );
    }
    switch (view.kind) {
      case 'object-list':
        return <ObjectList meta={view.type} onSelectObject={handleSelectObject} />;
      case 'object-detail':
        return (
          <ObjectDetail
            meta={view.type}
            pk={view.pk}
            onNavigateLink={handleNavigateLink}
            onBack={() => setView({ kind: 'object-list', type: view.type })}
          />
        );
      case 'link-nav':
        return (
          <LinkNav
            sourceType={view.sourceType}
            sourcePk={view.sourcePk}
            linkName={view.linkName}
            links={meta.links}
            objectTypes={meta.objects}
            onSelectObject={handleSelectObject}
            onBack={() => {
              const objType = findType(view.sourceType.name);
              if (objType) setView({ kind: 'object-detail', type: objType, pk: view.sourcePk });
            }}
          />
        );
      default:
        return null;
    }
  };

  return (
    <Layout style={{ minHeight: '100%' }}>
      <Sider width={220} theme="light" style={{ borderRight: '1px solid #f0f0f0' }}>
        <div style={{ padding: '12px 16px' }}>
          <Typography.Text strong>{t('nav.objectTypes')}</Typography.Text>
        </div>
        <Menu
          mode="inline"
          style={{ borderRight: 0 }}
          selectedKeys={selectedKey ? [selectedKey] : []}
          onClick={({ key }) => {
            const objType = findType(key);
            if (objType) {
              setSelectedKey(key);
              setView({ kind: 'object-list', type: objType });
            }
          }}
          items={meta.objects.map((obj) => ({
            key: obj.api_name,
            label: obj.description + ' (' + obj.name + ')',
          }))}
        />
      </Sider>
      <Content style={{ padding: 16 }}>{renderView()}</Content>
    </Layout>
  );
}
