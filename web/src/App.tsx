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
import RiskHomePage from './risk/RiskHomePage';
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

  // 信息架构收敛（口径包§六/§七）：Agent 对话 = 唯一一级入口（路由 / 直达）；
  // 数据浏览 / 图谱 / DES / 零售撤出门面菜单，仅作为 Sider 底部「更多入口」次级链接保留。
  const menuGroups: MenuGroup[] = [
    {
      key: 'risk-demo',
      type: 'group',
      label: t('nav.riskDemo'),
      children: [{ key: '/', icon: <RobotOutlined />, label: t('nav.riskDialogue') }],
    },
  ];

  const secondaryLinks: { to: string; icon: React.ReactNode; label: string }[] = [
    { to: '/risk/browse', icon: <DatabaseOutlined />, label: t('nav.riskWorkbench') },
    { to: '/risk/overview', icon: <SafetyCertificateOutlined />, label: t('nav.valueOverview') },
    { to: '/des', icon: <ClusterOutlined />, label: t('nav.desEnterprise') },
    { to: '/browse', icon: <AppstoreOutlined />, label: t('nav.retailChain') },
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
          {/* 更多入口（已撤出门面菜单，仅保留路由可达） */}
          <div style={{ padding: '14px 16px 4px', borderTop: '1px solid ' + RISK_COLORS.borderSoft, marginTop: 12 }}>
            <div style={{ fontSize: 11, color: RISK_COLORS.textFaint, letterSpacing: '0.1em', marginBottom: 8 }}>
              {t('nav.moreEntries')}
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              {secondaryLinks.map((l) => (
                <button
                  key={l.to}
                  onClick={() => navigate(l.to)}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 8, textAlign: 'left',
                    background: 'transparent', border: 0, cursor: 'pointer', padding: '5px 6px',
                    color: RISK_COLORS.textDim, fontSize: 12.5, borderRadius: 6,
                  }}
                >
                  <span style={{ color: RISK_COLORS.textFaint, fontSize: 13, width: 14 }}>{l.icon}</span>
                  {l.label}
                </button>
              ))}
            </div>
          </div>
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
              {/* 唯一一级入口：Agent 对话 + 七幕剧本演示 */}
              <Route path="/" element={<RiskHomePage />} />
              {/* 撤出门面的次级路由（页脚/Sider 更多入口可达，不再进菜单） */}
              <Route path="/risk/browse" element={<RiskBrowsePage />} />
              <Route path="/risk/overview" element={<RiskLandingPage />} />
              <Route path="/des" element={<EnterpriseOverviewPage />} />
              {/* 旧链接兜底：/risk/chat 与任意 /risk/* 一律进入对话主页 */}
              <Route path="/risk/chat" element={<Navigate to="/" replace />} />
              <Route path="/risk/*" element={<Navigate to="/" replace />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </ConfigProvider>
  );
}

import ProtoRoutes from './proto';
import ChatRoutes from './chat';

function AppRoutes() {
  const location = useLocation();
  if (location.pathname.startsWith('/proto')) return <ProtoRoutes />;
  if (location.pathname.startsWith('/chat')) return <ChatRoutes />;
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