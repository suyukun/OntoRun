// 对象列表组件 —— 由对象类型 schema 自动生成列，不硬编码
import { useEffect, useState } from 'react';
import { Card, Select, Table, Tag, Typography, message } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { fetchObjectList } from '../api';
import type { ObjectItem, ObjectTypeMeta } from '../types';

const { Title } = Typography;

interface Props {
  meta: ObjectTypeMeta;
  onSelectObject: (type: string, pk: string) => void;
}

/** 从 property schema 推断列类型（用于 Tag 渲染与排序） */
function inferColumnType(prop: import('../types').PropertyMeta): 'text' | 'enum' | 'number' | 'date' {
  if (prop.enum) return 'enum';
  if (prop.type === 'number' || prop.type === 'integer') return 'number';
  if (prop.format === 'date-time' || prop.format === 'date') return 'date';
  return 'text';
}

export default function ObjectList({ meta, onSelectObject }: Props) {
  const [items, setItems] = useState<ObjectItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const pageSize = 20;

  const load = async (p: number) => {
    setLoading(true);
    try {
      const data = await fetchObjectList(meta.api_name, {
        page: String(p),
        page_size: String(pageSize),
      });
      setItems(data.items);
      setTotal(data.total);
    } catch (err) {
      message.error('加载失败: ' + (err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(page); }, [meta.api_name, page]);

  // 由 schema 自动生成列
  const columns: ColumnsType<ObjectItem> = Object.entries(meta.properties).map(([key, prop]) => {
    const colType = inferColumnType(prop);
    const col: ColumnsType<ObjectItem>[number] = {
      title: prop.title || key,
      dataIndex: ['properties', key],
      key,
      sorter: colType === 'number' ? (a, b) => {
        const va = Number(a.properties[key]);
        const vb = Number(b.properties[key]);
        return va - vb;
      } : undefined,
      render: (val: unknown) => {
        if (val === null || val === undefined) return <Tag>空</Tag>;
        if (colType === 'enum') {
          const colors = ['blue', 'green', 'orange', 'purple', 'cyan', 'magenta'];
          const idx = (prop.enum || []).indexOf(String(val));
          return <Tag color={colors[idx % colors.length]}>{String(val)}</Tag>;
        }
        if (colType === 'date') {
          return new Date(String(val)).toLocaleString('zh-CN');
        }
        return String(val);
      },
    };
    return col;
  });

  return (
    <Card title={meta.description + ' (' + meta.name + ')'}>
      <Table<ObjectItem>
        columns={columns}
        dataSource={items}
        rowKey={(r) => r.pk}
        loading={loading}
        size="small"
        pagination={{
          current: page,
          pageSize,
          total,
          onChange: (p) => setPage(p),
          showTotal: (t) => '共 ' + t + ' 条',
        }}
        onRow={(record) => ({
          onClick: () => onSelectObject(meta.api_name, record.pk),
          style: { cursor: 'pointer' },
        })}
      />
    </Card>
  );
}
