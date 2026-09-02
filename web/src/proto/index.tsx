import { Component, type ReactNode } from 'react';
import { Button, Card, Result } from 'antd';
import { Routes, Route, Navigate } from 'react-router-dom';
import AntdXPage from './AntdXPage';
import LobePage from './LobePage';

class Boundary extends Component<{ children: ReactNode }, { error: Error | null }> {
  state = { error: null as Error | null };
  static getDerivedStateFromError(error: Error) {
    return { error };
  }
  render() {
    if (this.state.error)
      return (
        <Result
          status="error"
          title="原型渲染失败"
          subTitle={this.state.error.message}
          extra={<Button href="/proto">返回选择页</Button>}
        />
      );
    return this.props.children;
  }
}

function Chooser() {
  return (
    <div style={{ minHeight: '100vh', background: '#f5f7fa', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ display: 'flex', gap: 16 }}>
        <Card hoverable style={{ width: 300 }} title="A · @ant-design/x" extra={<Button size="small" href="/proto/antd-x">打开</Button>}>
          AntD 官方 AI 组件（Bubble/Sender/Conversations/ThoughtChain），与现有 antd 6 主题同源。
        </Card>
        <Card hoverable style={{ width: 300 }} title="B · @lobehub/ui" extra={<Button size="small" href="/proto/lobe-ui">打开</Button>}>
          LobeChat 打磨的聊天 UI（Markdown 排版是卖点），同为 antd 6 + React 19 原生。
        </Card>
      </div>
    </div>
  );
}

export default function ProtoRoutes() {
  // 注意：外层 App 已有 BrowserRouter，这里绝不能再包一层（Router 嵌套 = 整树白屏）
  return (
    <>
      <Routes>
        <Route path="/proto" element={<Chooser />} />
        <Route path="/proto/antd-x" element={<Boundary><AntdXPage /></Boundary>} />
        <Route path="/proto/lobe-ui" element={<Boundary><LobePage /></Boundary>} />
        <Route path="/proto/*" element={<Navigate to="/proto" replace />} />
      </Routes>
    </>
  );
}
