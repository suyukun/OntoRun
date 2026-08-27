// 本体驱动 UI 主壳 —— MetaProvider 加载 /meta/schema，react-router 路由 + AntD Layout
// S3 风险预警演示：浅色专业金融风（方向 A），/ 与 /risk/* 全浅色；对话并入数据工作台双栏；
// S1 零售演示（浅色壳）保持不破坏。
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
  ClusterOutlined,
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
import RiskBrowsePage from './risk/RiskBrowsePage';
import EnterpriseOverviewPage from './pages/des/EnterpriseOverviewPage';
import { RISK_COLORS, riskLightTheme } from './risk/riskTheme';
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
// 风险预警演示壳（浅色金融风：/ 与 /risk/*）；主题单一来源 = riskLightTheme
// ======================================================================
function RiskShell() {
  const navigate = useNavigate();
  const location = useLocation();
  const { t } = useTranslation();

  const menuGroups: MenuGroup[] = [
    {
      key: 'risk-demo',
      type: 'group',
      label: t('nav.riskDemo'),
      children: [
        { key: '/', icon: <SafetyCertificateOutlined />, label: t('nav.valueOverview') },
        // 「风险对话·双签」并入工作台入口（工作台右栏即对话面板）
        { key: '/risk/browse', icon: <DatabaseOutlined />, label: t('nav.riskWorkbench') },
        { key: '/des', icon: <ClusterOutlined />, label: t('nav.desEnterprise') },
      ],
    },
    {
      key: 'other',
      type: 'group',
      label: t('nav.retailDemo'),
      children: [{ key: '/browse', icon: <AppstoreOutlined />, label: t('nav.retailChain') }],
    },
  ];

  const flatKeys = menuGroups.flatMap((g) => g.children.map((c) => c.key));
  const selectedKey = flatKeys.includes(location.pathname) ? location.pathname : '/';

  return (
    <ConfigProvider theme={riskLightTheme}>
      <Layout style={{ minHeight: '100vh', background: RISK_COLORS.ink }}>
        <Sider
          width={232}
          style={{ background: RISK_COLORS.surface, borderRight: '1px solid ' + RISK_COLORS.border }}
        >
          <div style={{ padding: '18px 16px', borderBottom: '1px solid ' + RISK_COLORS.border }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span
                style={{
                  width: 26, height: 26, borderRadius: 6, display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                  background: RISK_COLORS.accent, color: '#ffffff', fontWeight: 600, fontSize: 14,
                }}
              >
                安
              </span>
              <div>
                <div style={{ color: RISK_COLORS.text, fontWeight: 600, fontSize: 14, lineHeight: 1.2 }}>安平金控</div>
                <div style={{ color: RISK_COLORS.textFaint, fontSize: 11 }}>风险管理部 · 风险预警系统</div>
              </div>
            </div>
          </div>
          <Menu
            mode="inline"
            style={{ background: 'transparent', borderRight: 0, paddingTop: 8 }}
            selectedKeys={[selectedKey]}
            items={menuGroups}
            onClick={({ key }) => navigate(key)}
          />
        </Sider>
        <Layout>
          <Header
            style={{
              height: 64,
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
              {/* 数据工作台：左数据浏览 + 右风险对话·双签（原 /risk/chat 已并入） */}
              <Route path="/risk/browse" element={<RiskBrowsePage />} />
              <Route path="/des" element={<EnterpriseOverviewPage />} />
              {/* 旧链接兜底：/risk/chat 与任意 /risk/* 一律进入工作台 */}
              <Route path="/risk/chat" element={<Navigate to="/risk/browse" replace />} />
              <Route path="/risk/*" element={<Navigate to="/risk/browse" replace />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </ConfigProvider>
  );
}

function AppRoutes() {
  const location = useLocation();
  const isRisk =
    location.pathname === '/' ||
    location.pathname.startsWith('/risk') ||
    location.pathname.startsWith('/des');
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
