// 动作表单组件 —— 由动作参数 schema 自动生成表单，不硬编码
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Button,
  Card,
  Form,
  Input,
  InputNumber,
  Modal,
  Select,
  Space,
  Tag,
  Typography,
  message,
  Alert,
} from 'antd';
import { submitAction } from '../api';
import type { ActionMeta, PropertyMeta } from '../types';

const { Paragraph } = Typography;

interface Props {
  action: ActionMeta;
  onDone: () => void;
}

/** 根据 property schema 生成表单控件 */
function fieldFromSchema(prop: PropertyMeta, key: string, t: (k: string, o?: Record<string, unknown>) => string) {
  const label = prop.title || key;
  const desc = prop.description;

  // 枚举 → Select
  if (prop.enum) {
    return (
      <Form.Item
        key={key}
        name={key}
        label={label}
        rules={[{ required: prop.enum.length > 0, message: t('actions.choose', { label }) }]}
        extra={desc}
      >
        <Select allowClear placeholder={t('actions.choose', { label })}>
          {prop.enum.map((v) => (
            <Select.Option key={v} value={v}>
              {v}
            </Select.Option>
          ))}
        </Select>
      </Form.Item>
    );
  }

  // 数值 → InputNumber
  if (prop.type === 'integer' || prop.type === 'number') {
    return (
      <Form.Item key={key} name={key} label={label} extra={desc}>
        <InputNumber style={{ width: '100%' }} placeholder={label} />
      </Form.Item>
    );
  }

  // 日期 → Input (简化)
  if (prop.format === 'date-time' || prop.format === 'date') {
    return (
      <Form.Item key={key} name={key} label={label} extra={desc}>
        <Input placeholder="YYYY-MM-DD HH:mm:ss" />
      </Form.Item>
    );
  }

  // 默认 → Input
  return (
    <Form.Item key={key} name={key} label={label} extra={desc}>
      <Input placeholder={label} />
    </Form.Item>
  );
}

export default function ActionForm({ action, onDone }: Props) {
  const { t } = useTranslation();
  const [form] = Form.useForm();
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<{ outcome: string; msg: string } | null>(null);

  const requiredFields = action.params_schema.required || [];

  const doSubmit = async (values: Record<string, unknown>) => {
    setSubmitting(true);
    setResult(null);
    try {
      const res = await submitAction(action.name, values);
      if (res.outcome === 'applied') {
        setResult({
          outcome: 'success',
          msg: t('actions.success', { id: (res.data as Record<string, unknown>)?.audit_id }),
        });
        form.resetFields();
        onDone();
      } else {
        setResult({ outcome: 'warning', msg: t('actions.rejected', { msg: res.error?.message || res.outcome }) });
      }
    } catch (err) {
      message.error(t('actions.submitFailed', { msg: (err as Error).message }));
    } finally {
      setSubmitting(false);
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      if (action.high_risk) {
        Modal.confirm({
          title: t('actions.confirmHighRisk'),
          content: t('actions.highRiskTip'),
          okText: t('actions.confirmExecute'),
          cancelText: t('actions.cancelExecute'),
          onOk: () => doSubmit(values),
        });
        return;
      }
      await doSubmit(values);
    } catch (err) {
      if (!(err as Error).message) return; // 表单校验失败，不提示
      message.error(t('actions.submitFailed', { msg: (err as Error).message }));
    }
  };

  return (
    <Card
      title={
        <Space>
          <span>{action.name}</span>
          {action.high_risk && <Tag color="red">{t('actions.highRisk')}</Tag>}
        </Space>
      }
    >
      <Paragraph type="secondary">{action.description}</Paragraph>

      {action.preconditions.length > 0 && (
        <Alert
          type="info"
          message={t('actions.preconditions')}
          description={
            <ul style={{ margin: 0, paddingLeft: 20 }}>
              {action.preconditions.map((pc) => (
                <li key={pc.error_code}>{pc.summary} ({pc.error_code})</li>
              ))}
            </ul>
          }
          style={{ marginBottom: 16 }}
        />
      )}

      {result && (
        <Alert
          type={result.outcome === 'success' ? 'success' : 'warning'}
          message={result.msg}
          closable
          style={{ marginBottom: 16 }}
        />
      )}

      <Form form={form} layout="vertical" size="small">
        {Object.entries(action.params_schema.properties).map(([key, prop]) => {
          const field = fieldFromSchema(prop, key, t);
          if (requiredFields.includes(key)) {
            return (
              <Form.Item key={key} noStyle>
                {field}
              </Form.Item>
            );
          }
          return field;
        })}
      </Form>

      <Space style={{ marginTop: 16 }}>
        <Button type="primary" loading={submitting} onClick={() => void handleSubmit()}>
          {t('actions.execute')}
        </Button>
        <Button onClick={() => form.resetFields()}>{t('common.reset')}</Button>
      </Space>
    </Card>
  );
}
