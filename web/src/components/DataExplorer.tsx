// 数据浏览组件（DataExplorer）—— 从 RiskBrowsePage 抽出的无自持主题可复用组件。
// 能力保持：对象侧栏（业务域分组）→ 列表 → 详情（属性 + 链接 out/in）→ 链接遍历，全程 schema 驱动。
// 数据源：物化快照（web/public/risk-demo/risk-snapshot.json，与对话同源）。不持有 ConfigProvider/页面底色，
// 由父级（RiskShell / WorkbenchPage）统一提供浅色主题；布局填满父容器，侧栏与主区各自独立滚动。
import { useMemo, useState } from 'react';
import { Button, Input, Table, Tag, Typography } from 'antd';
import { ArrowRightOutlined, DatabaseOutlined, RollbackOutlined, SearchOutlined } from '@ant-design/icons';
import '../risk/risk.css';
import { RISK_COLORS as C, WARN_LEVEL_META } from '../risk/riskTheme';
import { DOMAIN_GROUPS, LIST_FIELDS, STATUS_COLORS } from './dataExplorerConfig';
import { dataObjectTypes, formatRiskValue, traversalFor, useRiskSnapshot } from '../risk/riskData';
import type { RiskItem, RiskObjectMeta, RiskSnapshot } from '../risk/riskData';

const { Title, Text } = Typography;


type View =
  | { kind: 'list'; type: RiskObjectMeta }
  | { kind: 'detail'; type: RiskObjectMeta; pk: string }
  | { kind: 'links'; type: RiskObjectMeta; pk: string; displayLink: string; targetType: string; items: RiskItem[] };

