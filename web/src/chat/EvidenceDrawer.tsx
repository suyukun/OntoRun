// 证据链抽屉 —— 四区：数据来源 / 规则 / 口径 / 审计轨迹（docs/chat-ux-spec-v1.md §6）
// 批 3：live 模式渲染 /agent/risk/chat 真实证据载荷（结论/basis 表/命中规则/分母/明细行引用）
import { useEffect, type ReactNode } from 'react';
import { Button } from 'antd';
import { CloseOutlined, CopyOutlined } from '@ant-design/icons';
import { EVIDENCE_DETAIL } from './scriptData';
import type { EvidenceBlock } from './chatApi';
import { RISK_COLORS } from '../risk/riskTheme';
import { chatFontMono } from './chatTokens';

function SectionTitle({ children }: { children: ReactNode }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
      <span style={{ width: 3, height: 12, borderRadius: 1.5, background: RISK_COLORS.accent }} />
      <span style={{ fontSize: 13, lineHeight: '20px', fontWeight: 600 }}>{children}</span>
    </div>
  );
}

interface Props {
  open: boolean;
  auditId: string;
  onClose: () => void;
  /** live：真实证据载荷（批 3）；缺省走剧本演示数据 */
  liveBlocks?: EvidenceBlock[];
}

function CopyRow({ text, suffix }: { text: string; suffix?: string }) {
  return (
    <div className="chat-evi-row" style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '4px 0' }}>
      <code style={{ fontFamily: chatFontMono, fontSize: 13, background: RISK_COLORS.panelAlt, borderRadius: 4, padding: '1px 5px' }}>
        {text}
      </code>
      {suffix && <span style={{ fontSize: 12, lineHeight: '20px', color: RISK_COLORS.textFaint }}>{suffix}</span>}
      <span style={{ flex: 1 }} />
      <button
        className="chat-icon-btn chat-more"
        title="复制"
        onClick={() => void navigator.clipboard?.writeText(text).catch(() => undefined)}
      >
        <CopyOutlined />
      </button>
    </div>
  );
}

