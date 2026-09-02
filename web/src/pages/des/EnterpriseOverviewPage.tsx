// DES 企业模拟概览页（/des）—— 让「DES 升级」看得见：
// 概览卡（元信息）+ DDD 业务域 + 数据资产明细（每库每表实时行数 vs 生成清单对照）。
// 视觉基线：AntD 默认浅色 token（RiskShell 是深色风控壳，本页局部切回 light algorithm）；
// 阶段④统一重做视觉，此处不做装饰性设计。
import { Alert, Card, Col, ConfigProvider, Empty, Row, Select, Statistic, Table, Tag, Typography, theme } from 'antd';
import { ApartmentOutlined, ClusterOutlined } from '@ant-design/icons';
import { RISK_COLORS as C } from '../../risk/riskTheme';
import type { ColumnsType } from 'antd/es/table';
import { useEffect, useMemo, useState } from 'react';
import {
  fetchDesOverview,
  flattenDatabases,
  useDesEnterprises,
} from './desData';
import type { DesDomain, DesOverview } from './desData';

const TAGLINE = 'DES 企业模拟 · 数据由 des-enterprise-modeling 确定性流水线生成';

function formatCount(n: number | null | undefined): string {
  if (n == null) return '—';
  return n.toLocaleString('zh-CN');
}

function renderCount(cell: { rows: number | null; manifest_rows: number | null }) {
  // 实时行数；与生成清单不一致时如实标漂移量（演示期真实写回所致，正是要看的变化）
  const diff = cell.rows != null && cell.manifest_rows != null ? cell.rows - cell.manifest_rows : 0;
  return (
    <span>
      {formatCount(cell.rows)}
      {diff !== 0 && (
        <Tag color="orange" style={{ marginLeft: 8 }}>
          {diff > 0 ? '清单差 +' + diff : '清单差 ' + diff}
        </Tag>
      )}
    </span>
  );
}

/** yaml domains 未定型：只渲染确证字段（name/description），其余键值行如实列出。 */
function DomainCard({ domain }: { domain: DesDomain }) {
  const name = typeof domain.name === 'string' ? domain.name : JSON.stringify(domain.name ?? null);
  const description = typeof domain.description === 'string' ? domain.description : null;
  const extras = Object.entries(domain).filter(
    ([k, v]) => k !== 'name' && k !== 'description' && ['string', 'number', 'boolean'].includes(typeof v),
  );
  return (
    <Card size="small" title={name}>
      {description && (
        <Typography.Paragraph type="secondary" style={{ marginBottom: extras.length ? 8 : 0 }}>
          {description}
        </Typography.Paragraph>
      )}
      {extras.map(([k, v]) => (
        <div key={k} style={{ fontSize: 12.5, color: C.textDim }}>
          {k}: {String(v)}
        </div>
      ))}
    </Card>
  );
}