export default function DataExplorer() {
  const { data, loading, error } = useRiskSnapshot();
  const [view, setView] = useState<View | null>(null);
  const [selectedKey, setSelectedKey] = useState<string | null>(null);
  const [search, setSearch] = useState('');

  const objectTypes = useMemo(() => (data ? dataObjectTypes(data.meta, data.totals) : []), [data]);
  const findType = (api: string) => objectTypes.find((o) => o.api_name === api);

  const showList = (api: string) => {
    const t = findType(api);
    if (t) {
      setSelectedKey(api);
      setView({ kind: 'list', type: t });
    }
  };

  return (
    <div style={{ flex: 1, minWidth: 0, display: 'flex', minHeight: 0 }}>
      {/* 对象侧栏（按业务域分组；独立滚动） */}
      <aside style={{ width: 232, flex: '0 0 auto', overflowY: 'auto', borderRight: '1px solid ' + C.border, background: C.surface, padding: '16px 10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '0 8px 14px', fontSize: 13.5, fontWeight: 600 }}>
          <DatabaseOutlined style={{ color: C.accent }} /> 业务对象
        </div>
        {DOMAIN_GROUPS.map((g) => {
          const objects = g.objects.map((api) => findType(api)).filter((x): x is RiskObjectMeta => !!x);
          if (objects.length === 0) return null;
          return (
            <div key={g.key} style={{ marginBottom: 10 }}>
              <div style={{ fontSize: 11, color: C.textFaint, letterSpacing: '0.08em', padding: '4px 8px' }}>{g.label}</div>
              {objects.map((o) => (
                <button
                  key={o.api_name}
                  onClick={() => showList(o.api_name)}
                  style={{
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', textAlign: 'left', cursor: 'pointer',
                    padding: '8px 10px', borderRadius: 6, marginBottom: 2, fontSize: 13, color: C.text,
                    background: selectedKey === o.api_name ? C.accent + '14' : 'transparent',
                    border: '1px solid ' + (selectedKey === o.api_name ? C.accent + '66' : 'transparent'),
                  }}
                >
                  <span>{shortName(o.description)}</span>
                  <span className="risk-num" style={{ color: C.textFaint, fontSize: 11.5 }}>
                    {data ? formatCount(data.totals[o.api_name]) : '…'}
                  </span>
                </button>
              ))}
            </div>
          );
        })}
        {error && (
          <div style={{ padding: 10, fontSize: 12, color: C.red }}>快照加载失败：{error}</div>
        )}
      </aside>

      {/* 主区（独立滚动） */}
      <main style={{ flex: 1, minWidth: 0, overflowY: 'auto', padding: 20 }}>
        {renderView()}
      </main>
    </div>
  );

  function renderView() {
    if (!data) {
      return (
        <div style={{ textAlign: 'center', padding: 80, color: C.textFaint }}>
          {loading ? '正在加载演示数据快照…' : '数据快照加载失败：' + error}
        </div>
      );
    }
    if (!view) {
      // 默认进入集团客户（演示主线起点）
      const api = 'group_customer';
      const t = findType(api);
      if (t) return <ListPane key={api} snapshot={data} type={t} search={search} setSearch={setSearch} onOpenDetail={(pk) => setView({ kind: 'detail', type: t, pk })} />;
      return null;
    }
    switch (view.kind) {
      case 'list':
        return (
          <ListPane
            key={view.type.api_name + search}
            snapshot={data}
            type={view.type}
            search={search}
            setSearch={setSearch}
            onOpenDetail={(pk) => setView({ kind: 'detail', type: view.type, pk })}
          />
        );
      case 'detail':
        return (
          <DetailPane
            snapshot={data}
            type={view.type}
            pk={view.pk}
            onBack={() => setView({ kind: 'list', type: view.type })}
            onOpenLinks={(displayLink, targetType, items) => setView({ kind: 'links', type: view.type, pk: view.pk, displayLink, targetType, items })}
          />
        );
      case 'links':
        return (
          <LinksPane
            snapshot={data}
            type={view.type}
            pk={view.pk}
            displayLink={view.displayLink}
            targetType={view.targetType}
            items={view.items}
            onBack={() => setView({ kind: 'detail', type: view.type, pk: view.pk })}
            onOpenDetail={(api, pk) => {
              const t = findType(api);
              if (t) setView({ kind: 'detail', type: t, pk });
            }}
          />
        );
      default:
        return null;
    }
  }
}

function shortName(description: string): string {
  return description.replace(/（.*/, '');
}
function formatCount(n: number): string {
  return n >= 10000 ? (n / 10000).toFixed(n % 10000 === 0 ? 0 : 1) + '万' : n.toLocaleString('zh-CN');
}

// ---- 列表 ----
function ListPane({
  snapshot, type, search, setSearch, onOpenDetail,
}: {
  snapshot: RiskSnapshot;
  type: RiskObjectMeta;
  search: string;
  setSearch: (s: string) => void;
  onOpenDetail: (pk: string) => void;
}) {
  const all = useMemo(() => snapshot.items[type.api_name] ?? [], [snapshot, type.api_name]);
  const filtered = useMemo(() => {
    if (!search.trim()) return all;
    const q = search.trim().toLowerCase();
    return all.filter((it) => Object.values(it.properties).some((v) => String(v ?? '').toLowerCase().includes(q)));
  }, [all, search]);
  const fields = LIST_FIELDS[type.api_name] ?? Object.keys(type.properties).slice(0, 5);
  const columns = [
    { title: type.title_field === type.pk_field ? '标识' : type.properties[type.pk_field]?.title ?? type.pk_field, dataIndex: 'pk', key: 'pk', fixed: 'left' as const, width: 190,
      render: (pk: string) => <span className="risk-num" style={{ color: C.accent }}>{pk}</span> },
    ...fields.filter((f) => f !== type.pk_field && f !== type.title_field).map((f) => ({
      title: type.properties[f]?.title ?? f,
      dataIndex: ['properties', f] as string[],
      key: f,
      render: (v: unknown) => renderCell(type, f, v),
    })),
  ];
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14, flexWrap: 'wrap', gap: 10 }}>
        <div>
          <Title level={4} style={{ margin: 0, letterSpacing: '-0.01em', fontWeight: 600 }}>{shortName(type.description)}</Title>
          <Text style={{ color: C.textFaint, fontSize: 12.5 }}>
            共 <span className="risk-num" style={{ color: C.accent }}>{snapshot.totals[type.api_name]}</span> 条 · 演示展示样本 {all.length} 条（同一数据源）
          </Text>
        </div>
        <Input
          allowClear
          prefix={<SearchOutlined style={{ color: C.textFaint }} />}
          placeholder={'搜索（如 中科智造 / WS-2026…）'}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ width: 240 }}
        />
      </div>
      <TableBox>
        <Table<RiskItem>
          columns={columns}
          dataSource={filtered}
          rowKey={(r) => r.pk}
          size="small"
          pagination={{ pageSize: 10, size: 'small', showTotal: (t) => '共 ' + t + ' 条' }}
          scroll={{ x: 980 }}
          onRow={(r) => ({ onClick: () => onOpenDetail(r.pk), style: { cursor: 'pointer' } })}
          locale={{ emptyText: <span style={{ color: C.textFaint }}>无匹配记录</span> }}
          style={{ background: 'transparent' }}
          components={{ header: { cell: headerCell } }}
        />
      </TableBox>
    </div>
  );
}