export default function EvidenceDrawer({ open, auditId, onClose, liveBlocks }: Props) {
  // ESC 关闭（§6.3）
  useEffect(() => {
    if (!open) return;
    const h = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', h);
    return () => window.removeEventListener('keydown', h);
  }, [open, onClose]);

  const isLive = !!liveBlocks?.length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', background: '#fff' }}>
      <div
        style={{
          height: 48,
          flexShrink: 0,
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          padding: '0 16px',
          borderBottom: `1px solid ${RISK_COLORS.borderSoft}`,
        }}
      >
        <span style={{ fontSize: 14, lineHeight: '22px', fontWeight: 600 }}>证据链</span>
        <span
          style={{
            fontFamily: chatFontMono,
            fontSize: 12,
            lineHeight: '20px',
            background: RISK_COLORS.panelAlt,
            borderRadius: 4,
            padding: '1px 8px',
            color: RISK_COLORS.textDim,
          }}
        >
          {auditId}
        </span>
        <span style={{ flex: 1 }} />
        <button className="chat-icon-btn" title="关闭" onClick={onClose}>
          <CloseOutlined />
        </button>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: 16, display: 'flex', flexDirection: 'column', gap: 24 }}>
        {isLive ? (
          <>
            <section>
              <SectionTitle>结论（真实载荷）</SectionTitle>
              {liveBlocks!
                .filter((b) => b.conclusion)
                .slice(0, 3)
                .map((b, i) => (
                  <div key={i} style={{ fontSize: 13, lineHeight: '22px', marginBottom: 8 }}>
                    {b.conclusion}
                  </div>
                ))}
            </section>

            <section>
              <SectionTitle>数据来源（basis 表）</SectionTitle>
              {[...new Set(liveBlocks!.flatMap((b) => b.basis_tables ?? []))].map((t) => (
                <CopyRow key={t} text={t} suffix="实查" />
              ))}
            </section>

            <section>
              <SectionTitle>命中规则</SectionTitle>
              {liveBlocks!
                .flatMap((b) => b.rules_hits ?? [])
                .map((h, i) => (
                  <div key={i} style={{ marginBottom: 12 }}>
                    <div style={{ fontSize: 13, lineHeight: '20px', fontWeight: 600 }}>
                      {[h.rule, h.name].filter(Boolean).join(' · ') || '规则命中'}
                    </div>
                    <pre
                      style={{
                        margin: '6px 0',
                        padding: 8,
                        background: RISK_COLORS.panelAlt,
                        borderRadius: 6,
                        fontFamily: chatFontMono,
                        fontSize: 12,
                        lineHeight: '20px',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-all',
                        color: RISK_COLORS.textDim,
                      }}
                    >
                      {[h.lines, h.clause].filter(Boolean).join('\n') || '—'}
                    </pre>
                  </div>
                ))}
              {liveBlocks!.flatMap((b) => b.rules_hits ?? []).length === 0 && (
                <div style={{ fontSize: 12.5, lineHeight: '20px', color: RISK_COLORS.textFaint }}>本次实查无规则命中行</div>
              )}
            </section>

            <section>
              <SectionTitle>口径（分母）</SectionTitle>
              {liveBlocks!
                .map((b) => b.denominator)
                .filter((d): d is NonNullable<typeof d> => !!d)
                .slice(0, 1)
                .map((d, i) => (
                  <div key={i} style={{ display: 'flex', padding: '3px 0', fontSize: 13, lineHeight: '22px' }}>
                    <span style={{ width: 88, flexShrink: 0, fontSize: 12, lineHeight: '22px', color: RISK_COLORS.textFaint }}>
                      {d.name ?? '分母'}
                    </span>
                    <span>
                      {d.value_yi != null ? `${d.value_yi} 亿` : '—'}
                      {d.source ? `（${d.source}）` : ''}
                    </span>
                  </div>
                ))}
            </section>

            <section>
              <SectionTitle>明细行引用</SectionTitle>
              {liveBlocks!
                .flatMap((b) => b.detail_rows ?? [])
                .map((r) => r.row_ref)
                .filter((r): r is string => typeof r === 'string')
                .slice(0, 6)
                .map((ref) => (
                  <CopyRow key={ref} text={ref} />
                ))}
            </section>
          </>
        ) : (
          <>
            <section>
              <SectionTitle>数据来源（basis 表）</SectionTitle>
              {EVIDENCE_DETAIL.tables.map((t) => (
                <div key={t.name} className="chat-evi-row" style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '4px 0' }}>
                  <code style={{ fontFamily: chatFontMono, fontSize: 13, background: RISK_COLORS.panelAlt, borderRadius: 4, padding: '1px 5px' }}>
                    {t.name}
                  </code>
                  <span style={{ fontSize: 12, lineHeight: '20px', color: RISK_COLORS.textFaint }}>
                    {t.rows} · {t.snapshot}
                  </span>
                  <span style={{ flex: 1 }} />
                  <button
                    className="chat-icon-btn chat-more"
                    title="复制表名"
                    onClick={() => void navigator.clipboard?.writeText(t.name).catch(() => undefined)}
                  >
                    <CopyOutlined />
                  </button>
                </div>
              ))}
            </section>

            <section>
              <SectionTitle>规则</SectionTitle>
              {EVIDENCE_DETAIL.rules.map((r) => (
                <div key={r.name} style={{ marginBottom: 12 }}>
                  <div style={{ fontSize: 13, lineHeight: '20px', fontWeight: 600 }}>{r.name}</div>
                  <pre
                    style={{
                      margin: '6px 0',
                      padding: 8,
                      background: RISK_COLORS.panelAlt,
                      borderRadius: 6,
                      fontFamily: chatFontMono,
                      fontSize: 12,
                      lineHeight: '20px',
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-all',
                      color: RISK_COLORS.textDim,
                    }}
                  >
                    {r.expr}
                  </pre>
                  <div style={{ fontSize: 12, lineHeight: '20px', color: RISK_COLORS.textFaint }}>{r.source}</div>
                </div>
              ))}
            </section>

            <section>
              <SectionTitle>口径</SectionTitle>
              {EVIDENCE_DETAIL.caliber.map((c) => (
                <div key={c.key} style={{ display: 'flex', padding: '3px 0', fontSize: 13, lineHeight: '22px' }}>
                  <span style={{ width: 88, flexShrink: 0, fontSize: 12, lineHeight: '22px', color: RISK_COLORS.textFaint }}>{c.key}</span>
                  <span>{c.value}</span>
                </div>
              ))}
            </section>

            <section>
              <SectionTitle>审计轨迹</SectionTitle>
              <div
                style={{
                  borderLeft: `1px solid ${RISK_COLORS.borderSoft}`,
                  marginLeft: 3,
                  paddingLeft: 16,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 12,
                }}
              >
                {EVIDENCE_DETAIL.timeline.map((t) => (
                  <div key={t.time} style={{ position: 'relative', fontSize: 13, lineHeight: '20px' }}>
                    <span
                      style={{
                        position: 'absolute',
                        left: -19.5,
                        top: 7,
                        width: 6,
                        height: 6,
                        borderRadius: 3,
                        background: RISK_COLORS.accent,
                      }}
                    />
                    <span style={{ fontFamily: chatFontMono, fontSize: 12, color: RISK_COLORS.textFaint, marginRight: 8 }}>{t.time}</span>
                    <span>{t.action}</span>
                  </div>
                ))}
              </div>
            </section>
          </>
        )}
      </div>

      <div
        style={{
          height: 40,
          flexShrink: 0,
          borderTop: `1px solid ${RISK_COLORS.borderSoft}`,
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          padding: '0 16px',
        }}
      >
        <span style={{ flex: 1, fontSize: 12, lineHeight: '20px', color: RISK_COLORS.textFaint }}>
          {isLive ? '内容来自 ap_anping 六库实查载荷，禁 mock' : EVIDENCE_DETAIL.footer}
        </span>
        <Button type="text" size="small" disabled title="演示版未开放">
          导出审计包
        </Button>
      </div>
    </div>
  );
}