export default function EnterpriseOverviewPage() {
  const { items, selected, setSelected } = useDesEnterprises();
  const [overview, setOverview] = useState<DesOverview | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [libraryFilter, setLibraryFilter] = useState<string>('');

  useEffect(() => {
    if (!selected) return;
    let alive = true;
    setLoading(true);
    setError(null);
    fetchDesOverview(selected)
      .then((d) => alive && setOverview(d))
      .catch((e) => alive && setError(String(e?.message ?? e)))
      .finally(() => alive && setLoading(false));
    return () => {
      alive = false;
    };
  }, [selected]);

  const rows = useMemo(() => flattenDatabases(overview?.databases ?? []), [overview]);
  const libraries = useMemo(() => overview?.databases.map((db) => db.file) ?? [], [overview]);
  const filtered = libraryFilter ? rows.filter((r) => r.library === libraryFilter) : rows;

  const columns: ColumnsType<(typeof rows)[number]> = [
    { title: '表名', dataIndex: 'table' },
    { title: '所属库', dataIndex: 'library' },
    {
      title: '实时行数',
      dataIndex: 'rows',
      defaultSortOrder: 'descend',
      sorter: (a, b) => (a.rows ?? -1) - (b.rows ?? -1),
      render: (_v, rec) => renderCount(rec),
    },
    {
      title: '生成清单行数',
      dataIndex: 'manifest_rows',
      sorter: (a, b) => (a.manifest_rows ?? -1) - (b.manifest_rows ?? -1),
      render: (v: number | null) => formatCount(v),
    },
  ];

  const ent = overview?.enterprise;

  return (
    <ConfigProvider theme={{ algorithm: theme.defaultAlgorithm }}>
      <div style={{ minHeight: '100vh', background: C.ink, padding: 24 }}>
        {/* 页面级 h1（视觉隐藏）：屏幕阅读器页面定位 */}
        <h1 className="risk-sr-only">DES 企业模拟总览</h1>
        {/* 入口说明 */}
        <Alert
          type="info"
          showIcon
          icon={<ClusterOutlined />}
          title={TAGLINE}
          description="本页所有数字来自数据单一事实来源：SQLite 库实时 COUNT(*) 与 manifest/des_enterprise.yaml 真实内容，解析不到的字段如实缺省。"
          style={{ marginBottom: 16 }}
        />

        {/* 企业选择 */}
        <Card size="small" style={{ marginBottom: 16 }}>
          <Row align="middle" gutter={16}>
            <Col flex="none">
              <ApartmentOutlined />
            </Col>
            <Col flex="auto">
              <Typography.Title level={4} style={{ margin: 0 }}>
                {ent?.display_name ?? selected ?? '—'}
                {ent?.code_prefix && (
                  <Tag style={{ marginLeft: 10 }}>{ent.code_prefix}</Tag>
                )}
              </Typography.Title>
            </Col>
            <Col flex="none">
              <Select
                value={selected || undefined}
                onChange={setSelected}
                style={{ minWidth: 220 }}
                aria-label="选择企业"
                options={items.map((i) => ({
                  value: i.name,
                  label: i.display_name ? i.display_name + ' (' + i.name + ')' : i.name,
                }))}
              />
            </Col>
          </Row>
        </Card>

        {error && <Alert type="error" message={error} style={{ marginBottom: 16 }} />}

        {/* 概览卡区（数值全部来自端点） */}
        <Row gutter={[12, 12]} style={{ marginBottom: 16 }}>
          <Col xs={8} md={4}><Card size="small"><Statistic title="总库数" value={overview?.totals.databases ?? '—'} loading={loading} /></Card></Col>
          <Col xs={8} md={4}><Card size="small"><Statistic title="总表数" value={overview?.totals.tables ?? '—'} loading={loading} /></Card></Col>
          <Col xs={8} md={4}><Card size="small"><Statistic title="实时总行数" value={overview?.totals.live_rows ?? '—'} loading={loading} /></Card></Col>
          <Col xs={8} md={4}><Card size="small"><Statistic title="seed" value={ent?.seed ?? '—'} formatter={(v) => String(v ?? '—')} loading={loading} /></Card></Col>
          <Col xs={8} md={4}><Card size="small"><Statistic title="数据版本" value={ent?.data_version ?? '—'} loading={loading} /></Card></Col>
          <Col xs={8} md={4}>
            <Card size="small">
              <Statistic
                title="生成时间"
                value={ent?.generated_at ?? '—'}
                loading={loading}
              />
              {ent && ent.generated_at === null && (
                <Typography.Text type="secondary" style={{ fontSize: 11 }}>
                  manifest 无时间戳字段，暂缺省
                </Typography.Text>
              )}
            </Card>
          </Col>
        </Row>

        {/* 业务域区块（缺口如实展示，不编造） */}
        <Card title="DDD 业务域" extra={<Typography.Text type="secondary">来源 des_enterprise.yaml</Typography.Text>} style={{ marginBottom: 16 }}>
          {loading ? (
            <Empty description="加载中…" image={Empty.PRESENTED_IMAGE_SIMPLE} />
          ) : overview == null || overview.domains == null ? (
            <Empty
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              description={
                <span>
                  暂无结构化业务域数据：des_enterprise.yaml 未包含 domains 定义
                  <br />
                  （STEP2 建模产物待以机器可读格式落盘）
                </span>
              }
            />
          ) : (
            <Row gutter={[12, 12]}>
              {overview.domains.map((d, idx) => (
                <Col key={idx} xs={24} md={8}>
                  <DomainCard domain={d} />
                </Col>
              ))}
            </Row>
          )}
        </Card>

        {/* 表清单（实时统计 vs 生成清单对照） */}
        <Card
          title="数据资产明细 · 实时行数"
          extra={
            <Select
              value={libraryFilter}
              onChange={setLibraryFilter}
              style={{ minWidth: 180 }}
              aria-label="按库筛选"
              options={[
                { value: '', label: '全部库' },
                ...libraries.map((lib) => ({ value: lib, label: lib })),
              ]}
            />
          }
        >
          <Table
            size="small"
            loading={loading}
            dataSource={filtered}
            columns={columns}
            rowKey="key"
            pagination={{ pageSize: 20, showSizeChanger: false }}
          />
        </Card>
      </div>
    </ConfigProvider>
  );
}
