// 管道画布 —— @xyflow/react 渲染端到端流程概览 + 管道 DAG 编辑/查看/运行/历史
// 节点/连线由各构建段列表与 dag_json 驱动，不硬编码业务。
import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  ReactFlow,
  Background,
  BackgroundVariant,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  Handle,
  Position,
  type Connection,
  type Node,
  type NodeProps,
  type NodeTypes,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useTranslation } from 'react-i18next';
import {
  Alert,
  Button,
  Card,
  Form,
  Input,
  Modal,
  Select,
  Space,
  Table,
  Tabs,
  Tag,
  Typography,
  message,
} from 'antd';
import { DeleteOutlined, PlayCircleOutlined, SaveOutlined } from '@ant-design/icons';
import {
  createPipeline,
  getPipeline,
  listCurated,
  listDatasets,
  listExtractions,
  listMappings,
  listObjectTypes,
  pipelineRuns,
  runPipeline,
} from '../apiBuilder';
import {
  NODE_KINDS,
  SAMPLE_DAG,
  buildE2EFlow,
  buildPipelineFlow,
  KIND_COLORS,
  type E2ESegments,
  type FlowEdge,
  type FlowNode,
  type FlowNodeData,
} from '../pipelineFlow';
import type { DagJson, PipelineRunItem } from '../builderTypes';

const { Text } = Typography;
const PIPELINES_KEY = 'ontorun.pipelines';

function loadPipelineNames(): string[] {
  try {
    const raw = localStorage.getItem(PIPELINES_KEY);
    const arr = raw ? JSON.parse(raw) : [];
    return Array.isArray(arr) ? arr.filter((x) => typeof x === 'string') : [];
  } catch {
    return [];
  }
}

function savePipelineNames(names: string[]): void {
  try {
    localStorage.setItem(PIPELINES_KEY, JSON.stringify(names));
  } catch {
    // ignore
  }
}

function DagNodeCard({ data }: NodeProps<Node<FlowNodeData>>) {
  const bg = data.color || KIND_COLORS[data.kind || ''] || '#8c8c8c';
  return (
    <div
      style={{
        border: '1.5px solid ' + bg,
        borderRadius: 10,
        background: '#ffffff',
        padding: '6px 12px',
        minWidth: 150,
        textAlign: 'center',
        boxShadow: '0 1px 4px rgba(0,0,0,0.12)',
        fontSize: 13,
      }}
    >
      <Handle type="target" position={Position.Left} style={{ background: bg }} />
      <div style={{ fontWeight: 600 }}>{data.label}</div>
      {data.sub && (
        <div style={{ fontSize: 11, color: '#8c8c8c', marginTop: 2 }}>{data.sub}</div>
      )}
      <Handle type="source" position={Position.Right} style={{ background: bg }} />
    </div>
  );
}

const nodeTypes: NodeTypes = { dag: DagNodeCard };

