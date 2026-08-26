// 本体驱动 UI 主壳 —— MetaProvider 加载 /meta/schema，react-router 路由 + AntD Layout
// S3 M4 扩展：风险预警演示（深色金融风控壳，/ + /risk/*），S1 零售演示（浅色壳）保持不破坏。
import { useTranslation } from 'react-i18next';
import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from 'react-router-dom';
import { ConfigProvider, Layout, Menu, Typography, theme } from 'antd';
import {
  ApartmentOutlined,
  AppstoreOutlined,
  DatabaseOutlined,
  LinkOutlined,
  PartitionOutlined,
  RobotOutlined,
  SafetyCertificateOutlined,
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
import RiskLandingPage from './risk/RiskLandingPage';
import RiskChatPanel from './risk/RiskChatPanel';
import RiskBrowsePage from './risk/RiskBrowsePage';
import { RISK_COLORS, riskDarkTheme } from './risk/riskTheme';
import './risk/risk.css';

const { Sider, Header, Content } = Layout;
const { Title, Text } = Typography;

interface MenuGroup {
  key: string;
  type: 'group';
  label: string;
  children: { key: string; icon: React.ReactNode; label: string }[];
}

// ======================================================================
// S1 零售演示壳（浅色，原状保留；仅 Browse 路由从 / 移到 /browse）
// ======================================================================
function S1Shell() {
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
        { key: '/browse', icon: <DatabaseOutlined />, label: t('nav.browse') },
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
  const selectedKey = flatKeys.includes(location.pathname) ? location.pathname : '/browse';

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
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '0 24px',
          }}
        >
          <button
            onClick={() => navigate('/')}
            style={{ background: 'transparent', border: '1px solid ' + token.colorBorderSecondary, borderRadius: 6, padding: '6px 14px', cursor: 'pointer', color: token.colorTextSecondary, fontSize: 13 }}
          >
            ← 返回风险预警演示
          </button>
          <LanguageSwitcher />
        </Header>
        <Content style={{ padding: 24, background: token.colorBgLayout }}>
          <Routes>
            <Route path="/browse" element={<BrowsePage />} />
            <Route path="/actions" element={<ActionsPage />} />
            <Route path="/chat" element={<ChatPanel />} />
            <Route path="/builder/object-types" element={<ObjectTypesPage />} />
            <Route path="/builder/link-types" element={<LinkTypesPage />} />
            <Route path="/builder/pipelines" element={<PipelineCanvas />} />
            <Route path="/builder/graph" element={<GraphPage />} />
            <Route path="*" element={<Navigate to="/browse" replace />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
}

// ======================================================================
// 风险预警演示壳（深色金融风控：/ + /risk/*）
// ======================================================================
function RiskShell() {
  const navigate = useNavigate();
  const location = useLocation();

  const menuGroups: MenuGroup[] = [
    {
      key: 'risk-demo',
      type: 'group',
      label: '风险预警演示',
      children: [
        { key: '/', icon: <SafetyCertificateOutlined />, label: '价值总览' },
        { key: '/risk/chat', icon: <RobotOutlined />, label: '风险对话 · 双签' },
        { key: '/risk/browse', icon: <DatabaseOutlined />, label: '风险数据浏览' },
      ],
    },
    {
      key: 'other',
      type: 'group',
      label: '零售演示（S1）',
      children: [{ key: '/browse', icon: <AppstoreOutlined />, label: '零售供应链演示' }],
    },
  ];

  const flatKeys = menuGroups.flatMap((g) => g.children.map((c) => c.key));
  const selectedKey = flatKeys.includes(location.pathname) ? location.pathname : '/';

  return (
    <ConfigProvider theme={{ ...riskDarkTheme, algorithm: theme.darkAlgorithm }}>
      <Layout style={{ minHeight: '100vh', background: RISK_COLORS.ink }}>
        <Sider
          width={232}
          theme="dark"
          style={{ background: RISK_COLORS.surface, borderRight: '1px solid ' + RISK_COLORS.border }}
        >
          <div style={{ padding: '18px 16px', borderBottom: '1px solid ' + RISK_COLORS.border }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span
                style={{
                  width: 26, height: 26, borderRadius: 6, display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                  background: RISK_COLORS.accent, color: RISK_COLORS.accentText, fontWeight: 800, fontSize: 14,
                }}
              >
                安
              </span>
              <div>
                <div style={{ color: RISK_COLORS.text, fontWeight: 700, fontSize: 14, lineHeight: 1.2 }}>安平金控</div>
                <div style={{ color: RISK_COLORS.textFaint, fontSize: 11 }}>风险管理部 · 风险预警系统</div>
              </div>
            </div>
          </div>
          <Menu
            className="risk-menu"
            mode="inline"
            theme="dark"
            style={{ background: 'transparent', borderRight: 0, paddingTop: 8 }}
            selectedKeys={[selectedKey]}
            items={menuGroups}
            onClick={({ key }) => navigate(key)}
          />
        </Sider>
        <Layout>
          <Header
            style={{
              background: RISK_COLORS.surface,
              borderBottom: '1px solid ' + RISK_COLORS.border,
              display: 'flex',
              justifyContent: 'flex-end',
              alignItems: 'center',
              padding: '0 24px',
              gap: 16,
            }}
          >
            <span style={{ color: RISK_COLORS.textFaint, fontSize: 12 }}>
              模拟数据 · 脱敏处理 · 本体驱动演示环境
            </span>
            <LanguageSwitcher />
          </Header>
          <Content style={{ background: 'transparent', padding: 0 }}>
            <Routes>
              <Route path="/" element={<RiskLandingPage />} />
              <Route path="/risk/chat" element={<RiskChatPanel />} />
              <Route path="/risk/browse" element={<RiskBrowsePage />} />
              <Route path="/risk/*" element={<Navigate to="/risk/chat" replace />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </ConfigProvider>
  );
}

function AppRoutes() {
  const location = useLocation();
  const isRisk = location.pathname === '/' || location.pathname.startsWith('/risk');
  return isRisk ? <RiskShell /> : <S1Shell />;
}

export default function App() {
  return (
    <MetaProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </MetaProvider>
  );
}
