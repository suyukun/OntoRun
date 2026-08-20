// 语言切换 —— react-i18next，选择持久化到 localStorage（i18n/index.ts changeLanguage）
import { useTranslation } from 'react-i18next';
import { Select } from 'antd';
import { LANGUAGES, changeLanguage } from '../i18n';

export default function LanguageSwitcher() {
  const { i18n } = useTranslation();
  return (
    <Select
      data-testid="lang-switcher"
      value={i18n.language}
      style={{ width: 110 }}
      size="small"
      onChange={(v) => changeLanguage(v)}
      options={LANGUAGES.map((l) => ({ value: l.code, label: l.label }))}
    />
  );
}
