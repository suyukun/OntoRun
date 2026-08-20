// i18n 测试：默认 zh-CN 全量、切换 en-US 核心生效、localStorage 持久化
import { afterEach, describe, expect, it } from 'vitest';
import i18n, { changeLanguage, DEFAULT_LANGUAGE, LANGUAGES } from './index';

afterEach(async () => {
  localStorage.clear();
  await i18n.changeLanguage(DEFAULT_LANGUAGE);
});

describe('i18n', () => {
  it('默认语言为 zh-CN 且关键文案齐全（zh 全量）', () => {
    expect(i18n.language).toBe('zh-CN');
    expect(i18n.t('nav.browse')).toBe('数据浏览');
    expect(i18n.t('nav.builder')).toBe('本体构建器');
    expect(i18n.t('actions.execute')).toBe('执行动作');
    expect(i18n.t('actions.confirmHighRisk')).toBe('确认执行高风险动作');
    expect(i18n.t('graph.title')).toBe('本体图谱');
    expect(i18n.t('pipeline.runPipeline')).toBe('触发运行');
  });

  it('切换到 en-US 后核心文案生效（en 核心）', async () => {
    await i18n.changeLanguage('en-US');
    expect(i18n.language).toBe('en-US');
    expect(i18n.t('nav.browse')).toBe('Browse Data');
    expect(i18n.t('nav.builder')).toBe('Ontology Builder');
    expect(i18n.t('nav.objectTypes')).toBe('Object Types');
    expect(i18n.t('actions.execute')).toBe('Execute');
    expect(i18n.t('common.create')).toBe('Create');
    expect(i18n.t('common.delete')).toBe('Delete');
    expect(i18n.t('graph.title')).toBe('Ontology Graph');
    expect(i18n.t('pipeline.runPipeline')).toBe('Run');
  });

  it('语言清单包含 zh-CN 与 en-US', () => {
    expect(LANGUAGES.map((l) => l.code)).toEqual(['zh-CN', 'en-US']);
  });

  it('changeLanguage 写入 localStorage 且可复原', async () => {
    changeLanguage('en-US');
    expect(localStorage.getItem('ontorun.lang')).toBe('en-US');
    await i18n.changeLanguage(DEFAULT_LANGUAGE);
    expect(i18n.t('nav.browse')).toBe('数据浏览');
  });
});
