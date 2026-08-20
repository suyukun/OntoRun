// 本体驱动 UI 主壳 —— MetaProvider 加载 /meta/schema，react-router 路由 + AntD Layout
import { useTranslation } from 'react-i18next';
import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from 'react-router-dom';
import { Layout, Menu, Typography, theme } from 'antd';
import {
  ApartmentOutlined,
  AppstoreOutlined,
  DatabaseOutlined,
  LinkOutlined,
  PartitionOutlined,
  RobotOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import { MetaProvider, useMetaContext } from './context/MetaContext';
import LanguageSwitcher from './components/LanguageSwitcher';
import BrowsePage from './pages/BrowsePage';
import ActionsPage from './pages/ActionsPage';
import ChatPanel from './components/ChatPanel';
import ObjectTypesPage from './pages/builder/ObjectTypesPage';
import LinkTypesPage from './pages/builder/LinkTypesPage';
import PipelineCanvas from './components/PipelineCanvas';
import GraphPage from './pages/GraphPage';

const { Sider, Header, Content } = Layout;
const { Title, Text } = Typography;

interface MenuGroup {
  key: string;
  type: 'group';
  label: string;
  children: { key: string; icon: React.ReactNode; label: string }[];
}

function Shell() {
  const { t } = useTranslation();
  const { meta } = useMetaContext();
  const navigate = useNavigate();
  const location = useLocation();
  const { token } = theme.useToken();

  const menuGroups: MenuGroup[] = [
    {
      key: 'runtime',
      type: 'group',
      label: t('nav.runtime'),
      children: [
        { key: '/', icon: <DatabaseOutlined />, label: t('nav.browse') },
        {
          key: '/actions',
          icon: <ThunderboltOutlined />,
          label: t('nav.actions') + (meta ? ' (' + meta.actions.length + ')' : ''),
        },
        { key: '/chat', icon: <RobotOutlined />, label: t('nav.chat') },
      ],
    },
    {
      key: 'builder',
      type: 'group',
      label: t('nav.builder'),
      children: [
        { key: '/builder/object-types', icon: <AppstoreOutlined />, label: t('nav.objectTypes') },
        { key: '/builder/link-types', icon: <LinkOutlined />, label: t('nav.linkTypes') },
        { key: '/builder/pipelines', icon: <PartitionOutlined />, label: t('nav.pipelines') },
        { key: '/builder/graph', icon: <ApartmentOutlined />, label: t('nav.graph') },
      ],
    },
  ];

  const flatKeys = menuGroups.flatMap((g) => g.children.map((c) => c.key));
  const selectedKey = flatKeys.includes(location.pathname) ? location.pathname : '/';

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
          <Text type="secondary" style={{ fontSize: 12 }}>{t('app.tagline')}</Text>
        </div>
        <Menu
          mode="inline"
          style={{ borderRight: 0 }}
          selectedKeys={[selectedKey]}
          items={menuGroups}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            background: token.colorBgContainer,
            borderBottom: '1px solid ' + token.colorBorderSecondary,
            display: 'flex',
            justifyContent: 'flex-end',
            alignItems: 'center',
            padding: '0 24px',
          }}
        >
          <LanguageSwitcher />
        </Header>
        <Content style={{ padding: 24, background: token.colorBgLayout }}>
          <Routes>
            <Route path="/" element={<BrowsePage />} />
            <Route path="/actions" element={<ActionsPage />} />
            <Route path="/chat" element={<ChatPanel />} />
            <Route path="/builder/object-types" element={<ObjectTypesPage />} />
            <Route path="/builder/link-types" element={<LinkTypesPage />} />
            <Route path="/builder/pipelines" element={<PipelineCanvas />} />
            <Route path="/builder/graph" element={<GraphPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
}

export default function App() {
  return (
    <MetaProvider>
      <BrowserRouter>
        <Shell />
      </BrowserRouter>
    </MetaProvider>
  );
}
