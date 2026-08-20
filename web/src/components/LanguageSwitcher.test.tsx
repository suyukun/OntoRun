/// <reference types="vitest/globals" />
// LanguageSwitcher 测试：切换语言入口渲染 + 选择写入 localStorage
import { afterEach, describe, expect, it } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import LanguageSwitcher from './LanguageSwitcher';
import i18n, { DEFAULT_LANGUAGE } from '../i18n';

afterEach(async () => {
  localStorage.clear();
  await i18n.changeLanguage(DEFAULT_LANGUAGE);
});

describe('LanguageSwitcher', () => {
  it('渲染语言切换下拉（含 zh/en 选项）', async () => {
    const user = userEvent.setup();
    render(<LanguageSwitcher />);
    const sel = screen.getByTestId('lang-switcher');
    expect(sel).toBeTruthy();
    await user.click(sel);
    await waitFor(() => {
      expect(screen.getAllByText('English').length).toBeGreaterThan(0);
    });
  });

  it('选择 English 后写入 localStorage 且文案切换', async () => {
    const user = userEvent.setup();
    render(<LanguageSwitcher />);
    await user.click(screen.getByTestId('lang-switcher'));
    const enOption = (await screen.findAllByText('English'))[0];
    await user.click(enOption);
    await waitFor(() => {
      expect(localStorage.getItem('ontorun.lang')).toBe('en-US');
      expect(i18n.t('nav.browse')).toBe('Browse Data');
    });
  });
});
