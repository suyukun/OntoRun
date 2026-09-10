import type { ChatEvent, FinalResult, StepInfo, TableRef } from '../types';

/**
 * mock 数据模式：内置 step/token/final 事件序列（格式对齐附录 A / demo iter_query）。
 * 关键字 → 场景映射见 pickScenario；README 有完整对照表。
 */

export type Scenario =
  | 'hot_success'
  | 'cold_pushdown_success'
  | 'cold_adhoc_success'
  | 'success_degraded'
  | 'empty_result'
  | 'ask_param'
  | 'out_of_range'
  | 'rejected'
  | 'unregistered'
  | 'validation_failed'
  /** 传输层两态（无 final 帧）：服务异常 error 帧 / 断流中断——八状态 UI 自查用 */
  | 'service_error'
  | 'interrupted_stream';

/** 产生 FinalResult 的数据场景（service_error / interrupted_stream 走 error 帧或无 final 收尾） */
type DataScenario = Exclude<Scenario, 'service_error' | 'interrupted_stream'>;

const SUCCESS_PATHS = ['hot', 'cold_pushdown', 'cold_adhoc'];

/** mock 模式关键字 → 场景（联调后由真实后端取代；此处让八状态在无后端时可独立演示） */
export function pickScenario(question: string): Scenario {
  if (/服务异常|停服|宕机/.test(question)) return 'service_error';
  if (/断流|断网|断开/.test(question)) return 'interrupted_stream';
  if (/活跃|活动|日活|抽奖|转化/.test(question)) return 'rejected';
  if (/9月|去年|2025/.test(question)) return 'out_of_range';
  if (/凌晨/.test(question)) return 'empty_result';
  if (/校验/.test(question)) return 'validation_failed';
  if (/降级/.test(question)) return 'success_degraded';
  if (/渠道/.test(question)) return 'cold_pushdown_success';
  if (/男女|性别/.test(question)) return 'cold_adhoc_success';
  if (/注册|总数|用户/.test(question)) {
    return /8月|7月|八月|七月/.test(question) ? 'hot_success' : 'ask_param';
  }
  return 'unregistered';
}

function st(n: number, title: string, status: StepInfo['status'], detail: string, extra: Pick<StepInfo, 'sql' | 'ms'> = {}): StepInfo {
  return { n, title, status, detail, ...extra };
}

interface Spec {
  path: string;
  rule: string | null;
  answer: string;
  sql: string | null;
  rows: Record<string, unknown>[];
  tables: TableRef[];
  steps: StepInfo[];
  block_reason?: FinalResult['block_reason'];
  degraded?: boolean;
  /** D7 viz 契约：与 rules.py 规则注册的 viz 字段一致（REG_TOTAL=kpi、REG_BY_CHANNEL=bar、GENDER_RATIO=pie） */
  viz?: FinalResult['viz'];
}

const BOUNDARY = '2026-07-01 ~ 2026-08-31';
const SQL_TOTAL = "SELECT COALESCE(SUM(cnt),0) AS total FROM dws_reg_daily_df WHERE data_dt BETWEEN '2026-08-01' AND '2026-08-31'";
const SQL_CHANNEL = "SELECT ch.chnl_nm AS channel, COUNT(DISTINCT r.usr_id) AS cnt FROM dwd_tr_rgst_df r JOIN dim_ch_chl_df ch ON ch.chnl_id = r.rgst_chnl_id WHERE r.data_dt BETWEEN '2026-08-01' AND '2026-08-31' GROUP BY 1 ORDER BY 2 DESC";

function routeStep(rid: string, ok: boolean): StepInfo {
  return st(1, '意图路由', ok ? 'ok' : 'fail',
    '选定规则 = ' + rid + '（mock 路由 · 模拟 DeepSeek 286ms · 原始输出: {"rule_id":"' + rid + '","params":{"start":"2026-08-01","end":"2026-08-31"}}）');
}

const CALIBER_TOTAL = 'SUM(去重 usr_id)；含子公司同步注册；口径裁决号 2026-09-08-J1';

