import { useRef, useState } from 'react';

interface Props {
  busy: boolean;
  ready: boolean;
  onSend: (q: string) => void;
  onStop: () => void;
}

/** 输入区：IME 组合键保护（§3.6）+ 生成中停止按钮（AbortController）。 */
export function ChatInput({ busy, ready, onSend, onStop }: Props) {
  const [value, setValue] = useState('');
  const composingRef = useRef(false);

  const fire = () => {
    const q = value.trim();
    if (!q || busy || !ready) return;
    onSend(q);
    setValue('');
  };

  return (
    <div className="inputrow">
      <input
        value={value}
        placeholder={ready ? '输入问题…' : '业务档案装配中…'}
        disabled={!ready}
        onChange={(e) => setValue(e.target.value)}
        onCompositionStart={() => { composingRef.current = true; }}
        onCompositionEnd={() => { composingRef.current = false; }}
        onKeyDown={(e) => {
          // IME 组合期间 Enter 不发送；isComposing 与 composition 标记双保险
          if (e.key === 'Enter' && !e.nativeEvent.isComposing && !composingRef.current) fire();
        }}
      />
      {busy ? (
        <button className="stopbtn" onClick={onStop}>
          ■ 停止
        </button>
      ) : (
        <button onClick={fire} disabled={!ready || !value.trim()}>
          发送
        </button>
      )}
    </div>
  );
}
