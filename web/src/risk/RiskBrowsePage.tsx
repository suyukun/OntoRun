// 风险数据浏览页（/risk/browse）—— 按业务对象浏览 ap_anping 真实风险数据
// 数据源：物化快照（web/public/risk-demo/risk-snapshot.json，由脚本同源生成）。
// 列表 → 详情（属性 + 链接 out/in）→ 链接遍历，全程 schema 驱动，无空对象、无孤岛。
import { useMemo, useState } from 'react';
import { Button, ConfigProvider, Input, Table, Tag, Typography, theme as antdTheme } from 'antd';
import { ArrowRightOutlined, DatabaseOutlined, RollbackOutlined, SearchOutlined } from '@ant-design/icons';
import './risk.css';
import { RISK_COLORS, riskDarkTheme, WARN_LEVEL_META } from './riskTheme';
import { dataObjectTypes, formatRiskValue, traversalFor, useRiskSnapshot } from './riskData';
import type { RiskItem, RiskObjectMeta, RiskSnapshot } from './riskData';

const { Title, Text } = Typography;

// 业务域分组（展示偏好；对象/字段仍由 schema 驱动）
const DOMAIN_GROUPS: { key: string; label: string; objects: string[] }[] = [
  { key: 'customer', label: '客户域', objects: ['group_customer', 'risk_customer'] },
  { key: 'monitor', label: '风险监测域', objects: ['warning_signal', 'concentration_limit', 'metric'] },
  { key: 'disposal', label: '预警处置域', objects: ['disposal', 'approve_order', 'approve_task'] },
  { key: 'project', label: '风险项目域', objects: ['risk_project'] },
];

// 列表展示字段偏好（各对象取 4-6 个关键字段；完整字段在详情看）
const LIST_FIELDS: Record<string, string[]> = {
  risk_customer: ['customer_name', 'customer_no', 'industry_name', 'internal_level', 'asset_quality_level', 'group_customer_no'],
  group_customer: ['group_customer_name', 'member_count', 'customer_status', 'asset_quality_level'],
  warning_signal: ['signal_name', 'customer_name', 'warn_level', 'signal_status', 'risk_exposure', 'signal_generate_date'],
  disposal: ['disposal_status', 'warning_id', 'disposal_time'],
  approve_order: ['approve_order_title', 'approve_order_status', 'business_type', 'apply_time'],
  approve_task: ['approve_order_id', 'approve_task_status', 'approve_result', 'approve_time'],
  concentration_limit: ['customer_name', 'concentration_limit', 'warning_value', 'current_status'],
  risk_project: ['project_name', 'group_customer_name', 'business_balance', 'risk_exposure_balance', 'five_classification', 'guarantee_method'],
  metric: ['index_name', 'index_value', 'index_unit', 'dim_type_name', 'group_customer_no'],
};

const STATUS_COLORS: Record<string, string> = {
  待确认: RISK_COLORS.textFaint,
  确认中: RISK_COLORS.blue,
  已确认: RISK_COLORS.yellow,
  处置中: RISK_COLORS.red,
  已关闭: RISK_COLORS.textDim,
  已撤销: RISK_COLORS.textFaint,
  未处置: RISK_COLORS.textFaint,
  暂缓处置: RISK_COLORS.textDim,
  已处置: RISK_COLORS.green,
  PROCESS: RISK_COLORS.blue,
  APPROVED: RISK_COLORS.green,
  REJECTED: RISK_COLORS.red,
  PENDING: RISK_COLORS.yellow,
  COMPLETED: RISK_COLORS.green,
  NORMAL: RISK_COLORS.green,
  ORANGE_ALERT: RISK_COLORS.yellow,
  RED_ALERT: RISK_COLORS.red,
};

type View =
  | { kind: 'list'; type: RiskObjectMeta }
  | { kind: 'detail'; type: RiskObjectMeta; pk: string }
  | { kind: 'links'; type: RiskObjectMeta; pk: string; displayLink: string; targetType: string; items: RiskItem[] };

