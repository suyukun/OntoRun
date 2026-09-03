// 输入区 —— textarea 1-5 行自适应 + Enter/IME/停止/字数（docs/chat-ux-spec-v1.md §7）
import { useRef, useState } from 'react';
import { Input } from 'antd';
import { SendOutlined, StopOutlined } from '@ant-design/icons';
import { RISK_COLORS } from '../risk/riskTheme';

const PLACEHOLDER = '向风险智能体提问，如：为什么归集 10.8% 触发橙色预警？';
const MAX_LEN = 500;

interface Props {
  generating: boolean;
  onSend: (text: string) => void;
  onStop: () => void;
}

export default function ChatComposer({ generating, onSend, onStop }: Props) {
  const [value, setValue] = useState('');
  const wrapRef = useRef<HTMLDivElement>(null);

  const send = () => {
    const text = value.trim();
    if (!text || generating) return;
    onSend(text);
    setValue('');
    // 发送后保持 focus（§7.2）
    wrapRef.current?.querySelector('textarea')?.focus();
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key !== 'Enter' || e.shiftKey) return;
    if (e.nativeEvent.isComposing) return; // IME 组合中 Enter 不发送（§7.2）
    e.preventDefault();
    send(); // 生成中 send 内部直接忽略
  };

  const canSend = value.trim().length > 0 && !generating;

  return (
    <div style={{ padding: '0 24px 16px', flexShrink: 0 }}>
      <div ref={wrapRef} className="chat-composer" style={{ maxWidth: 760, margin: '0 auto' }}>
        <Input.TextArea
          value={value}
          onChange={(e) => setValue(e.target.value.slice(0, MAX_LEN))}
          onKeyDown={onKeyDown}
          placeholder={PLACEHOLDER}
          variant="borderless"
          autoSize={{ minRows: 1, maxRows: 5 }}
          maxLength={MAX_LEN}
          style={{ fontSize: 15, lineHeight: '24px', padding: 0, resize: 'none', color: RISK_COLORS.text }}
        />
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 8, marginTop: 8 }}>
          {value.length > 400 && (
            <span style={{ fontSize: 12, lineHeight: '20px', color: RISK_COLORS.textFaint, fontVariantNumeric: 'tabular-nums' }}>
              {value.length}/{MAX_LEN}
            </span>
          )}
          {generating ? (
            <button
              className="chat-stop-btn"
              onClick={onStop}
              title="停止生成"
              style={{
                width: 32,
                height: 32,
                borderRadius: 8,
                background: '#fff',
                border: `1px solid ${RISK_COLORS.border}`,
                color: RISK_COLORS.text,
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <StopOutlined style={{ fontSize: 14 }} />
            </button>
          ) : (
            <button
              onClick={send}
              disabled={!canSend}
              title="发送（Enter 发送 · Shift+Enter 换行）"
              style={{
                width: 32,
                height: 32,
                borderRadius: 8,
                border: 0,
                cursor: canSend ? 'pointer' : 'default',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: canSend ? RISK_COLORS.accent : RISK_COLORS.panelAlt,
                color: canSend ? '#fff' : RISK_COLORS.textFaint,
              }}
            >
              <SendOutlined style={{ fontSize: 16 }} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