function buildSpec(sc: DataScenario, rejectKw?: string): Spec {
  switch (sc) {
    case 'hot_success': {
      const answer = '2026-08 月注册 2,893 人。';
      return {
        path: 'hot', rule: 'REG_TOTAL', answer, sql: SQL_TOTAL, viz: 'kpi',
        rows: [{ total: 2893 }], tables: [{ name: 'dws_reg_daily_df', layer: 'DWS' }],
        steps: [
          routeStep('REG_TOTAL', true),
          st(2, '口径声明', 'ok', CALIBER_TOTAL),
          st(3, '参数抽取+校验', 'ok', '{"start":"2026-08-01","end":"2026-08-31"} ✓（关键词回退抽取）'),
          st(4, 'SQL 编译', 'ok', '按命中规则的模板编译，参数已绑定', { sql: SQL_TOTAL }),
          st(5, '下推执行', 'ok', 'sqlite → 1 行，2.4ms', { ms: 2.4 }),
          st(6, '结果校验', 'ok', '✓ 列结构与规则声明一致'),
          st(7, '回答', 'ok', answer),
        ],
      };
    }
    case 'cold_pushdown_success': {
      const answer = '共 2,893 人，TOP3：APP 1,240、小程序 987、官网 456。';
      return {
        path: 'cold_pushdown', rule: 'REG_BY_CHANNEL', answer, sql: SQL_CHANNEL, viz: 'bar',
        rows: [
          { channel: 'APP', cnt: 1240 },
          { channel: '小程序', cnt: 987 },
          { channel: '官网', cnt: 456 },
          { channel: '线下门店', cnt: 210 },
        ],
        tables: [{ name: 'dwd_tr_rgst_df', layer: 'DWD' }, { name: 'dim_ch_chl_df', layer: 'DIM' }],
        steps: [
          routeStep('REG_BY_CHANNEL', true),
          st(2, '口径声明', 'ok', '明细按 rgst_chnl_id 聚合去重；渠道名 JOIN 渠道维表；与 REG_TOTAL 必须同源一致'),
          st(3, '参数抽取+校验', 'ok', '{"start":"2026-08-01","end":"2026-08-31"} ✓（关键词回退抽取）'),
          st(4, 'SQL 编译', 'ok', '按命中规则的模板编译，参数已绑定', { sql: SQL_CHANNEL }),
          st(5, '下推执行', 'ok', 'sqlite → 4 行，6.8ms', { ms: 6.8 }),
          st(6, '结果校验', 'ok', '✓ 列结构与规则声明一致'),
          st(6, '结果校验', 'ok', '✓ 同源交叉：分渠道合计 2,893 = 热路径总数 2,893'),
          st(7, '回答', 'ok', answer),
        ],
      };
    }
    case 'cold_adhoc_success': {
      const answer = '男 1,523（52.7%）、女 1,310（45.3%）、未知 60（2.1%）。合计 2,893 人。（明细级即席计算（未预聚合）：结果为即时快照，非月报口径）';
      return {
        path: 'cold_adhoc', rule: 'GENDER_RATIO', viz: 'pie',
        answer,
        sql: "SELECT CASE usr_sex WHEN 1 THEN '男' WHEN 2 THEN '女' ELSE '未知' END AS gender, COUNT(DISTINCT u.usr_id) AS cnt FROM dim_cu_usr_info_df u WHERE u.rgst_dt BETWEEN '2026-08-01' AND '2026-08-31' GROUP BY 1 ORDER BY 2 DESC",
        rows: [
          { gender: '男', cnt: 1523 },
          { gender: '女', cnt: 1310 },
          { gender: '未知', cnt: 60 },
        ],
        tables: [{ name: 'dim_cu_usr_info_df', layer: 'DIM' }],
        steps: [
          routeStep('GENDER_RATIO', true),
          st(2, '口径声明', 'ok', '维表 usr_sex 属性分布；明细级即席计算，回答必须标注'),
          st(3, '参数抽取+校验', 'ok', '{"start":"2026-08-01","end":"2026-08-31"} ✓（关键词回退抽取）'),
          st(4, 'SQL 编译', 'ok', '按命中规则的模板编译，参数已绑定'),
          st(5, '下推执行', 'ok', 'sqlite → 3 行，9.1ms', { ms: 9.1 }),
          st(6, '结果校验', 'ok', '✓ 列结构与规则声明一致'),
          st(6, '结果校验', 'ok', '✓ 冷路径免责声明已附加'),
          st(7, '回答', 'ok', answer),
        ],
      };
    }
    case 'success_degraded': {
      const base = buildSpec('hot_success');
      return { ...base, degraded: true };
    }
    case 'empty_result': {
      const base = buildSpec('hot_success');
      return { ...base, rows: [], answer: '该范围无数据。' };
    }
    case 'ask_param': {
      const answer = '请问您要查询哪个月份？';
      return {
        path: 'blocked_param', rule: 'REG_TOTAL', answer, sql: null, rows: [], tables: [],
        block_reason: 'missing_param',
        steps: [
          routeStep('REG_TOTAL', true),
          st(2, '口径声明', 'ok', CALIBER_TOTAL),
          st(3, '参数校验', 'fail', '时间范围缺失 → 追问用户，不猜测'),
          st(7, '回答', 'blocked', answer),
        ],
      };
    }
    case 'out_of_range': {
      const answer = '当前样本数据仅覆盖 ' + BOUNDARY + '，该时间段无数据。';
      return {
        path: 'blocked_param', rule: 'REG_TOTAL', answer, sql: null, rows: [], tables: [],
        block_reason: 'out_of_range',
        steps: [
          routeStep('REG_TOTAL', true),
          st(2, '口径声明', 'ok', CALIBER_TOTAL),
          st(3, '参数校验', 'fail', '时间范围超出样本数据边界 {"min":"2026-07-01","max":"2026-08-31"} → 如实说明，不硬答'),
          st(7, '回答', 'blocked', answer),
        ],
      };
    }
    case 'rejected': {
      // 与后端 build_reject_answer 同思路：命中词 + 已就绪口径引导（无数字，不触 D6 门）
      const answer = '「' + (rejectKw ?? '这个问题') + '」属于活跃/转化域——这块口径还没注册，我不猜数。现在能答：注册总量、分渠道注册、性别分布，换个问法试试？';
      return {
        path: 'rejected', rule: 'OUT_OF_SCOPE', answer, sql: null, rows: [], tables: [],
        steps: [
          routeStep('OUT_OF_SCOPE', true),
          st(2, '口径拦截', 'blocked', answer),
          st(7, '回答', 'blocked', answer),
        ],
      };
    }
    case 'unregistered': {
      const answer = '该问题尚未注册口径，可提交为新的派生规则候选。';
      return {
        path: 'unregistered', rule: null, answer, sql: null, rows: [], tables: [],
        steps: [
          routeStep('无', false),
          st(7, '回答', 'blocked', answer),
        ],
      };
    }
    case 'validation_failed': {
      const answer = '校验未通过，拒绝返回结果。';
      return {
        path: 'validation_failed', rule: 'REG_BY_CHANNEL', answer, sql: SQL_CHANNEL, rows: [], tables: [],
        steps: [
          routeStep('REG_BY_CHANNEL', true),
          st(2, '口径声明', 'ok', '明细按 rgst_chnl_id 聚合去重；渠道名 JOIN 渠道维表；与 REG_TOTAL 必须同源一致'),
          st(3, '参数抽取+校验', 'ok', '{"start":"2026-08-01","end":"2026-08-31"} ✓（关键词回退抽取）'),
          st(4, 'SQL 编译', 'ok', '按命中规则的模板编译，参数已绑定', { sql: SQL_CHANNEL }),
          st(5, '下推执行', 'ok', 'sqlite → 4 行，6.8ms', { ms: 6.8 }),
          st(6, '结果校验', 'ok', '✓ 列结构与规则声明一致'),
          st(6, '结果校验', 'fail', '✗ 同源交叉：分渠道合计 3,000 ≠ 热路径总数 2,893'),
          st(7, '回答', 'blocked', answer),
        ],
      };
    }
  }
}

