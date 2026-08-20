// i18n 初始化（react-i18next + i18next）
// 约定：zh-CN 全量文案；en-US 核心文案（导航/主要按钮/关键页面）。
// 默认语言 zh-CN（保持既有测试与演示中文）；语言选择存 localStorage。
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import zhCN from './locales/zh-CN.json';
import enUS from './locales/en-US.json';

export const LANGUAGES = [
  { code: 'zh-CN', label: '中文' },
  { code: 'en-US', label: 'English' },
] as const;

export const DEFAULT_LANGUAGE = 'zh-CN';
export const STORAGE_KEY = 'ontorun.lang';

export function getInitialLanguage(): string {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved && LANGUAGES.some((l) => l.code === saved)) return saved;
  } catch {
    // localStorage 不可用时回退默认语言
  }
  return DEFAULT_LANGUAGE;
}

export function changeLanguage(lng: string): void {
  try {
    localStorage.setItem(STORAGE_KEY, lng);
  } catch {
    // ignore
  }
  void i18n.changeLanguage(lng);
}

i18n.use(initReactI18next).init({
  resources: {
    'zh-CN': { translation: zhCN },
    'en-US': { translation: enUS },
  },
  lng: getInitialLanguage(),
  fallbackLng: DEFAULT_LANGUAGE,
  interpolation: { escapeValue: false },
});

export default i18n;
