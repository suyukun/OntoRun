// 链接类型管理（builder）：列表/新建/编辑/删除/审阅/发布
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Button, Card, Form, Input, Modal, Select, Space, Table, Typography, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import {
  createLinkType,
  deleteLinkType,
  listLinkTypes,
  listObjectTypes,
  publishLinkType,
  reviewLinkType,
  updateLinkType,
} from '../../apiBuilder';
import type { LinkTypeRow, ObjectTypeRow } from '../../builderTypes';
import { CARDINALITIES, LINK_CATEGORIES, StatusTag } from '../../components/builderCommon';

const { Title } = Typography;

export default function LinkTypesPage() {
  const { t } = useTranslation();
  const [items, setItems] = useState<LinkTypeRow[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState<string | undefined>();
  const [objectTypes, setObjectTypes] = useState<ObjectTypeRow[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<LinkTypeRow | null>(null);
  const [saving, setSaving] = useState(false);
  const [form] = Form.useForm();

  const load = useCallback(
    async (p: number, st?: string) => {
      setLoading(true);
      try {
        const data = await listLinkTypes({ status: st, page: p, page_size: 20 });
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
    void load(page, status);
    void listObjectTypes({ page_size: 200 }).then((d) => setObjectTypes(d.items)).catch(() => undefined);
  }, [load, page, status]);

  const typeOptions = useMemo(
    () => objectTypes.map((o) => ({ value: o.id, label: o.name + ' (' + o.id + ')' })),
    [objectTypes],
  );

  const typeName = (id: string) => {
    const hit = objectTypes.find((o) => o.id === id || o.name === id);
    return hit ? hit.name + (hit.id !== id ? ' (' + hit.id + ')' : '') : id;
  };

  const openCreate = () => {
    setEditing(null);
    form.setFieldsValue({
      name: '',
      semantic_name: '',
      category: 'semantic',
      source_type_id: undefined,
      target_type_id: undefined,
      cardinality: 'N:1',
      fk_field: '',
    });
    setModalOpen(true);
  };

  const openEdit = (row: LinkTypeRow) => {
    setEditing(row);
    form.setFieldsValue({
      name: row.name,
      semantic_name: row.semantic_name,
      category: row.category,
      source_type_id: row.source_type_id,
      target_type_id: row.target_type_id,
      cardinality: row.cardinality,
      fk_field: row.fk_field,
    });
    setModalOpen(true);
  };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      setSaving(true);
      const body = {
        name: values.name.trim(),
        semantic_name: values.semantic_name || '',
        category: values.category,
        source_type_id: values.source_type_id,
        target_type_id: values.target_type_id,
        cardinality: values.cardinality,
        fk_field: values.fk_field || '',
      };
      if (editing) {
        await updateLinkType(editing.id, body);
      } else {
        await createLinkType({ ...body, ontology_id: 'default' });
      }
      message.success(t('common.saveSuccess'));
      setModalOpen(false);
      void load(page, status);
    } catch (err) {
      message.error(t('builder.saveFailed', { msg: (err as Error).message }));
    } finally {
      setSaving(false);
    }
  };

  const doTransition = async (row: LinkTypeRow, action: 'review' | 'publish') => {
    Modal.confirm({
      title: t('builder.' + (action === 'review' ? 'reviewConfirm' : 'publishConfirm'), { name: row.name }),
      onOk: async () => {
        try {
          if (action === 'review') await reviewLinkType(row.id);
          else await publishLinkType(row.id);
          message.success(t('common.saveSuccess'));
          void load(page, status);
        } catch (err) {
          message.error(t('builder.transitionFailed', { msg: (err as Error).message }));
        }
      },
    });
  };

  const doDelete = (row: LinkTypeRow) => {
    Modal.confirm({
      title: t('builder.deleteConfirm', { name: row.name }),
      okButtonProps: { danger: true },
      onOk: async () => {
        try {
          await deleteLinkType(row.id);
          message.success(t('common.deleteSuccess'));
          void load(page, status);
        } catch (err) {
          message.error(t('builder.deleteFailed', { msg: (err as Error).message }));
        }
      },
    });
  };

  const columns = useMemo(
    () => [
      { title: t('common.name'), dataIndex: 'name', key: 'name' },
      { title: t('builder.semanticName'), dataIndex: 'semantic_name', key: 'semantic_name' },
      {
        title: t('builder.sourceType'),
        dataIndex: 'source_type_id',
        key: 'source_type_id',
        render: (v: string) => typeName(v),
      },
      {
        title: t('builder.targetType'),
        dataIndex: 'target_type_id',
        key: 'target_type_id',
        render: (v: string) => typeName(v),
      },
      { title: t('builder.cardinality'), dataIndex: 'cardinality', key: 'cardinality' },
      { title: t('builder.fkField'), dataIndex: 'fk_field', key: 'fk_field' },
      { title: t('common.status'), dataIndex: 'status', key: 'status', render: (v: string) => <StatusTag status={v} /> },
      {
        title: t('common.operations'),
        key: 'ops',
        width: 260,
        render: (_: unknown, r: LinkTypeRow) => (
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
    [t, objectTypes],
  );

  return (
    <Card
      title={<Title level={4} style={{ margin: 0 }}>{t('builder.linkTypes')}</Title>}
      extra={<Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>{t('common.create')}</Button>}
    >
      <Space style={{ marginBottom: 12 }}>
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
        title={editing ? t('builder.editLinkType') : t('builder.createLinkType')}
        open={modalOpen}
        onOk={() => void handleSave()}
        onCancel={() => setModalOpen(false)}
        confirmLoading={saving}
        width={640}
        destroyOnHidden
      >
        <Form form={form} layout="vertical">
          <Space style={{ display: 'flex' }} align="start">
            <Form.Item name="name" label={t('common.name')} rules={[{ required: true, message: t('actions.required', { label: t('common.name') }) }]} style={{ width: 220 }}>
              <Input placeholder="order.customer" />
            </Form.Item>
            <Form.Item name="semantic_name" label={t('builder.semanticName')} style={{ width: 220 }}>
              <Input />
            </Form.Item>
            <Form.Item name="category" label={t('common.category')} rules={[{ required: true }]} style={{ width: 160 }}>
              <Select options={LINK_CATEGORIES.map((c) => ({ value: c, label: c }))} />
            </Form.Item>
          </Space>
          <Space style={{ display: 'flex' }} align="start">
            <Form.Item name="source_type_id" label={t('builder.sourceType')} rules={[{ required: true }]} style={{ width: 240 }}>
              <Select options={typeOptions} showSearch optionFilterProp="label" />
            </Form.Item>
            <Form.Item name="target_type_id" label={t('builder.targetType')} rules={[{ required: true }]} style={{ width: 240 }}>
              <Select options={typeOptions} showSearch optionFilterProp="label" />
            </Form.Item>
          </Space>
          <Space style={{ display: 'flex' }} align="start">
            <Form.Item name="cardinality" label={t('builder.cardinality')} rules={[{ required: true }]} style={{ width: 160 }}>
              <Select options={CARDINALITIES.map((c) => ({ value: c, label: c }))} />
            </Form.Item>
            <Form.Item name="fk_field" label={t('builder.fkField')} style={{ width: 240 }}>
              <Input />
            </Form.Item>
          </Space>
        </Form>
      </Modal>
    </Card>
  );
}