function buildResult(sc: DataScenario, question: string): FinalResult {
  const rejectKw = question.match(/活跃|活动|日活|抽奖|转化/)?.[0];
  const s = buildSpec(sc, rejectKw);
  return {
    request_id: 'REQ-2026-09-09-MOCK01',
    started_at: '2026-09-09T13:45:00',
    total_ms: 1320,
    data_profile: 'mock', // 演示诚信徽标元数据（对齐 engine.py final 帧）
    question,
    rule: s.rule,
    path: s.path,
    answer: s.answer,
    sql: s.sql,
    rows: s.rows,
    tables: s.tables,
    steps: s.steps,
    block_reason: s.block_reason,
    degraded: s.degraded,
    viz: s.viz,
  };
}

function tokenEvents(answer: string): ChatEvent[] {
  const evs: ChatEvent[] = [];
  for (let i = 0; i < answer.length; i += 3) {
    evs.push({ kind: 'token', text: answer.slice(i, i + 3) });
  }
  return evs;
}

/** 组装一次模拟查询的完整事件序列（step → token? → final/error），格式对齐附录 A。 */
export function buildMockEvents(question: string): ChatEvent[] {
  const sc = pickScenario(question);
  if (sc === 'service_error') {
    // 附录 B：基础设施失败 → 脱敏 error 帧（后发出即终止，无 final）
    return [
      { kind: 'step', step: st(1, '意图路由', 'fail', '语义服务基础设施异常（mock 场景：模拟服务不可达）') },
      { kind: 'error', code: 'E_NET', message: '查询失败：服务未响应' },
    ];
  }
  if (sc === 'interrupted_stream') {
    // 附录 A：断流无 final 帧 → 壳判「已中断」+ 重试
    return [
      { kind: 'step', step: st(1, '意图路由', 'ok', '选定规则 = REG_TOTAL（mock 路由 · 模拟 DeepSeek 286ms）') },
      { kind: 'step', step: st(2, '口径声明', 'ok', CALIBER_TOTAL) },
    ];
  }
  const result = buildResult(sc, question);
  const evs: ChatEvent[] = result.steps.map((s) => ({ kind: 'step', step: s }) as ChatEvent);
  if (SUCCESS_PATHS.includes(result.path)) evs.push(...tokenEvents(result.answer));
  evs.push({ kind: 'final', result });
  return evs;
}
