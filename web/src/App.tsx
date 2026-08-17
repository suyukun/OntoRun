// 本体驱动 UI 主壳 —— 元数据加载 → 导航 → 组件渲染
import { useState } from 'react';
import { Alert, Layout, Menu, Spin, Typography, theme } from 'antd';
import { AppstoreOutlined, ThunderboltOutlined, RobotOutlined } from '@ant-design/icons';
import { useMeta } from './hooks/useMeta';
import ObjectList from './components/ObjectList';
import ObjectDetail from './components/ObjectDetail';
import LinkNav from './components/LinkNav';
import ActionForm from './components/ActionForm';
import ChatPanel from './components/ChatPanel';
import type { ActionMeta, ObjectTypeMeta } from './types';

const { Sider, Content } = Layout;
const { Title, Text, Paragraph } = Typography;

type View =
  | { kind: 'object-list'; type: ObjectTypeMeta }
  | { kind: 'object-detail'; type: ObjectTypeMeta; pk: string }
  | { kind: 'link-nav'; sourceType: ObjectTypeMeta; sourcePk: string; linkName: string }
  | { kind: 'actions' }
  | { kind: 'chat' };

export default function App() {
  const { meta, loading, error } = useMeta();
  const { token } = theme.useToken();
  const [view, setView] = useState<View | null>(null);
  const [selectedType, setSelectedType] = useState<string | null>(null);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Spin size="large" tip="加载本体元数据..." />
      </div>
    );
  }

  if (error || !meta) {
    return (
      <div style={{ padding: 40 }}>
        <Alert type="error" message="无法加载本体元数据" description={error || '未知错误'} />
      </div>
    );
  }

  const handleSelectObject = (type: string, pk: string) => {
    const objType = meta.objects.find((o) => o.api_name === type || o.name === type);
    if (objType) setView({ kind: 'object-detail', type: objType, pk });
  };

  const handleNavigateLink = (type: string, pk: string, linkName: string) => {
    const objType = meta.objects.find((o) => o.api_name === type || o.name === type);
    if (objType) setView({ kind: 'link-nav', sourceType: objType, sourcePk: pk, linkName });
  };

  const renderView = () => {
    if (!view) {
      return (
        <div style={{ textAlign: 'center', padding: 80 }}>
          <Title level={3}>OntoRun 语义接口</Title>
          <Paragraph type="secondary">
            零售供应链最小语义接口闭环 —— 本体驱动 UI
          </Paragraph>
          <Paragraph>
            左侧选择对象类型浏览数据，或选择动作执行操作，或与 AI 助手对话。
          </Paragraph>
        </div>
      );
    }

    switch (view.kind) {
      case 'object-list':
        return (
          <ObjectList
            meta={view.type}
            onSelectObject={handleSelectObject}
          />
        );
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
              const objType = meta.objects.find(
                (o) => o.name === view.sourceType.name,
              );
              if (objType)
                setView({
                  kind: 'object-detail',
                  type: objType,
                  pk: view.sourcePk,
                });
            }}
          />
        );
      case 'actions':
        return (
          <div>
            <Title level={4}>动作列表（{meta.actions.length}）</Title>
            {meta.actions.map((action: ActionMeta) => (
              <div key={action.name} style={{ marginBottom: 16 }}>
                <ActionForm action={action} onDone={() => {
                  if (selectedType) {
                    const objType = meta.objects.find((o) => o.api_name === selectedType || o.name === selectedType);
                    if (objType) setView({ kind: 'object-list', type: objType });
                  }
                }} />
              </div>
            ))}
          </div>
        );
      case 'chat':
        return <ChatPanel />;
      default:
        return null;
    }
  };

  const objectMenuItems = meta.objects.map((obj) => ({
    key: obj.api_name,
    icon: <AppstoreOutlined />,
    label: obj.description + ' (' + obj.name + ')',
  }));

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        width={240}
        style={{
          background: token.colorBgContainer,
          borderRight: '1px solid ' + token.colorBorderSecondary,
        }}
      >
        <div style={{ padding: '16px', borderBottom: '1px solid ' + token.colorBorderSecondary }}>
          <Title level={5} style={{ margin: 0 }}>OntoRun</Title>
          <Text type="secondary" style={{ fontSize: 12 }}>
            语义接口 · 本体驱动
          </Text>
        </div>
        <Menu
          mode="inline"
          selectedKeys={selectedType ? [selectedType] : []}
          style={{ borderRight: 0 }}
          items={[
            {
              key: 'objects',
              icon: <AppstoreOutlined />,
              label: '对象类型',
              children: objectMenuItems,
            },
            {
              key: 'actions',
              icon: <ThunderboltOutlined />,
              label: '动作 (' + meta.actions.length + ')',
            },
            {
              key: 'chat',
              icon: <RobotOutlined />,
              label: 'AI 助手',
            },
          ]}
          onClick={({ key }) => {
            if (key === 'actions') {
              setView({ kind: 'actions' });
              setSelectedType(null);
            } else if (key === 'chat') {
              setView({ kind: 'chat' });
              setSelectedType(null);
            } else {
              const objType = meta.objects.find((o) => o.api_name === key);
              if (objType) {
                setSelectedType(key);
                setView({ kind: 'object-list', type: objType });
              }
            }
          }}
        />
      </Sider>
      <Layout>
        <Content style={{ padding: 24, background: token.colorBgLayout }}>
          {renderView()}
        </Content>
      </Layout>
    </Layout>
  );
}