export default function RiskBrowsePage() {
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
    <ConfigProvider theme={{ ...riskDarkTheme, algorithm: antdTheme.darkAlgorithm }}>
      <div className="risk-bg" style={{ minHeight: '100vh', color: RISK_COLORS.text, display: 'flex' }}>
        {/* 对象侧栏（按业务域分组） */}
        <div style={{ width: 232, flex: '0 0 auto', borderRight: '1px solid ' + RISK_COLORS.border, background: RISK_COLORS.surface, padding: '16px 10px', overflowY: 'auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '0 8px 14px', fontSize: 13.5, fontWeight: 700 }}>
            <DatabaseOutlined style={{ color: RISK_COLORS.accent }} /> 业务对象
          </div>
          {DOMAIN_GROUPS.map((g) => {
            const objects = g.objects.map((api) => findType(api)).filter((x): x is RiskObjectMeta => !!x);
            if (objects.length === 0) return null;
            return (
              <div key={g.key} style={{ marginBottom: 10 }}>
                <div style={{ fontSize: 11, color: RISK_COLORS.textFaint, letterSpacing: '0.08em', padding: '4px 8px' }}>{g.label}</div>
                {objects.map((o) => (
                  <button
                    key={o.api_name}
                    onClick={() => showList(o.api_name)}
                    style={{
                      display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', textAlign: 'left', cursor: 'pointer',
                      padding: '8px 10px', borderRadius: 4, marginBottom: 2, fontSize: 13, color: RISK_COLORS.text,
                      background: selectedKey === o.api_name ? 'rgba(242,176,76,0.12)' : 'transparent',
                      border: selectedKey === o.api_name ? '1px solid rgba(242,176,76,0.4)' : '1px solid transparent',
                    }}
                  >
                    <span>{shortName(o.description)}</span>
                    <span className="risk-num" style={{ color: RISK_COLORS.textFaint, fontSize: 11.5 }}>
                      {data ? formatCount(data.totals[o.api_name]) : '…'}
                    </span>
                  </button>
                ))}
              </div>
            );
          })}
          {error && (
            <div style={{ padding: 10, fontSize: 12, color: RISK_COLORS.red }}>快照加载失败：{error}</div>
          )}
        </div>

        {/* 主区 */}
        <div style={{ flex: 1, minWidth: 0, padding: 20 }}>
          {renderView()}
        </div>
      </div>
    </ConfigProvider>
  );

  function renderView() {
    if (!data) {
      return (
        <div style={{ textAlign: 'center', padding: 80, color: RISK_COLORS.textFaint }}>
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
      render: (pk: string) => <span className="risk-num" style={{ color: RISK_COLORS.accent }}>{pk}</span> },
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
          <Title level={4} style={{ margin: 0, color: RISK_COLORS.text }}>{shortName(type.description)}</Title>
          <Text style={{ color: RISK_COLORS.textFaint, fontSize: 12.5 }}>
            共 <span className="risk-num" style={{ color: RISK_COLORS.accent }}>{snapshot.totals[type.api_name]}</span> 条 · 演示展示样本 {all.length} 条（同一数据源）
          </Text>
        </div>
        <Input
          allowClear
          prefix={<SearchOutlined style={{ color: RISK_COLORS.textFaint }} />}
          placeholder={'搜索（如 中科智造 / WS-2026…）'}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ width: 240, background: RISK_COLORS.ink, borderColor: RISK_COLORS.border, color: RISK_COLORS.text }}
        />
      </div>
      <div style={{ border: '1px solid ' + RISK_COLORS.border, borderRadius: 6, overflow: 'hidden', background: RISK_COLORS.panel }}>
        <Table<RiskItem>
          columns={columns}
          dataSource={filtered}
          rowKey={(r) => r.pk}
          size="small"
          pagination={{ pageSize: 10, size: 'small', showTotal: (t) => '共 ' + t + ' 条' }}
          scroll={{ x: 980 }}
          onRow={(r) => ({ onClick: () => onOpenDetail(r.pk), style: { cursor: 'pointer' } })}
          locale={{ emptyText: <span style={{ color: RISK_COLORS.textFaint }}>无匹配记录</span> }}
          style={{ background: 'transparent' }}
          components={{ header: { cell: (props: React.PropsWithChildren<{ [k: string]: unknown }>) => <th {...props} style={{ background: RISK_COLORS.surface, color: RISK_COLORS.textDim, fontWeight: 600, borderBottom: '1px solid ' + RISK_COLORS.border }} /> } }}
        />
      </div>
    </div>
  );
}

