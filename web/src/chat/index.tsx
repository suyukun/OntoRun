// /chat 路由入口 —— 仿 /proto 挂法（外层 App 已有 BrowserRouter，绝不能再包一层）
import { ConfigProvider } from 'antd';
import { Navigate, Route, Routes } from 'react-router-dom';
import { riskLightTheme } from '../risk/riskTheme';
import ChatShell from './ChatShell';
import './chat.css';

export default function ChatRoutes() {
  return (
    <ConfigProvider theme={riskLightTheme}>
      <Routes>
        <Route path="/chat" element={<ChatShell />} />
        <Route path="/chat/*" element={<Navigate to="/chat" replace />} />
      </Routes>
    </ConfigProvider>
  );
}