function headerCell(props: React.PropsWithChildren<{ [k: string]: unknown }>) {
  return (
    <th {...props} style={{ background: C.surface, color: C.textDim, fontWeight: 600, borderBottom: '1px solid ' + C.border }} />
  );
}

function renderCell(type: RiskObjectMeta, field: string, v: unknown) {
  if (field === 'warn_level') {
    const meta = WARN_LEVEL_META[String(v ?? '')];
    return meta ? <Tag style={{ color: meta.color, background: meta.bg, borderColor: meta.border }}>{meta.label}</Tag> : <span>{String(v ?? '')}</span>;
  }
  if (field === 'signal_status' || field === 'disposal_status' || field === 'current_status' || field === 'approve_order_status' || field === 'approve_task_status' || field === 'approve_result') {
    const c = STATUS_COLORS[String(v ?? '')];
    return c ? <Tag style={{ color: c, borderColor: c, background: '#ffffff' }}>{String(v ?? '')}</Tag> : <span>{String(v ?? '')}</span>;
  }
  if (typeof v === 'number') {
    return <span className="risk-num" style={{ color: C.text }}>{formatRiskValue(v)}</span>;
  }
  return <span style={{ color: C.textDim }}>{formatRiskValue(v)}</span>;
}

// ---- 详情 ----
function DetailPane({
  snapshot, type, pk, onBack, onOpenLinks,
}: {
  snapshot: RiskSnapshot;
  type: RiskObjectMeta;
  pk: string;
  onBack: () => void;
  onOpenLinks: (displayLink: string, targetType: string, items: RiskItem[]) => void;
}) {
  const item = snapshot.items[type.api_name]?.find((i) => i.pk === pk);
  if (!item) return <div style={{ color: C.textFaint }}>记录不存在</div>;
  const out = traversalFor(snapshot, type.api_name, pk, 'out');
  const inn = traversalFor(snapshot, type.api_name, pk, 'in');
  const metrics = type.api_name === 'group_customer' ? snapshot.group_metrics[pk] : undefined;

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 14, flexWrap: 'wrap' }}>
        <Button size="small" icon={<RollbackOutlined />} onClick={onBack}>返回列表</Button>
        <Title level={4} style={{ margin: 0, letterSpacing: '-0.01em', fontWeight: 600 }}>{shortName(type.description)}</Title>
        <span className="risk-num" style={{ color: C.accent, fontSize: 13 }}>{pk}</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.3fr 1fr', gap: 16, alignItems: 'start' }}>
        <div>
          <div style={{ ...panel(), padding: 16, marginBottom: 16 }}>
            <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 10, color: C.textDim }}>属性</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 8 }}>
              {Object.entries(type.properties).map(([f, p]) => {
                const v = item.properties[f];
                return (
                  <div key={f} style={{ border: '1px solid ' + C.borderSoft, borderRadius: 6, padding: '7px 10px', background: C.panelAlt }}>
                    <div style={{ fontSize: 11, color: C.textFaint, marginBottom: 3 }}>{p.title}</div>
                    <div style={{ fontSize: 13, wordBreak: 'break-all' }}>{renderCell(type, f, v)}</div>
                  </div>
                );
              })}
            </div>
          </div>
          {metrics && metrics.length > 0 && (
            <div style={{ ...panel(), padding: 16 }}>
              <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 10, color: C.textDim }}>集团风险指标（真实聚合，来自维度指标库）</div>
              <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                {metrics.map((m) => (
                  <div key={m.index_name} style={{ border: '1px solid ' + C.borderSoft, borderRadius: 6, padding: '10px 14px', background: C.panelAlt, minWidth: 150 }}>
                    <div style={{ fontSize: 11, color: C.textFaint }}>{m.index_name}</div>
                    <div className="risk-num" style={{ fontSize: 22, fontWeight: 600, letterSpacing: '-0.01em', color: C.accent }}>
                      {formatRiskValue(m.index_value)}
                      <span style={{ fontSize: 11, color: C.textDim, marginLeft: 4, fontWeight: 400 }}>{m.index_unit}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* 链接遍历 */}
        <div style={{ ...panel(), padding: 16 }}>
          <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 4, color: C.textDim }}>关联链路（本体链接遍历）</div>
          <div style={{ fontSize: 12, color: C.textFaint, marginBottom: 12 }}>从本体链接出发，沿关系一路点下去，无孤岛。</div>
          {out.size === 0 && inn.size === 0 && <div style={{ color: C.textFaint, fontSize: 13 }}>该记录在演示样本内暂无关联（样本是真实数据的切片）。</div>}
          {[...out.entries()].map(([link, v]) => (
            <LinkRow key={'out-' + link} label={link} count={v.items.length} direction="出" color={C.blue} onClick={() => onOpenLinks(link, v.targetType, v.items)} />
          ))}
          {[...inn.entries()].map(([link, v]) => (
            <LinkRow key={'in-' + link} label={link} count={v.items.length} direction="入" color={C.accent} onClick={() => onOpenLinks(link, v.targetType, v.items)} />
          ))}
        </div>
      </div>
    </div>
  );
}

