/* oxlint-disable react/only-export-components */
// 构建器共享组件：状态标签与枚举常量（状态值来自后端，展示文案走 i18n）
import { Tag } from 'antd';
import { useTranslation } from 'react-i18next';

export function StatusTag({ status }: { status: string }) {
  const { t } = useTranslation();
  const colorMap: Record<string, string> = {
    draft: 'default',
    reviewed: 'blue',
    published: 'green',
    approved: 'green',
    active: 'green',
    uploaded: 'cyan',
    archived: 'default',
  };
  const key = 'builder.' + status;
  const label = t(key).startsWith('builder.') ? status : t(key);
  return <Tag color={colorMap[status] || 'default'}>{label}</Tag>;
}

export const OBJECT_CATEGORIES = ['domain', 'artifact', 'conceptual'];
export const LINK_CATEGORIES = ['semantic', 'fk_inferred', 'structural'];
export const CARDINALITIES = ['1:1', '1:N', 'N:1', 'N:M'];