// text 块 —— Markdown 富文本（docs/chat-ux-spec-v1.md §5.1/§8.1）
// 打字机机制 = @ant-design/x TypingContent（useTyping rAF 引擎）；本组件只做 Markdown 渲染与规格光标。
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
// 深层导入：TypingContent 未从包根导出（x 2.9.0），派单指令点名使用该内置组件
import { TypingContent } from '@ant-design/x/es/bubble/TypingContent';
import { RISK_COLORS } from '../../risk/riskTheme';

export default function BlockText({ md, streaming }: { md: string; streaming: boolean }) {
  // revealed 仅在流式分支消费；流式结束直接渲染全量 md（渲染分支派生，无 effect setState）
  const [revealed, setRevealed] = useState('');
  const [typingDone, setTypingDone] = useState(false);

  if (!streaming) {
    return (
      <div className="chat-md">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{md}</ReactMarkdown>
      </div>
    );
  }

  return (
    <div className="chat-md chat-streaming">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{revealed}</ReactMarkdown>
      {!typingDone && <span className="chat-cursor" style={{ background: RISK_COLORS.accent }} />}
      {/* 隐藏驱动：TypingContent 负责逐字进度（视觉按规格用 .chat-md + .chat-cursor 呈现） */}
      <div style={{ display: 'none' }} aria-hidden>
        <TypingContent
          prefixCls="chat-typing"
          streaming={false}
          content={md}
          typing={{ effect: 'typing', step: 2, interval: 24 }}
          onTyping={(partial) => setRevealed(partial)}
          onTypingComplete={() => {
            setRevealed(md);
            setTypingDone(true);
          }}
        />
      </div>
    </div>
  );
}