function renderCell(type: RiskObjectMeta, field: string, v: unknown) {
  if (field === 'warn_level') {
    const meta = WARN_LEVEL_META[String(v ?? '')];
    return meta ? <Tag color={meta.color} style={{ color: '#fff' }}>{meta.label}</Tag> : <span>{String(v ?? '')}</span>;
  }
  if (field === 'signal_status' || field === 'disposal_status' || field === 'current_status' || field === 'approve_order_status' || field === 'approve_task_status' || field === 'approve_result') {
    const c = STATUS_COLORS[String(v ?? '')];
    return c ? <Tag style={{ color: c, borderColor: c, background: 'transparent' }}>{String(v ?? '')}</Tag> : <span>{String(v ?? '')}</span>;
  }
  if (typeof v === 'number') {
    return <span className="risk-num" style={{ color: RISK_COLORS.text }}>{formatRiskValue(v)}</span>;
  }
  return <span style={{ color: RISK_COLORS.textDim }}>{formatRiskValue(v)}</span>;
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
  if (!item) return <div style={{ color: RISK_COLORS.textFaint }}>记录不存在</div>;
  const out = traversalFor(snapshot, type.api_name, pk, 'out');
  const inn = traversalFor(snapshot, type.api_name, pk, 'in');
  const metrics = type.api_name === 'group_customer' ? snapshot.group_metrics[pk] : undefined;

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 14, flexWrap: 'wrap' }}>
        <Button size="small" icon={<RollbackOutlined />} onClick={onBack} style={{ background: 'transparent', borderColor: RISK_COLORS.border, color: RISK_COLORS.textDim }}>
          返回列表
        </Button>
        <Title level={4} style={{ margin: 0, color: RISK_COLORS.text }}>{shortName(type.description)}</Title>
        <span className="risk-num" style={{ color: RISK_COLORS.accent, fontSize: 13 }}>{pk}</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.3fr 1fr', gap: 16, alignItems: 'start' }}>
        <div>
          <div style={{ ...panel(), padding: 16, marginBottom: 16 }}>
            <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 10, color: RISK_COLORS.textDim }}>属性</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 8 }}>
              {Object.entries(type.properties).map(([f, p]) => {
                const v = item.properties[f];
                return (
                  <div key={f} style={{ border: '1px solid ' + RISK_COLORS.border, borderRadius: 4, padding: '7px 10px', background: RISK_COLORS.surface }}>
                    <div style={{ fontSize: 11, color: RISK_COLORS.textFaint, marginBottom: 3 }}>{p.title}</div>
                    <div style={{ fontSize: 13, wordBreak: 'break-all' }}>{renderCell(type, f, v)}</div>
                  </div>
                );
              })}
            </div>
          </div>
          {metrics && metrics.length > 0 && (
            <div style={{ ...panel(), padding: 16 }}>
              <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 10, color: RISK_COLORS.textDim }}>集团风险指标（真实聚合，来自维度指标库）</div>
              <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                {metrics.map((m) => (
                  <div key={m.index_name} style={{ border: '1px solid ' + RISK_COLORS.border, borderRadius: 4, padding: '10px 14px', background: RISK_COLORS.surface, minWidth: 150 }}>
                    <div style={{ fontSize: 11, color: RISK_COLORS.textFaint }}>{m.index_name}</div>
                    <div className="risk-num" style={{ fontSize: 20, fontWeight: 700, color: RISK_COLORS.accent }}>
                      {formatRiskValue(m.index_value)}
                      <span style={{ fontSize: 11, color: RISK_COLORS.textDim, marginLeft: 4 }}>{m.index_unit}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* 链接遍历 */}
        <div style={{ ...panel(), padding: 16 }}>
          <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 4, color: RISK_COLORS.textDim }}>关联链路（本体链接遍历）</div>
          <div style={{ fontSize: 12, color: RISK_COLORS.textFaint, marginBottom: 12 }}>从本体链接出发，沿关系一路点下去，无孤岛。</div>
          {out.size === 0 && inn.size === 0 && <div style={{ color: RISK_COLORS.textFaint, fontSize: 13 }}>该记录在演示样本内暂无关联（样本是真实数据的切片）。</div>}
          {[...out.entries()].map(([link, v]) => (
            <LinkRow key={'out-' + link} label={link} count={v.items.length} direction="出" color={RISK_COLORS.blue} onClick={() => onOpenLinks(link, v.targetType, v.items)} />
          ))}
          {[...inn.entries()].map(([link, v]) => (
            <LinkRow key={'in-' + link} label={link} count={v.items.length} direction="入" color={RISK_COLORS.accent} onClick={() => onOpenLinks(link, v.targetType, v.items)} />
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
        padding: '9px 10px', marginBottom: 6, borderRadius: 4, fontSize: 12.5,
        background: RISK_COLORS.surface, border: '1px solid ' + RISK_COLORS.border, color: RISK_COLORS.text,
      }}
    >
      <span style={{ fontSize: 10, padding: '1px 5px', borderRadius: 3, background: color, color: '#06101f', fontWeight: 700 }}>{direction}</span>
      <span style={{ flex: 1 }}>{label}</span>
      <span className="risk-num" style={{ color: RISK_COLORS.textFaint }}>{count}</span>
      <ArrowRightOutlined style={{ color: RISK_COLORS.textFaint, fontSize: 11 }} />
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
    { title: '标识', dataIndex: 'pk', key: 'pk', width: 190, render: (v: string) => <span className="risk-num" style={{ color: RISK_COLORS.accent }}>{v}</span> },
    ...fields.filter((f) => f !== (targetMeta?.pk_field ?? 'pk')).map((f) => ({
      title: targetMeta?.properties[f]?.title ?? f, dataIndex: ['properties', f] as string[], key: f,
      render: (_v: unknown, r: RiskItem) => renderCell(targetMeta as RiskObjectMeta, f, r.properties[f]),
    })),
  ];
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 14, flexWrap: 'wrap' }}>
        <Button size="small" icon={<RollbackOutlined />} onClick={onBack} style={{ background: 'transparent', borderColor: RISK_COLORS.border, color: RISK_COLORS.textDim }}>
          返回详情
        </Button>
        <Title level={4} style={{ margin: 0, color: RISK_COLORS.text }}>链接遍历</Title>
        <span className="risk-num" style={{ color: RISK_COLORS.accent, fontSize: 13 }}>{displayLink}</span>
        <Text style={{ color: RISK_COLORS.textFaint, fontSize: 12.5 }}>
          {shortName(type.description)} {pk} → {targetMeta ? shortName(targetMeta.description) : targetType}（{items.length} 条）
        </Text>
      </div>
      <div style={{ border: '1px solid ' + RISK_COLORS.border, borderRadius: 6, overflow: 'hidden', background: RISK_COLORS.panel }}>
        <Table<RiskItem>
          columns={columns}
          dataSource={items}
          rowKey={(r) => r.pk}
          size="small"
          pagination={false}
          scroll={{ x: 880 }}
          onRow={(r) => ({ onClick: () => onOpenDetail(targetType, r.pk), style: { cursor: 'pointer' } })}
          locale={{ emptyText: <span style={{ color: RISK_COLORS.textFaint }}>无关联记录</span> }}
          style={{ background: 'transparent' }}
          components={{ header: { cell: (props: React.PropsWithChildren<{ [k: string]: unknown }>) => <th {...props} style={{ background: RISK_COLORS.surface, color: RISK_COLORS.textDim, fontWeight: 600, borderBottom: '1px solid ' + RISK_COLORS.border }} /> } }}
        />
      </div>
    </div>
  );
}

function panel() {
  return { background: RISK_COLORS.panel, border: '1px solid ' + RISK_COLORS.border, borderRadius: 6 };
}
