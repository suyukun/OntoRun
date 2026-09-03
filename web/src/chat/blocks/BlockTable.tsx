// table 块 —— 归集集中度明细（docs/chat-ux-spec-v1.md §5.2）
import { useState, type ReactNode } from 'react';
import { Modal, Table } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { CopyOutlined, FileSearchOutlined, ZoomInOutlined } from '@ant-design/icons';
import { TABLE_ROWS } from '../../proto/fakeData';
import { RISK_COLORS, WARN_TAG_TINTS } from '../../risk/riskTheme';

type Row = (typeof TABLE_ROWS)[number];

/** 状态列淡彩标签（§5.2：安全 green 无底；触达黄 tint；橙色预警橙 tint） */
const LEVEL_STYLE: Record<string, React.CSSProperties> = {
  安全: { color: RISK_COLORS.green },
  触达: { color: RISK_COLORS.yellow, background: WARN_TAG_TINTS.YELLOW.bg, border: `1px solid ${WARN_TAG_TINTS.YELLOW.border}` },
  橙色预警: { color: RISK_COLORS.orange, background: WARN_TAG_TINTS.ORANGE.bg, border: `1px solid ${WARN_TAG_TINTS.ORANGE.border}` },
};

function StatusTag({ level }: { level: string }) {
  const s = LEVEL_STYLE[level];
  if (!s) return <span>{level}</span>;
  return (
    <span style={{ ...s, display: 'inline-block', fontSize: 12, lineHeight: '20px', borderRadius: 4, padding: '0 8px' }}>
      {level}
    </span>
  );
}

function IconBtn({ title, onClick, children }: { title: string; onClick: () => void; children: ReactNode }) {
  return (
    <button className="chat-icon-btn" title={title} onClick={onClick} style={{ marginLeft: 4 }}>
      {children}
    </button>
  );
}

const COLUMNS: ColumnsType<Row> = [
  { title: '机构', dataIndex: 'org' }, // 余量给机构名（§5.2 列宽指引）
  { title: '敞口', dataIndex: 'exposure', width: 120, align: 'right' },
  { title: '占比', dataIndex: 'ratio', width: 110, align: 'right' },
  { title: '参考线', dataIndex: 'ref', width: 160 },
  { title: '状态', dataIndex: 'level', width: 120, render: (v: string) => <StatusTag level={v} /> },
];

function DetailTable() {
  return (
    <Table
      size="small"
      pagination={false}
      dataSource={TABLE_ROWS}
      rowKey="org"
      columns={COLUMNS}
      rowClassName={(r) => (r.level === '橙色预警' ? 'chat-hit-row' : '')}
    />
  );
}

export default function BlockTable({ onEvidence }: { onEvidence: () => void }) {
  const [zoom, setZoom] = useState(false);

  const copyCsv = () => {
    const lines = TABLE_ROWS.map((r) => [r.org, r.exposure, r.ratio, r.ref, r.level].join(','));
    void navigator.clipboard?.writeText(['机构,敞口,占比,参考线,状态', ...lines].join('\n')).catch(() => undefined);
  };

  return (
    <div style={{ background: '#fff', border: `1px solid ${RISK_COLORS.borderSoft}`, borderRadius: 8, padding: 12 }}>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
        <span style={{ fontSize: 13, lineHeight: '20px', fontWeight: 600 }}>归集集中度明细</span>
        <span style={{ flex: 1 }} />
        <IconBtn title="复制 CSV" onClick={copyCsv}>
          <CopyOutlined />
        </IconBtn>
        <IconBtn title="放大" onClick={() => setZoom(true)}>
          <ZoomInOutlined />
        </IconBtn>
        <IconBtn title="查看依据" onClick={onEvidence}>
          <FileSearchOutlined />
        </IconBtn>
      </div>
      <div className="chat-table">
        <DetailTable />
      </div>
      <Modal open={zoom} width={720} title="归集集中度明细" onCancel={() => setZoom(false)} footer={null}>
        <div className="chat-table">
          <DetailTable />
        </div>
      </Modal>
    </div>
  );
}
