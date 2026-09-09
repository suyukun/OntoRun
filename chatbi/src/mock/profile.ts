import type { Profile } from '../types';

/**
 * 内置 mock profile（附录 C schema 的壳所需字段）。
 * 真实 profile 由后端 GET /api/profile 下发；后端未起时壳以此降级运行（页面带「mock 数据」标识）。
 */
export const MOCK_PROFILE: Profile = {
  name: 'fortune-registration',
  display: '财富广场 · 注册域',
  endpoint: '/api/chat',
  panels: ['decision_pipeline', 'path_badge', 'conclusion_basis', 'history'],
  examples: [
    '8月注册用户数是多少？',
    '8月按渠道的注册用户数？',
    '8月注册用户的男女比例是多少？',
    '9月注册用户数是多少？',
    '注册用户数是多少？',
    '8月的日活是多少？',
  ],
  path_labels: {
    hot: '热路径',
    cold_pushdown: '冷路径·明细下推',
    cold_adhoc: '冷路径·维表即席',
    rejected: '范围外拒答',
    blocked_param: '参数追问',
    unregistered: '未注册口径',
    validation_failed: '校验拦截',
  },
};

/** path 徽章文案兜底：真实 profile 缺 path_labels 时使用（§附录 C：文案由 profile 装配，此处仅为兜底） */
export const DEFAULT_PATH_LABELS = MOCK_PROFILE.path_labels;
