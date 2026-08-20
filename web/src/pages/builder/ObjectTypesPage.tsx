// 对象类型管理（builder）：列表/新建/编辑/删除/审阅/发布 —— 全部走 /api/v1/builder
import { useCallback, useEffect, useMemo, useState } from 'react';
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
  Tag,
  Typography,
  message,
} from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import {
  createObjectType,
  deleteObjectType,
  listObjectTypes,
  publishObjectType,
  reviewObjectType,
  updateObjectType,
} from '../../apiBuilder';
import type { ObjectTypeRow, PropertySchema } from '../../builderTypes';
import { OBJECT_CATEGORIES, StatusTag } from '../../components/builderCommon';

const { Title } = Typography;

const DEFAULT_SCHEMA: PropertySchema = {
  type: 'object',
  properties: { id: { type: 'string', title: 'ID' } },
  required: ['id'],
};

function parseSchema(raw: string): PropertySchema {
  const obj = JSON.parse(raw) as PropertySchema;
  if (!obj || typeof obj !== 'object' || obj.type !== 'object' || !obj.properties || typeof obj.properties !== 'object') {
    throw new Error('type=object 且含 properties');
  }
  return obj;
}

export default function ObjectTypesPage() {
  const { t } = useTranslation();
  const [items, setItems] = useState<ObjectTypeRow[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [category, setCategory] = useState<string | undefined>();
  const [status, setStatus] = useState<string | undefined>();
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<ObjectTypeRow | null>(null);
  const [saving, setSaving] = useState(false);
  const [form] = Form.useForm();

  const load = useCallback(
    async (p: number, cat?: string, st?: string) => {
      setLoading(true);
      try {
        const data = await listObjectTypes({ category: cat, status: st, page: p, page_size: 20 });
        setItems(data.items);
        setTotal(data.total);
      } catch (err) {
        message.error(t('builder.fetchFailed', { msg: (err as Error).message }));
      } finally {
        setLoading(false);
      }
    },
    [t],
  );

  useEffect(() => {
    void load(page, category, status);
  }, [load, page, category, status]);

  const openCreate = () => {
    setEditing(null);
    form.setFieldsValue({
      name: '',
      name_cn: '',
      description: '',
      category: 'domain',
      property_schema: JSON.stringify(DEFAULT_SCHEMA, null, 2),
    });
    setModalOpen(true);
  };

  const openEdit = (row: ObjectTypeRow) => {
    setEditing(row);
    form.setFieldsValue({
      name: row.name,
      name_cn: row.name_cn,
      description: row.description,
      category: row.category,
      property_schema: JSON.stringify(row.property_schema, null, 2),
    });
    setModalOpen(true);
  };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      const property_schema = parseSchema(values.property_schema);
      const body = {
        name: values.name.trim(),
        name_cn: values.name_cn || '',
        description: values.description || '',
        category: values.category,
        property_schema,
      };
      setSaving(true);
      if (editing) {
        await updateObjectType(editing.id, body);
      } else {
        await createObjectType({ ...body, ontology_id: 'default' });
      }
      message.success(t('common.saveSuccess'));
      setModalOpen(false);
      void load(page, category, status);
    } catch (err) {
      if ((err as Error).message?.includes('type=object')) {
        message.error(t('builder.schemaInvalid'));
      } else {
        message.error(t('builder.saveFailed', { msg: (err as Error).message }));
      }
    } finally {
      setSaving(false);
    }
  };

  const doTransition = async (row: ObjectTypeRow, action: 'review' | 'publish') => {
    const key = action === 'review' ? 'reviewConfirm' : 'publishConfirm';
    Modal.confirm({
      title: t('builder.' + key, { name: row.name }),
      onOk: async () => {
        try {
          if (action === 'review') await reviewObjectType(row.id);
          else await publishObjectType(row.id);
          message.success(t('common.saveSuccess'));
          void load(page, category, status);
        } catch (err) {
          message.error(t('builder.transitionFailed', { msg: (err as Error).message }));
        }
      },
    });
  };

  const doDelete = (row: ObjectTypeRow) => {
    Modal.confirm({
      title: t('builder.deleteConfirm', { name: row.name }),
      okButtonProps: { danger: true },
      onOk: async () => {
        try {
          await deleteObjectType(row.id);
          message.success(t('common.deleteSuccess'));
          void load(page, category, status);
        } catch (err) {
          message.error(t('builder.deleteFailed', { msg: (err as Error).message }));
        }
      },
    });
  };

  const schemaSummary = (schema: PropertySchema): string => {
    const props = schema.properties || {};
    const names = Object.keys(props);
    if (!names.length) return '-';
    const required = schema.required || [];
    return names
      .slice(0, 8)
      .map((k) => k + (required.includes(k) ? '*' : ''))
      .join(', ') + (names.length > 8 ? ' …' : '');
  };

  const columns = useMemo(
    () => [
      { title: t('common.name'), dataIndex: 'name', key: 'name', render: (v: string, r: ObjectTypeRow) => (
        <Space size={4} direction="vertical" style={{ gap: 0 }}>
          <span>{v}</span>
          {r.name_cn && <span style={{ color: '#8c8c8c', fontSize: 12 }}>{r.name_cn}</span>}
        </Space>
      )},
      { title: t('common.description'), dataIndex: 'description', key: 'description', ellipsis: true },
      { title: t('common.category'), dataIndex: 'category', key: 'category', render: (v: string) => <Tag>{v}</Tag> },
      { title: t('common.status'), dataIndex: 'status', key: 'status', render: (v: string) => <StatusTag status={v} /> },
      { title: t('builder.propertySchema'), key: 'schema', render: (_: unknown, r: ObjectTypeRow) => (
        <span style={{ fontSize: 12, color: '#595959' }}>{schemaSummary(r.property_schema)}</span>
      )},
      { title: t('common.updatedAt'), dataIndex: 'updated_at', key: 'updated_at', width: 170 },
      {
        title: t('common.operations'),
        key: 'ops',
        width: 260,
        render: (_: unknown, r: ObjectTypeRow) => (
          <Space size={4} wrap>
            <Button size="small" onClick={() => openEdit(r)}>{t('common.edit')}</Button>
            {r.status === 'draft' && (
              <Button size="small" onClick={() => doTransition(r, 'review')}>{t('common.review')}</Button>
            )}
            {r.status === 'reviewed' && (
              <Button size="small" type="primary" ghost onClick={() => doTransition(r, 'publish')}>{t('common.publish')}</Button>
            )}
            <Button size="small" danger disabled={r.status !== 'draft'} onClick={() => doDelete(r)}>
              {t('common.delete')}
            </Button>
          </Space>
        ),
      },
    ],
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [t],
  );

  return (
    <Card
      title={<Title level={4} style={{ margin: 0 }}>{t('builder.objectTypes')}</Title>}
      extra={<Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>{t('common.create')}</Button>}
    >
      <Space style={{ marginBottom: 12 }}>
        <Select
          allowClear
          placeholder={t('builder.categoryFilter')}
          style={{ width: 160 }}
          value={category}
          onChange={setCategory}
          options={OBJECT_CATEGORIES.map((c) => ({ value: c, label: c }))}
        />
        <Select
          allowClear
          placeholder={t('builder.statusFilter')}
          style={{ width: 160 }}
          value={status}
          onChange={setStatus}
          options={['draft', 'reviewed', 'published'].map((s) => ({ value: s, label: s }))}
        />
      </Space>
      <Table
        rowKey="id"
        columns={columns}
        dataSource={items}
        loading={loading}
        size="small"
        pagination={{
          current: page,
          pageSize: 20,
          total,
          onChange: setPage,
          showTotal: (tot) => t('common.total', { count: tot }),
        }}
      />
      <Modal
        title={editing ? t('builder.editObjectType') : t('builder.createObjectType')}
        open={modalOpen}
        onOk={() => void handleSave()}
        onCancel={() => setModalOpen(false)}
        confirmLoading={saving}
        width={720}
        destroyOnHidden
      >
        <Form form={form} layout="vertical">
          <Space style={{ display: 'flex' }} align="start">
            <Form.Item name="name" label={t('common.name')} rules={[{ required: true, message: t('actions.required', { label: t('common.name') }) }]} style={{ width: 200 }}>
              <Input />
            </Form.Item>
            <Form.Item name="name_cn" label={t('common.nameCn')} style={{ width: 200 }}>
              <Input />
            </Form.Item>
            <Form.Item name="category" label={t('common.category')} rules={[{ required: true }]} style={{ width: 180 }}>
              <Select options={OBJECT_CATEGORIES.map((c) => ({ value: c, label: c }))} />
            </Form.Item>
          </Space>
          <Form.Item name="description" label={t('common.description')}>
            <Input.TextArea rows={2} />
          </Form.Item>
          <Form.Item
            name="property_schema"
            label={t('builder.propertySchema')}
            rules={[{ required: true, message: t('builder.schemaInvalid') }]}
            extra={t('builder.schemaHint')}
          >
            <Input.TextArea rows={12} style={{ fontFamily: 'monospace', fontSize: 12 }} />
          </Form.Item>
          <Alert type="info" showIcon message="JSON Schema（properties/required/enum/format 驱动列表列与表单控件）" />
        </Form>
      </Modal>
    </Card>
  );
}