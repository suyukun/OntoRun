/* oxlint-disable react/only-export-components */
// 本体图谱 —— cytoscape 渲染 对象类型×链接类型 图
// 铁律：节点/边全部由 /meta/schema 元数据驱动，不硬编码业务。
// buildGraphElements 为纯函数，便于 vitest 直接断言（cytoscape 在 jsdom 不可用）。
import { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import type { Core } from 'cytoscape';
import { useTranslation } from 'react-i18next';
import { Alert, Card, Space, Tag, Typography } from 'antd';
import type { MetaSchema } from '../types';

const { Text } = Typography;

export interface GraphNodeData {
  id: string;
  label: string;
  sub?: string;
}

export interface GraphEdgeData {
  id: string;
  source: string;
  target: string;
  label: string;
}

export interface GraphElements {
  nodes: { data: GraphNodeData }[];
  edges: { data: GraphEdgeData }[];
}

/** 从 schema 元数据生成图谱元素（node=对象类型，edge=链接类型，标注基数） */
export function buildGraphElements(meta: MetaSchema): GraphElements {
  const nodes = meta.objects.map((o) => ({
    data: {
      id: o.name,
      label: o.name,
      sub: o.description,
    } as GraphNodeData,
  }));
  const edges = meta.links.map((l) => ({
    data: {
      id: l.name,
      source: l.source_type,
      target: l.target_type,
      label: l.name + ' [' + l.cardinality + ']',
    } as GraphEdgeData,
  }));
  return { nodes, edges };
}

interface Props {
  meta: MetaSchema;
  height?: number;
}

export default function SchemaGraph({ meta, height = 560 }: Props) {
  const { t } = useTranslation();
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    const { nodes, edges } = buildGraphElements(meta);
    const cy: Core = cytoscape({
      container: containerRef.current,
      elements: { nodes, edges },
      style: [
        {
          selector: 'node',
          style: {
            'background-color': '#1677ff',
            'border-color': '#0958d9',
            'border-width': 1.5,
            label: 'data(label)',
            color: '#fff',
            'font-size': '12px',
            'text-valign': 'center',
            'text-halign': 'center',
            width: 'label',
            height: 'label',
            padding: '8px',
            shape: 'round-rectangle',
          },
        },
        {
          selector: 'edge',
          style: {
            width: 1.5,
            'line-color': '#8c8c8c',
            'target-arrow-color': '#8c8c8c',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            label: 'data(label)',
            'font-size': '10px',
            color: '#595959',
            'text-background-color': '#ffffff',
            'text-background-opacity': 0.9,
            'text-background-padding': '2px',
          },
        },
      ],
      layout: {
        name: 'cose',
        animate: false,
        padding: 30,
        nodeRepulsion: () => 9000,
        idealEdgeLength: () => 140,
      },
    });
    cyRef.current = cy;
    return () => {
      cy.destroy();
      cyRef.current = null;
    };
  }, [meta]);

  if (!meta.objects.length && !meta.links.length) {
    return <Alert type="info" message={t('graph.noData')} showIcon />;
  }

  return (
    <Card
      title={t('graph.title')}
      extra={
        <Space size={4}>
          <Tag color="blue">{t('graph.objectNode')}</Tag>
          <Tag color="default">{t('graph.linkEdge')}</Tag>
        </Space>
      }
    >
      <Text type="secondary" style={{ display: 'block', marginBottom: 12 }}>
        {t('graph.desc')}
      </Text>
      <div
        ref={containerRef}
        style={{ height, border: '1px solid #f0f0f0', borderRadius: 8 }}
        data-testid="schema-graph"
      />
    </Card>
  );
}