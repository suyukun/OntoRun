import { afterEach, describe, expect, it } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import { MessageCard } from '../components/MessageCard';
import type { ChatMessage, FinalResult } from '../types';

/** final.data_profile="mock" 仿真数据徽标：有字段 → 卡头元信息行显示暖色徽标；无字段（旧会话兼容）→ 完全不渲染。 */

function baseResult(): FinalResult {
  return {
    request_id: 'REQ-TEST-MOCKBADGE',
    started_at: '2026-09-09T13:45:00',
    question: '8月注册用户数是多少？',
    rule: 'REG_TOTAL',
    path: 'hot',
    answer: '2026-08 月注册 2,893 人。',
    sql: 'SELECT 1',
    rows: [{ total: 2893 }],
    tables: [{ name: 'dws_reg_daily_df', layer: 'DWS' }],
    steps: [],
  };
}

function doneMsg(result: FinalResult): ChatMessage {
  return {
    id: 1,
    role: 'ai',
    text: '8月注册用户数是多少？',
    steps: [],
    streamedText: '',
    result,
    error: null,
    phase: 'done',
  };
}

const noop = () => {};

function renderCard(result: FinalResult) {
  return render(
    <MessageCard msg={doneMsg(result)} pathLabels={{}} onRetry={noop} onFollowUp={noop} />,
  );
}

// vitest globals 关闭时 testing-library 不自动 cleanup，DOM 会跨用例堆叠
afterEach(() => cleanup());

describe('仿真数据徽标（final.data_profile）', () => {
  it('data_profile="mock" → 卡头元信息行（think-right）渲染徽标', () => {
    const { container } = renderCard({ ...baseResult(), data_profile: 'mock' });
    const badge = container.querySelector('.think-right .badge-mock');
    expect(badge).toBeTruthy();
    expect(badge?.textContent).toBe('仿真数据');
  });

  it('final 无该字段（旧会话兼容）→ 完全不渲染', () => {
    renderCard(baseResult());
    expect(screen.queryByText('仿真数据')).toBeNull();
    expect(document.querySelector('.badge-mock')).toBeNull();
  });

  it('非 mock 值（如 real）→ 不渲染', () => {
    renderCard({ ...baseResult(), data_profile: 'real' });
    expect(screen.queryByText('仿真数据')).toBeNull();
  });
});