export default function PipelineCanvas() {
  const { t } = useTranslation();
  const [tab, setTab] = useState('e2e');

  // ---- e2e 概览 ----
  const [segments, setSegments] = useState<E2ESegments | null>(null);
  const [e2eDetail, setE2eDetail] = useState<{ title: string; items: string[] } | null>(null);

  // ---- 管道编辑器 ----
  const [pipelineNames, setPipelineNames] = useState<string[]>(loadPipelineNames);
  const [selectedName, setSelectedName] = useState<string | null>(null);
  const [nodes, setNodes, onNodesChange] = useNodesState<FlowNode>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<FlowEdge>([]);
  const [createOpen, setCreateOpen] = useState(false);
  const [createForm] = Form.useForm();
  const [saving, setSaving] = useState(false);
  const [running, setRunning] = useState(false);
  const [runs, setRuns] = useState<PipelineRunItem[]>([]);
  const [runResult, setRunResult] = useState<string | null>(null);

  const loadE2E = useCallback(async () => {
    try {
      const [ds, cur, mp, ex, pub] = await Promise.all([
        listDatasets({ page_size: 100 }),
        listCurated({ page_size: 100 }),
        listMappings({ page_size: 100 }),
        listExtractions({ page_size: 100 }),
        listObjectTypes({ status: 'published', page_size: 100 }),
      ]);
      setSegments({
        datasets: ds.items,
        curated: cur.items,
        mappings: mp.items,
        extractions: ex.items,
        published: pub.items,
      });
    } catch (err) {
      message.error(t('pipeline.loadFailed', { msg: (err as Error).message }));
      setSegments({ datasets: [], curated: [], mappings: [], extractions: [], published: [] });
    }
  }, [t]);

  useEffect(() => {
    if (tab === 'e2e') void loadE2E();
  }, [tab, loadE2E]);

  const loadPipeline = useCallback(
    async (name: string) => {
      try {
        const pl = await getPipeline(name);
        const flow = buildPipelineFlow(pl.dag_json || { nodes: [] });
        setNodes(flow.nodes);
        setEdges(flow.edges);
        setSelectedName(name);
      } catch (err) {
        message.error(t('pipeline.loadFailed', { msg: (err as Error).message }));
      }
    },
    [setNodes, setEdges, t],
  );

  const loadRuns = useCallback(async (name: string) => {
    try {
      const data = await pipelineRuns(name);
      setRuns(data.runs);
    } catch {
      setRuns([]);
    }
  }, []);

  const selectPipeline = useCallback(
    async (name: string) => {
      setSelectedName(name);
      await loadPipeline(name);
      void loadRuns(name);
    },
    [loadPipeline, loadRuns],
  );

  const e2eFlow = useMemo(() => {
    if (!segments) return null;
    return buildE2EFlow(segments, (k, o) => t(k, o));
  }, [segments, t]);

  const onConnect = useCallback(
    (conn: Connection) => {
      if (!conn.source || !conn.target || conn.source === conn.target) return;
      setEdges((eds) => {
        if (eds.some((e) => e.source === conn.source && e.target === conn.target)) return eds;
        return addEdge({ ...conn, id: conn.source + '__' + conn.target }, eds);
      });
    },
    [setEdges],
  );

  const addNode = useCallback(
    (kind: string) => {
      const count = nodes.filter((n) => (n.data.kind || '') === kind).length + 1;
      const id = kind + '_' + count;
      const layer = Math.max(...nodes.map((n) => n.position.x), 0) / 280 + 1;
      setNodes((nds) => [
        ...nds,
        {
          id,
          type: 'dag',
          position: { x: 40 + layer * 280, y: 40 + nds.length * 60 },
          data: { label: id, sub: kind, kind, color: KIND_COLORS[kind] || '#8c8c8c' },
        },
      ]);
    },
    [nodes, setNodes],
  );

  const removeSelected = useCallback(() => {
    setNodes((nds) => {
      const sel = nds.filter((n) => n.selected).map((n) => n.id);
      if (!sel.length) return nds;
      setEdges((eds) => eds.filter((e) => !sel.includes(e.source) && !sel.includes(e.target)));
      return nds.filter((n) => !sel.includes(n.id));
    });
  }, [setNodes, setEdges]);

  const currentDag = useCallback((): DagJson => {
    return {
      nodes: nodes.map((n) => ({
        id: n.id,
        kind: (n.data.kind as DagJson['nodes'][number]['kind']) || 'transform',
        config: {},
        next: edges.filter((e) => e.source === n.id).map((e) => e.target),
      })),
    };
  }, [nodes, edges]);

  const handleSave = async () => {
    if (!selectedName) {
      message.warning(t('pipeline.selectPipeline'));
      return;
    }
    setSaving(true);
    try {
      await createPipeline(selectedName, currentDag(), 'draft');
      message.success(t('pipeline.created', { name: selectedName }));
      if (!pipelineNames.includes(selectedName)) {
        const next = [...pipelineNames, selectedName];
        setPipelineNames(next);
        savePipelineNames(next);
      }
    } catch (err) {
      message.error((err as Error).message);
    } finally {
      setSaving(false);
    }
  };

  const handleRun = async () => {
    if (!selectedName) return;
    setRunning(true);
    setRunResult(null);
    try {
      const res = await runPipeline(selectedName);
      setRunResult(
        t('pipeline.runTriggered', { runId: res.run_id, status: res.final_status }) +
          (res.nodes.length ? ' · ' + res.nodes.map((n) => n.node_id + '=' + n.status).join(', ') : ''),
      );
      void loadRuns(selectedName);
    } catch (err) {
      message.error(t('pipeline.runFailed', { msg: (err as Error).message }));
    } finally {
      setRunning(false);
    }
  };

  const handleCreate = async () => {
    try {
      const { name } = await createForm.validateFields();
      const clean = String(name).trim();
      if (!clean) return;
      setCreateOpen(false);
      createForm.resetFields();
      setSelectedName(clean);
      const flow = buildPipelineFlow({ nodes: [] });
      setNodes(flow.nodes);
      setEdges(flow.edges);
      setRuns([]);
      setRunResult(null);
    } catch {
      // 表单校验失败
    }
  };

  const loadTemplate = () => {
    const flow = buildPipelineFlow(SAMPLE_DAG);
    setNodes(flow.nodes);
    setEdges(flow.edges);
    setRunResult(null);
  };

  const stageClick = useCallback(
    (nodeId: string) => {
      if (!segments || !nodeId.startsWith('stage-')) return;
      const key = nodeId.slice('stage-'.length);
      const map: Record<string, { title: string; list: { name?: string; id?: string }[] }> = {
        datasets: { title: t('builder.datasets'), list: segments.datasets },
        curated: { title: t('builder.curated'), list: segments.curated },
        mappings: { title: t('builder.mappings'), list: segments.mappings },
        extractions: { title: t('builder.extractions'), list: segments.extractions },
        publish: { title: t('builder.objectTypes'), list: segments.published },
      };
      const hit = map[key];
      if (hit) {
        setE2eDetail({ title: hit.title, items: hit.list.map((x) => x.name || x.id || '') });
      }
    },
    [segments, t],
  );

  const runsColumns = useMemo(
    () => [
      { title: t('pipeline.runId'), dataIndex: 'run_id', key: 'run_id' },
      {
        title: t('pipeline.finalStatus'),
        dataIndex: 'final_status',
        key: 'final_status',
        render: (v: string) => (
          <Tag color={v === 'succeeded' ? 'green' : v === 'failed' ? 'red' : 'orange'}>{v}</Tag>
        ),
      },
      { title: t('pipeline.nodeStatus'), dataIndex: 'node_count', key: 'node_count' },
      { title: t('pipeline.startedAt'), dataIndex: 'started_at', key: 'started_at' },
      { title: t('pipeline.finishedAt'), dataIndex: 'finished_at', key: 'finished_at' },
    ],
    [t],
  );

  return (
    <div>
      <Tabs
        activeKey={tab}
        onChange={setTab}
        items={[
          {
            key: 'e2e',
            label: t('pipeline.e2eTitle'),
            children: (
              <Card>
                <Text type="secondary" style={{ display: 'block', marginBottom: 12 }}>
                  {t('pipeline.e2eDesc')}
                </Text>
                {e2eFlow ? (
                  <div style={{ height: 480 }}>
                    <ReactFlow
                      nodes={e2eFlow.nodes}
                      edges={e2eFlow.edges}
                      nodeTypes={nodeTypes}
                      fitView
                      onNodeClick={(_, node) => stageClick(node.id)}
                      nodesDraggable={false}
                      nodesConnectable={false}
                      proOptions={{ hideAttribution: true }}
                    >
                      <Background variant={BackgroundVariant.Dots} gap={16} />
                      <Controls />
                      <MiniMap pannable zoomable />
                    </ReactFlow>
                  </div>
                ) : (
                  <Alert type="info" message={t('common.loading')} showIcon />
                )}
              </Card>
            ),
          },
          {
            key: 'editor',
            label: t('pipeline.editorTitle'),
            children: (
              <Space direction="vertical" style={{ width: '100%' }} size={16}>
                <Card size="small">
                  <Space wrap>
                    <Select
                      style={{ minWidth: 220 }}
                      placeholder={t('pipeline.selectPipeline')}
                      value={selectedName ?? undefined}
                      onChange={(v) => void selectPipeline(v)}
                      options={pipelineNames.map((n) => ({ value: n, label: n }))}
                    />
                    <Button type="primary" onClick={() => setCreateOpen(true)}>
                      {t('common.create')}
                    </Button>
                    <Button onClick={loadTemplate}>{t('pipeline.loadTemplate')}</Button>
                  </Space>
                </Card>
                <Card size="small" title={t('builder.pipelines') + ' · ' + (selectedName || '-')}>
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <Space wrap>
                      {NODE_KINDS.map((k) => (
                        <Button key={k} icon={<span style={{ color: KIND_COLORS[k] }}>●</span>} onClick={() => addNode(k)}>
                          {t('pipeline.addNode', { kind: t('pipeline.nodeKinds.' + k) })}
                        </Button>
                      ))}
                      <Button danger icon={<DeleteOutlined />} onClick={removeSelected}>
                        {t('common.delete')}
                      </Button>
                      <Button icon={<SaveOutlined />} type="primary" loading={saving} onClick={() => void handleSave()}>
                        {t('pipeline.savePipeline')}
                      </Button>
                      <Button icon={<PlayCircleOutlined />} type="primary" ghost loading={running} onClick={() => void handleRun()}>
                        {t('pipeline.runPipeline')}
                      </Button>
                    </Space>
                    {runResult && (
                      <Alert type={runResult.includes('failed') ? 'error' : 'success'} message={runResult} closable onClose={() => setRunResult(null)} />
                    )}
                    <div style={{ height: 420, border: '1px solid #f0f0f0', borderRadius: 8 }}>
                      <ReactFlow
                        nodes={nodes}
                        edges={edges}
                        nodeTypes={nodeTypes}
                        onNodesChange={onNodesChange}
                        onEdgesChange={onEdgesChange}
                        onConnect={onConnect}
                        fitView
                        proOptions={{ hideAttribution: true }}
                      >
                        <Background variant={BackgroundVariant.Dots} gap={16} />
                        <Controls />
                        <MiniMap pannable zoomable />
                      </ReactFlow>
                    </div>
                    <div>
                      <Text strong>{t('pipeline.runs')}</Text>
                      <Table
                        rowKey="run_id"
                        columns={runsColumns}
                        dataSource={runs}
                        size="small"
                        pagination={false}
                        style={{ marginTop: 8 }}
                        locale={{ emptyText: t('common.noData') }}
                      />
                    </div>
                  </Space>
                </Card>
              </Space>
            ),
          },
        ]}
      />
      <Modal
        title={t('pipeline.create')}
        open={createOpen}
        onOk={() => void handleCreate()}
        onCancel={() => setCreateOpen(false)}
        destroyOnHidden
      >
        <Form form={createForm} layout="vertical">
          <Form.Item
            name="name"
            label={t('pipeline.pipelineName')}
            rules={[{ required: true, message: t('actions.required', { label: t('pipeline.pipelineName') }) }]}
          >
            <Input placeholder="my_pipeline" />
          </Form.Item>
        </Form>
      </Modal>
      <Modal
        title={e2eDetail?.title}
        open={!!e2eDetail}
        footer={null}
        onCancel={() => setE2eDetail(null)}
      >
        <ul style={{ maxHeight: 320, overflowY: 'auto', paddingLeft: 20 }}>
          {e2eDetail?.items.map((it, i) => (
            <li key={i}>{it || '(unnamed)'}</li>
          ))}
        </ul>
      </Modal>
    </div>
  );
}