function LinkRow({ label, count, direction, color, onClick }: { label: string; count: number; direction: string; color: string; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      style={{
        display: 'flex', alignItems: 'center', gap: 8, width: '100%', cursor: 'pointer', textAlign: 'left',
        padding: '9px 10px', marginBottom: 6, borderRadius: 6, fontSize: 12.5,
        background: C.panelAlt, border: '1px solid ' + C.border, color: C.text,
      }}
    >
      <span style={{ fontSize: 10, padding: '1px 5px', borderRadius: 6, background: color, color: '#ffffff', fontWeight: 600 }}>{direction}</span>
      <span style={{ flex: 1 }}>{label}</span>
      <span className="risk-num" style={{ color: C.textFaint }}>{count}</span>
      <ArrowRightOutlined style={{ color: C.textFaint, fontSize: 11 }} />
    </button>
  );
}

// ---- 链接导航 ----
function LinksPane({
  snapshot, type, pk, displayLink, targetType, items, onBack, onOpenDetail,
}: {
  snapshot: RiskSnapshot;
  type: RiskObjectMeta;
  pk: string;
  displayLink: string;
  targetType: string;
  items: RiskItem[];
  onBack: () => void;
  onOpenDetail: (api: string, pk: string) => void;
}) {
  const targetMeta = snapshot.meta.objects.find((o) => o.api_name === targetType);
  const fields = targetMeta ? LIST_FIELDS[targetMeta.api_name] ?? Object.keys(targetMeta.properties).slice(0, 5) : [];
  const columns = [
    { title: '标识', dataIndex: 'pk', key: 'pk', width: 190, render: (v: string) => <span className="risk-num" style={{ color: C.accent }}>{v}</span> },
    ...fields.filter((f) => f !== (targetMeta?.pk_field ?? 'pk')).map((f) => ({
      title: targetMeta?.properties[f]?.title ?? f, dataIndex: ['properties', f] as string[], key: f,
      render: (_v: unknown, r: RiskItem) => renderCell(targetMeta as RiskObjectMeta, f, r.properties[f]),
    })),
  ];
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 14, flexWrap: 'wrap' }}>
        <Button size="small" icon={<RollbackOutlined />} onClick={onBack}>返回详情</Button>
        <Title level={4} style={{ margin: 0, letterSpacing: '-0.01em', fontWeight: 600 }}>链接遍历</Title>
        <span className="risk-num" style={{ color: C.accent, fontSize: 13 }}>{displayLink}</span>
        <Text style={{ color: C.textFaint, fontSize: 12.5 }}>
          {shortName(type.description)} {pk} → {targetMeta ? shortName(targetMeta.description) : targetType}（{items.length} 条）
        </Text>
      </div>
      <TableBox>
        <Table<RiskItem>
          columns={columns}
          dataSource={items}
          rowKey={(r) => r.pk}
          size="small"
          pagination={false}
          scroll={{ x: 880 }}
          onRow={(r) => ({ onClick: () => onOpenDetail(targetType, r.pk), style: { cursor: 'pointer' } })}
          locale={{ emptyText: <span style={{ color: C.textFaint }}>无关联记录</span> }}
          style={{ background: 'transparent' }}
          components={{ header: { cell: headerCell } }}
        />
      </TableBox>
    </div>
  );
}

function panel() {
  return { background: C.panel, border: '1px solid ' + C.border, borderRadius: 8 };
}

function TableBox({ children }: React.PropsWithChildren) {
  return <div style={{ border: '1px solid ' + C.border, borderRadius: 8, overflow: 'hidden', background: C.panel }}>{children}</div>;
}
