// report 块 —— 索引卡 + 预览 Modal + 下载 MD（docs/chat-ux-spec-v1.md §5.4）
import { useState } from 'react';
import { Button, Modal } from 'antd';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { FileTextOutlined, LoadingOutlined } from '@ant-design/icons';
import { REPORT } from '../scriptData';
import { RISK_COLORS, WARN_TAG_TINTS } from '../../risk/riskTheme';
import { chatFontMono } from '../chatTokens';

export default function BlockReport({ phase }: { phase: 'skeleton' | 'done' }) {
  const [preview, setPreview] = useState(false);

  const downloadMd = () => {
    const blob = new Blob([REPORT.md], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = REPORT.fileName;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div
      style={{
        background: '#fff',
        border: `1px solid ${RISK_COLORS.borderSoft}`,
        borderLeft: `3px solid ${RISK_COLORS.accent}`, // 左缘 3px accent 竖条（§5.4）
        borderRadius: 8,
        padding: 12,
      }}
    >
      {phase === 'skeleton' ? (
        <>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
            <LoadingOutlined style={{ color: RISK_COLORS.accent, fontSize: 16 }} />
            <span style={{ fontSize: 14, lineHeight: '22px', fontWeight: 600 }}>{REPORT.title}</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            <div className="chat-skel" style={{ width: '90%' }} />
            <div className="chat-skel" style={{ width: '76%' }} />
            <div className="chat-skel" style={{ width: '60%' }} />
          </div>
        </>
      ) : (
        <>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <FileTextOutlined style={{ color: RISK_COLORS.accent, fontSize: 16 }} />
            <span style={{ fontSize: 14, lineHeight: '22px', fontWeight: 600 }}>{REPORT.title}</span>
            <span
              style={{
                fontSize: 12,
                lineHeight: '20px',
                color: RISK_COLORS.yellow,
                background: WARN_TAG_TINTS.YELLOW.bg,
                border: `1px solid ${WARN_TAG_TINTS.YELLOW.border}`,
                borderRadius: 4,
                padding: '0 8px',
              }}
            >
              {REPORT.tag}
            </span>
          </div>
          <div className="chat-clamp-2" style={{ marginTop: 6, fontSize: 13, lineHeight: '22px', color: RISK_COLORS.textDim }}>
            {REPORT.summary}
          </div>
          <div style={{ marginTop: 10, display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 12, color: RISK_COLORS.textFaint, fontVariantNumeric: 'tabular-nums' }}>{REPORT.meta}</span>
            <span style={{ flex: 1 }} />
            <Button size="small" onClick={() => setPreview(true)}>
              预览
            </Button>
            <Button size="small" type="text" onClick={downloadMd}>
              下载 MD
            </Button>
          </div>
        </>
      )}

      <Modal
        open={preview}
        width={720}
        title={REPORT.title}
        onCancel={() => setPreview(false)}
        footer={null}
        styles={{ body: { maxHeight: '80vh', overflowY: 'auto', paddingTop: 12 } }}
      >
        <div style={{ fontSize: 12, color: RISK_COLORS.textFaint, marginBottom: 12 }}>安平金控 · 风险处置建议（模拟）</div>
        <div className="chat-md chat-report-md">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{REPORT.md}</ReactMarkdown>
        </div>
        <div
          style={{
            marginTop: 16,
            paddingTop: 10,
            borderTop: `1px solid ${RISK_COLORS.borderSoft}`,
            fontSize: 12.5,
            color: RISK_COLORS.textDim,
          }}
        >
          审计{' '}
          <code style={{ fontFamily: chatFontMono, fontSize: 12.5, background: RISK_COLORS.panelAlt, borderRadius: 4, padding: '1px 5px' }}>
            #A-1024
          </code>{' '}
          · 处置动作经人工批准后写回源系统
        </div>
      </Modal>
    </div>
  );
}
