"""双库连接与 schema 管理（B2，技术方案 §7.3/§7.4）。

- 源系统库（source）：权威（backing datasource，类比 Palantir data layer），动作写回目标；
- 本体库（ontology）：索引 + 本体自有状态（ontology_state）+ 审计（audit_log）+ schema_version；
- 一致性取补偿式（§7.4）：源库事务先提交，本体库后写；本体库失败 → 审计记 failed，可人工对账；
- schema_version：本体演进最小实现（版本号+变更记录，分支/场景发布期，§7.3）。
"""

from __future__ import annotations

import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

# ----------------------------------------------------------------------
# 操作者白名单单一来源（TD-9 / red-team F3）
# ----------------------------------------------------------------------
# audit_log.actor 与 action_runs.executed_by 的 CHECK 值、运行时校验
# （action_engine.ALLOWED_ACTORS 由此导入）、API 层 X-Actor 白名单，全部同源，
# 防 schema 字面量与运行时校验双轨漂移。DDL 内经 _ACTOR_VALUES_ 占位符替换注入。
ALLOWED_ACTORS: tuple[str, ...] = ("human", "llm", "api")

# CHECK 值片段：由 ALLOWED_ACTORS 派生（repr 单引号 -> SQL 字面量）。
# 仅本模块一处可改，改后 audit_log / action_runs 的 CHECK 与运行时校验同步生效。
ACTOR_VALUES_SQL: str = "(" + ",".join(repr(a) for a in ALLOWED_ACTORS) + ")"


# ----------------------------------------------------------------------
# 治理骨架枚举单一来源（P1.5，TD-9 同源模式）
# 以下常量派生 GOVERNANCE_SCHEMA 的 CHECK 值；permissions.py / audit.py /
# annotate.py 的运行时校验与 DB CHECK 共用同一组常量，防 schema 字面量与
# 运行时校验双轨漂移。DDL 内经 _XXX_VALUES_ 占位符替换注入（仿 _ACTOR_VALUES_）。
# ----------------------------------------------------------------------
PERMISSION_OPERATIONS: tuple[str, ...] = ("read", "write", "approve")  # D2 三分治
PERMISSION_EFFECTS: tuple[str, ...] = ("allow", "deny")
SUBJECT_KINDS: tuple[str, ...] = ("agent", "human")  # D1 双主体
POLICY_SCOPES: tuple[str, ...] = ("object", "attribute")  # D4 粒度
MAPPING_KINDS: tuple[str, ...] = ("object", "attribute", "link")
CONFIDENCE_LEVELS: tuple[str, ...] = ("high", "medium", "low")
REVIEW_STATUSES: tuple[str, ...] = ("draft", "reviewing", "approved", "rejected")
RETENTION_CLASSES: tuple[str, ...] = ("standard", "sensitive", "transient")
AUDIT_SOURCES: tuple[str, ...] = ("action", "query", "review", "permission", "publish")


def _sql_in(values: tuple[str, ...]) -> str:
    """tuple[str] -> SQL 字面量列表（repr 单引号 -> SQL 字面量，仿 ACTOR_VALUES_SQL）。"""
    return "(" + ",".join(repr(v) for v in values) + ")"


SCHEMA_VERSION = 1

ONTOLOGY_SCHEMA = """
CREATE TABLE IF NOT EXISTS audit_log (
  audit_id          TEXT PRIMARY KEY,
  ts                TEXT NOT NULL,
  action_name       TEXT NOT NULL,
  actor             TEXT NOT NULL CHECK (actor IN _ACTOR_VALUES_),
  actor_detail      TEXT NOT NULL DEFAULT '',
  request_id        TEXT NOT NULL DEFAULT '',
  params_json       TEXT NOT NULL,
  preconditions_json TEXT NOT NULL DEFAULT '[]',
  effects_json      TEXT NOT NULL DEFAULT '[]',
  writeback_json    TEXT NOT NULL DEFAULT '[]',
  outcome           TEXT NOT NULL CHECK (outcome IN ('applied','rejected','failed')),
  error_code        TEXT,
  message           TEXT,
  detail_json       TEXT,
  duration_ms       INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS ontology_state (
  object_type  TEXT NOT NULL,
  pk           TEXT NOT NULL,
  prop         TEXT NOT NULL,
  value        TEXT,
  updated_at   TEXT NOT NULL,
  PRIMARY KEY (object_type, pk, prop)
);
CREATE TABLE IF NOT EXISTS schema_version (
  version    INTEGER PRIMARY KEY,
  note       TEXT NOT NULL,
  applied_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_log(action_name);
CREATE INDEX IF NOT EXISTS idx_audit_outcome ON audit_log(outcome);
""".replace("_ACTOR_VALUES_", ACTOR_VALUES_SQL)

# ======================================================================
# BUILDER_SCHEMA_V1 —— 本体构建子系统 10 张表（蓝图 v0.3 §4 / 补丁 v0.3.1）
#
# 数据全部落本体库（data/ontology/ontology.db），与运行时段（audit_log /
# ontology_state / schema_version）共库；构建产物在运行时只读（补丁 A2）。
# schema_version 复用本体库单版本号表（v1），注脚追加 builder 段标识。
# ======================================================================

BUILDER_SCHEMA_VERSION = 1

# action_runs 表列定义单一来源（TD-9）：BUILDER_SCHEMA 建表与 v4 迁移重建共用，
# 保证存量库重建后表结构与新库完全一致（不双轨漂移）。CHECK 值经 _ACTOR_VALUES_
# 占位符由模块顶部 ALLOWED_ACTORS 派生（与 audit_log.actor 同源）。
ACTION_RUNS_COLUMNS = """  id              TEXT PRIMARY KEY,
  action_type_id  TEXT NOT NULL,
  before_snapshot_json TEXT NOT NULL DEFAULT '{}',
  after_snapshot_json  TEXT NOT NULL DEFAULT '{}',
  status          TEXT NOT NULL CHECK (status IN ('applied','rejected','failed','dry_run')),
  error           TEXT NOT NULL DEFAULT '',
  executed_by     TEXT NOT NULL DEFAULT 'api' CHECK (executed_by IN _ACTOR_VALUES_),
  -- TD-9（v4 patch）：executed_by 白名单 CHECK，与 audit_log.actor 同源。
  -- v3 patch（P4/E6）：audit_ref 引用 audit_log.audit_id（对账锚点）。
  -- audit_log 仍是运行时审计权威；action_runs 只引用不复制（单一真相，不双轨漂移）。
  audit_ref       TEXT NOT NULL DEFAULT '',
  created_at      TEXT NOT NULL
"""

# 占位符解析后的最终列定义（CHECK 值由 ALLOWED_ACTORS 派生注入）：
# BUILDER_SCHEMA 建表与 v4 迁移重建共用此单一来源，保证两处 DDL 完全一致。
ACTION_RUNS_COLUMNS_SQL: str = ACTION_RUNS_COLUMNS.replace(
    "_ACTOR_VALUES_", ACTOR_VALUES_SQL
)

# BUILDER_TABLES 单一来源（red-team I3）：从下方 BUILDER_SCHEMA DDL 自动解析。
# 任何增删 CREATE TABLE 都会自动反映到 BUILDER_TABLES，避免双轨漂移。
# （实际赋值在 BUILDER_SCHEMA 定义之后，见文件底部 I3 hook。）

BUILDER_SCHEMA = """
CREATE TABLE IF NOT EXISTS object_types (
  id              TEXT PRIMARY KEY,
  ontology_id     TEXT NOT NULL DEFAULT 'default',
  name            TEXT NOT NULL,
  name_cn         TEXT NOT NULL DEFAULT '',
  description     TEXT NOT NULL DEFAULT '',
  category        TEXT NOT NULL CHECK (category IN ('domain','artifact','conceptual')),
  property_schema TEXT NOT NULL DEFAULT '{}',
  status          TEXT NOT NULL CHECK (status IN ('draft','reviewed','published')),
  created_at      TEXT NOT NULL,
  updated_at      TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_object_types_name ON object_types(name);
CREATE INDEX IF NOT EXISTS idx_object_types_status ON object_types(status);

CREATE TABLE IF NOT EXISTS link_types (
  id              TEXT PRIMARY KEY,
  ontology_id     TEXT NOT NULL DEFAULT 'default',
  name            TEXT NOT NULL,
  semantic_name   TEXT NOT NULL DEFAULT '',
  category        TEXT NOT NULL CHECK (category IN ('semantic','fk_inferred','structural')),
  source_type_id  TEXT,
  target_type_id  TEXT,
  cardinality     TEXT NOT NULL CHECK (cardinality IN ('1:1','1:N','N:1','N:M')),
  status          TEXT NOT NULL CHECK (status IN ('draft','reviewed','published')),
  created_at      TEXT NOT NULL,
  updated_at      TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_link_types_name ON link_types(name);
CREATE INDEX IF NOT EXISTS idx_link_types_status ON link_types(status);

CREATE TABLE IF NOT EXISTS datasets (
  id          TEXT PRIMARY KEY,
  ontology_id TEXT NOT NULL DEFAULT 'default',
  name        TEXT NOT NULL,
  kind        TEXT NOT NULL CHECK (kind IN ('csv','excel','json','md','pdf','docx')),
  status      TEXT NOT NULL CHECK (status IN ('uploaded','ingested','failed')),
  row_count   INTEGER NOT NULL DEFAULT 0,
  schema_json TEXT NOT NULL DEFAULT '{}',
  source_path TEXT NOT NULL DEFAULT '',
  created_at  TEXT NOT NULL,
  updated_at  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_datasets_kind ON datasets(kind);
CREATE INDEX IF NOT EXISTS idx_datasets_status ON datasets(status);

CREATE TABLE IF NOT EXISTS pipelines (
  id          TEXT PRIMARY KEY,
  ontology_id TEXT NOT NULL DEFAULT 'default',
  name        TEXT NOT NULL,
  dag_json    TEXT NOT NULL DEFAULT '{"nodes":[],"edges":[]}',
  status      TEXT NOT NULL CHECK (status IN ('draft','active','archived')),
  created_at  TEXT NOT NULL,
  updated_at  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_pipelines_status ON pipelines(status);

CREATE TABLE IF NOT EXISTS curated_datasets (
  id            TEXT PRIMARY KEY,
  dataset_id    TEXT NOT NULL,
  quality_json  TEXT NOT NULL DEFAULT '{}',
  status        TEXT NOT NULL CHECK (status IN ('draft','reviewed','approved')),
  version       INTEGER NOT NULL DEFAULT 1,
  row_count     INTEGER NOT NULL DEFAULT 0,
  created_at    TEXT NOT NULL,
  updated_at    TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_curated_dataset ON curated_datasets(dataset_id);
CREATE INDEX IF NOT EXISTS idx_curated_status ON curated_datasets(status);

CREATE TABLE IF NOT EXISTS mappings (
  id              TEXT PRIMARY KEY,
  ontology_id     TEXT NOT NULL DEFAULT 'default',
  entity_class    TEXT NOT NULL,
  source_table    TEXT NOT NULL,
  field_mapping_json TEXT NOT NULL DEFAULT '{}',
  fk_mappings_json   TEXT NOT NULL DEFAULT '[]',
  cardinalities_json TEXT NOT NULL DEFAULT '{}',
  status          TEXT NOT NULL CHECK (status IN ('draft','reviewed','published')),
  created_at      TEXT NOT NULL,
  updated_at      TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_mappings_entity ON mappings(entity_class);
CREATE INDEX IF NOT EXISTS idx_mappings_status ON mappings(status);

CREATE TABLE IF NOT EXISTS extraction_tasks (
  id                  TEXT PRIMARY KEY,
  ontology_id         TEXT NOT NULL DEFAULT 'default',
  status              TEXT NOT NULL CHECK (status IN ('pending','running','succeeded','failed','rejected')),
  result_summary_json TEXT NOT NULL DEFAULT '{}',
  validation_report_json TEXT NOT NULL DEFAULT '{}',
  -- P3 提取器溯源字段（QA 备注 W1）：source_path 记原始数据路径，provider 记 LLM provider 名
  source_path         TEXT NOT NULL DEFAULT '',
  provider            TEXT NOT NULL DEFAULT '',
  created_at          TEXT NOT NULL,
  updated_at          TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_extraction_status ON extraction_tasks(status);

CREATE TABLE IF NOT EXISTS logic_rules (
  id           TEXT PRIMARY KEY,
  ontology_id  TEXT NOT NULL DEFAULT 'default',
  name         TEXT NOT NULL,
  logic_type   TEXT NOT NULL CHECK (logic_type IN ('state_machine','precondition','threshold','invariant')),
  expression_json TEXT NOT NULL DEFAULT '{}',
  severity     TEXT NOT NULL CHECK (severity IN ('info','warning','error','fatal')),
  status       TEXT NOT NULL CHECK (status IN ('draft','reviewed','published')),
  created_at   TEXT NOT NULL,
  updated_at   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_logic_rules_status ON logic_rules(status);

CREATE TABLE IF NOT EXISTS action_types (
  id                     TEXT PRIMARY KEY,
  ontology_id            TEXT NOT NULL DEFAULT 'default',
  name                   TEXT NOT NULL,
  parameters_json        TEXT NOT NULL DEFAULT '{}',
  submission_criteria_json TEXT NOT NULL DEFAULT '{}',
  effects_json           TEXT NOT NULL DEFAULT '{}',
  status                 TEXT NOT NULL CHECK (status IN ('draft','reviewed','published')),
  created_at             TEXT NOT NULL,
  updated_at             TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_action_types_name ON action_types(name);
CREATE INDEX IF NOT EXISTS idx_action_types_status ON action_types(status);

CREATE TABLE IF NOT EXISTS action_runs (
__ACTION_RUNS_COLUMNS__
);
CREATE INDEX IF NOT EXISTS idx_action_runs_type ON action_runs(action_type_id);
CREATE INDEX IF NOT EXISTS idx_action_runs_status ON action_runs(status);
""".replace("__ACTION_RUNS_COLUMNS__", ACTION_RUNS_COLUMNS_SQL)


# ======================================================================
# GOVERNANCE_SCHEMA —— 治理骨架三张网（P1.5，设计 §4.1）
#
# ① 权限元数据（permission_roles / permission_policies + 索引）；
# ② 审计最小骨架（audit_field_mirror 字段级镜像 + WORM 触发器；
#    audit_log 加列走幂等补丁 _apply_governance_patches）；
# ③ 映射置信度打标（mapping_candidates / mapping_review_history + 索引 + WORM）。
#
# 全部落 ontology.db（治理真相库），与运行时段 / builder 段共库。
# CHECK 值经 _XXX_VALUES_ 占位符由模块顶部常量派生（TD-9 同源），
# 防 schema 字面量与运行时校验双轨漂移。
# ======================================================================
_GOVERNANCE_SCHEMA_TEMPLATE = """
-- ================= 治理骨架（P1.5）=================
-- ① 权限元数据
CREATE TABLE IF NOT EXISTS permission_roles (
  role_id      TEXT PRIMARY KEY,
  name         TEXT NOT NULL,
  members_json TEXT NOT NULL DEFAULT '[]',     -- [{"kind": "agent"|"human", "id": "..."}]
  created_at   TEXT NOT NULL,
  updated_at   TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS permission_policies (
  policy_id      TEXT PRIMARY KEY,
  object_type    TEXT NOT NULL,                -- V1 注册表校验（应用层）
  operation      TEXT NOT NULL CHECK (operation IN _OP_VALUES_),
  effect         TEXT NOT NULL CHECK (effect IN _EFFECT_VALUES_),
  -- 空串 = 纯角色策略（subject=None + role_id 引用，V7 二选一）持久化形态，decide 按角色展开
  subject_kind   TEXT NOT NULL DEFAULT '' CHECK (subject_kind IN _SUBJECT_KIND_VALUES_),
  subject_id     TEXT NOT NULL DEFAULT '',
  role_id        TEXT NOT NULL DEFAULT '',     -- 与 subject 二选一（V7 应用层）
  scope          TEXT NOT NULL DEFAULT 'object' CHECK (scope IN _SCOPE_VALUES_),
  attributes_json TEXT NOT NULL DEFAULT '[]',  -- V6：仅 operation=read 允许非空
  version        INTEGER NOT NULL DEFAULT 1,
  created_at     TEXT NOT NULL,
  updated_at     TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_policy_obj  ON permission_policies(object_type, operation);

-- ② 审计：字段级镜像（audit_log 加列走幂等补丁，见 _apply_governance_patches）
CREATE TABLE IF NOT EXISTS audit_field_mirror (
  mirror_id    TEXT PRIMARY KEY,
  audit_id     TEXT NOT NULL,                  -- 应用层对账（TD-10 先例，不加 SQLite FK）
  object_type  TEXT NOT NULL,
  pk           TEXT NOT NULL,
  prop         TEXT NOT NULL,
  old_value    TEXT,
  new_value    TEXT,
  ts           TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_mirror_audit  ON audit_field_mirror(audit_id);
CREATE INDEX IF NOT EXISTS idx_mirror_target ON audit_field_mirror(object_type, pk, prop);
-- WORM 触发器（audit_log / audit_field_mirror）
CREATE TRIGGER IF NOT EXISTS trg_audit_log_wo_upd  BEFORE UPDATE ON audit_log
  BEGIN SELECT RAISE(ABORT, 'audit_log 只读（WORM）'); END;
CREATE TRIGGER IF NOT EXISTS trg_audit_log_wo_del  BEFORE DELETE ON audit_log
  BEGIN SELECT RAISE(ABORT, 'audit_log 只读（WORM）'); END;
CREATE TRIGGER IF NOT EXISTS trg_mirror_wo_upd  BEFORE UPDATE ON audit_field_mirror
  BEGIN SELECT RAISE(ABORT, 'audit_field_mirror 只读（WORM）'); END;
CREATE TRIGGER IF NOT EXISTS trg_mirror_wo_del  BEFORE DELETE ON audit_field_mirror
  BEGIN SELECT RAISE(ABORT, 'audit_field_mirror 只读（WORM）'); END;

-- ③ 映射置信度打标
CREATE TABLE IF NOT EXISTS mapping_candidates (
  candidate_id     TEXT PRIMARY KEY,
  kind             TEXT NOT NULL CHECK (kind IN _MAPPING_KIND_VALUES_),
  source_table     TEXT NOT NULL,
  source_field     TEXT,
  target           TEXT NOT NULL,              -- C4 注册表校验（应用层）
  confidence_score REAL NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
  confidence_level TEXT NOT NULL CHECK (confidence_level IN _LEVEL_VALUES_),
  review_status    TEXT NOT NULL CHECK (review_status IN _STATUS_VALUES_),
  auto_approved    INTEGER NOT NULL DEFAULT 0,
  evidence_json    TEXT NOT NULL DEFAULT '{}',
  created_at       TEXT NOT NULL,
  updated_at       TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_cand_status ON mapping_candidates(review_status, confidence_level);
CREATE TABLE IF NOT EXISTS mapping_review_history (
  history_id   TEXT PRIMARY KEY,
  candidate_id TEXT NOT NULL,
  from_status  TEXT NOT NULL,
  to_status    TEXT NOT NULL,
  reviewer     TEXT NOT NULL,                   -- human id 或 'auto'
  reviewed_at  TEXT NOT NULL,
  note         TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_review_cand ON mapping_review_history(candidate_id);
-- WORM 触发器（mapping_review_history：审核痕迹 append-only）
CREATE TRIGGER IF NOT EXISTS trg_review_wo_upd  BEFORE UPDATE ON mapping_review_history
  BEGIN SELECT RAISE(ABORT, 'mapping_review_history 只读（WORM）'); END;
CREATE TRIGGER IF NOT EXISTS trg_review_wo_del  BEFORE DELETE ON mapping_review_history
  BEGIN SELECT RAISE(ABORT, 'mapping_review_history 只读（WORM）'); END;
"""
GOVERNANCE_SCHEMA: str = (
    _GOVERNANCE_SCHEMA_TEMPLATE.replace("_OP_VALUES_", _sql_in(PERMISSION_OPERATIONS))
    .replace("_EFFECT_VALUES_", _sql_in(PERMISSION_EFFECTS))
    # 纯角色策略（V7 二选一）subject_kind 持久化为空串：CHECK 值 = 合法主体类型 + 空串标记
    .replace("_SUBJECT_KIND_VALUES_", _sql_in(SUBJECT_KINDS + ("",)))
    .replace("_SCOPE_VALUES_", _sql_in(POLICY_SCOPES))
    .replace("_MAPPING_KIND_VALUES_", _sql_in(MAPPING_KINDS))
    .replace("_LEVEL_VALUES_", _sql_in(CONFIDENCE_LEVELS))
    .replace("_STATUS_VALUES_", _sql_in(REVIEW_STATUSES))
)


def _patch_action_runs_executed_by_check(conn: sqlite3.Connection) -> None:
    """v4 patch（TD-9）：action_runs.executed_by 补 CHECK 白名单。

    SQLite 不支持 ALTER TABLE ... ADD CONSTRAINT，采用重建表迁移：单事务内
    建新表（含 CHECK）→ 拷数据 → 换名 → 重建索引；失败整体回滚，不丢数据。
    新库（BUILDER_SCHEMA 已含 CHECK）与已迁移库经 sqlite_master 检出后幂等跳过。
    存量数据含白名单外 executed_by 时 INSERT..SELECT 触发 CHECK 失败 -> 回滚
    （不破坏数据；当前演示/测试数据均为合法 actor，无实际阻塞）。
    """
    row = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='action_runs'"
    ).fetchone()
    if row is None:
        return
    if "CHECK (executed_by IN" in (row[0] or ""):
        return
    # 防御性前置：重建列清单依赖 audit_ref 存在（v3 patch 已先执行，此处再兜底）
    cols = {r[1] for r in conn.execute("PRAGMA table_info(action_runs)").fetchall()}
    if "audit_ref" not in cols:
        conn.execute(
            "ALTER TABLE action_runs ADD COLUMN audit_ref TEXT NOT NULL DEFAULT ''"
        )
    conn.execute("PRAGMA foreign_keys=OFF")
    conn.execute("BEGIN")
    try:
        conn.execute("DROP INDEX IF EXISTS idx_action_runs_type")
        conn.execute("DROP INDEX IF EXISTS idx_action_runs_status")
        conn.execute(
            f"CREATE TABLE action_runs_new (\n{ACTION_RUNS_COLUMNS_SQL})"
        )
        conn.execute(
            "INSERT INTO action_runs_new (id, action_type_id, before_snapshot_json, "
            "after_snapshot_json, status, error, executed_by, audit_ref, created_at) "
            "SELECT id, action_type_id, before_snapshot_json, after_snapshot_json, "
            "status, error, executed_by, audit_ref, created_at FROM action_runs"
        )
        conn.execute("DROP TABLE action_runs")
        conn.execute("ALTER TABLE action_runs_new RENAME TO action_runs")
        conn.execute(
            "CREATE INDEX idx_action_runs_type ON action_runs(action_type_id)"
        )
        conn.execute(
            "CREATE INDEX idx_action_runs_status ON action_runs(status)"
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def _apply_builder_patches(conn: sqlite3.Connection) -> None:
    """builder 段幂等补丁（v2/v3/v4）单一实现：migrate 与 init_builder_schema
    共用，防两处逻辑双轨漂移。

    - v2：link_types.fk_field（idempotent ALTER）；
    - v3：action_runs.audit_ref（idempotent ALTER）；
    - v4（TD-9）：action_runs.executed_by CHECK 白名单（重建表迁移）。
    """
    # v2 patch：link_types 加 fk_field（idempotent）。
    cols = {r[1] for r in conn.execute("PRAGMA table_info(link_types)").fetchall()}
    if "fk_field" not in cols:
        conn.execute("ALTER TABLE link_types ADD COLUMN fk_field TEXT NOT NULL DEFAULT ''")
    # v3 patch（P4/E6）：action_runs 加 audit_ref（idempotent）。
    cols = {r[1] for r in conn.execute("PRAGMA table_info(action_runs)").fetchall()}
    if "audit_ref" not in cols:
        conn.execute(
            "ALTER TABLE action_runs ADD COLUMN audit_ref TEXT NOT NULL DEFAULT ''"
        )
    # v4 patch（TD-9）：action_runs.executed_by CHECK 白名单。
    _patch_action_runs_executed_by_check(conn)


def _apply_governance_patches(conn: sqlite3.Connection) -> None:
    """治理段幂等补丁：audit_log 加 4 列（prev_hash/record_hash/retention_class/source）。

    仿 v2/v3 ALTER 先例：PRAGMA table_info 检出已加则跳过。新列均有默认值，
    既有行保持兼容（设计 §4.3）。仅在 audit_log 存在时执行（Store.migrate 路径
    ONTOLOGY_SCHEMA 已先建表；裸 builder 库无此表则跳过，不误伤）。
    """
    cols = {r[1] for r in conn.execute("PRAGMA table_info(audit_log)").fetchall()}
    if not cols:
        return
    if "prev_hash" not in cols:
        conn.execute("ALTER TABLE audit_log ADD COLUMN prev_hash TEXT NOT NULL DEFAULT ''")
    if "record_hash" not in cols:
        conn.execute("ALTER TABLE audit_log ADD COLUMN record_hash TEXT NOT NULL DEFAULT ''")
    if "retention_class" not in cols:
        conn.execute(
            "ALTER TABLE audit_log ADD COLUMN retention_class TEXT NOT NULL DEFAULT 'sensitive' "
            f"CHECK (retention_class IN {_sql_in(RETENTION_CLASSES)})"
        )
    if "source" not in cols:
        conn.execute(
            "ALTER TABLE audit_log ADD COLUMN source TEXT NOT NULL DEFAULT 'action' "
            f"CHECK (source IN {_sql_in(AUDIT_SOURCES)})"
        )
    _patch_audit_log_source_check(conn)


def _patch_audit_log_source_check(conn: sqlite3.Connection) -> None:
    """v5 patch（P3）：audit_log.source CHECK 补 'publish'（发布审计 source='publish'）。

    P3 引入发布审计（action_name='mapping_publish', source='publish'），但存量库的
    source CHECK 白名单（('action','query','review','permission')）不含 'publish'，
    SQLite 无法 ALTER ADD CONSTRAINT。采用重建表迁移（仿 v4 action_runs.executed_by
    先例）：单事务建新表（含新 CHECK）→ 拷数据 → 换名 → 重建索引与 WORM 触发器；
    失败整体回滚不丢数据。存量哈希链 prev_hash/record_hash 原样拷贝，verify_integrity
    不受影响。新库（source 列已按最新 AUDIT_SOURCES 建 CHECK）经 sqlite_master 检出
    'publish' 后幂等跳过。
    """
    row = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='audit_log'"
    ).fetchone()
    if row is None or "publish" in (row[0] or ""):
        return
    new_sql = re.sub(
        r"CHECK \(source IN \(.*?\)\)",
        f"CHECK (source IN {_sql_in(AUDIT_SOURCES)})",
        row[0],
        flags=re.DOTALL,
    )
    cols = ",".join(r[1] for r in conn.execute("PRAGMA table_info(audit_log)").fetchall())
    new_sql = re.sub(r"^CREATE TABLE audit_log", "CREATE TABLE audit_log_new", new_sql, count=1)
    try:
        conn.execute("DROP TRIGGER IF EXISTS trg_audit_log_wo_upd")
        conn.execute("DROP TRIGGER IF EXISTS trg_audit_log_wo_del")
        conn.execute(new_sql)
        conn.execute(f"INSERT INTO audit_log_new ({cols}) SELECT {cols} FROM audit_log")
        conn.execute("DROP TABLE audit_log")
        conn.execute("ALTER TABLE audit_log_new RENAME TO audit_log")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_log(action_name)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_outcome ON audit_log(outcome)")
        conn.execute(
            "CREATE TRIGGER trg_audit_log_wo_upd BEFORE UPDATE ON audit_log "
            "BEGIN SELECT RAISE(ABORT, 'audit_log 只读（WORM）'); END"
        )
        conn.execute(
            "CREATE TRIGGER trg_audit_log_wo_del BEFORE DELETE ON audit_log "
            "BEGIN SELECT RAISE(ABORT, 'audit_log 只读（WORM）'); END"
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def init_builder_schema(conn: sqlite3.Connection) -> None:
    """建 builder 10 张表（幂等，CREATE TABLE IF NOT EXISTS 风格）。

    与 schema_version 共用本体库单版本号表（v1），注脚合并运行时 + builder 两段。
    后续阶段引入破坏性变更时升 version（蓝图 §10 schema_version 演进）。
    裸调用场景下若 schema_version 尚未建，本函数自包含建表（不依赖 ONTOLOGY_SCHEMA
    已先执行），避免调用方耦合。

    note 字段含运行时 + builder 两段（与 Store.migrate 一致；red-team E2 修复：
    即便独立调用也保持 schema_version note 完整）。
    """
    # schema_version 在 BUILDER_SCHEMA 内被 INSERT 引用，先确保它存在
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_version ("
        "version INTEGER PRIMARY KEY, note TEXT NOT NULL, applied_at TEXT NOT NULL)"
    )
    conn.executescript(BUILDER_SCHEMA)
    _apply_builder_patches(conn)
    runtime_note = (
        "MVP 本体运行时 v1：audit_log / ontology_state / schema_version"
    )
    builder_note = (
        "含 builder 子系统 10 表（蓝图 v0.3 §4 / 补丁 v0.3.1）；"
        "v2 patch: link_types.fk_field；v3 patch: action_runs.audit_ref；"
        "v4 patch: action_runs.executed_by CHECK（TD-9）"
    )
    conn.execute(
        "INSERT OR REPLACE INTO schema_version (version, note, applied_at) "
        "VALUES (?,?,?)",
        (
            BUILDER_SCHEMA_VERSION,
            f"{runtime_note}；{builder_note}",
            _now(),
        ),
    )
    conn.commit()

DEFAULT_SOURCE_DB = (
    Path(__file__).resolve().parents[2] / "data" / "sources" / "retail_source.db"
)
DEFAULT_ONTOLOGY_DB = (
    Path(__file__).resolve().parents[2] / "data" / "ontology" / "ontology.db"
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


class Store:
    """双库访问入口：每次调用返回独立连接（SQLite 单写连接 = 天然串行，§3.4）。"""

    def __init__(
        self,
        source_path: str | Path | None = None,
        ontology_path: str | Path | None = None,
    ) -> None:
        self._source_path = Path(source_path) if source_path else DEFAULT_SOURCE_DB
        self._ontology_path = (
            Path(ontology_path) if ontology_path else DEFAULT_ONTOLOGY_DB
        )
        self._ontology_path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def source_path(self) -> Path:
        return self._source_path

    @property
    def ontology_path(self) -> Path:
        return self._ontology_path

    def source_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._source_path)
        conn.row_factory = sqlite3.Row
        return conn

    def ontology_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._ontology_path)
        conn.row_factory = sqlite3.Row
        return conn

    def migrate(self, version: int = SCHEMA_VERSION) -> None:
        """建表 + 记录 schema 版本（幂等）。

        一次 migrate 同时落运行时段（audit_log / ontology_state / schema_version）
        与 builder 段（10 张表 + BUILDER_SCHEMA_VERSION）。两段共用 v1 行，note 用
        分号拼接两段说明，避免前次 INSERT 被覆盖导致丢失运行时段说明（red-team E2）。

        v2 patch（P2）：link_types 加 fk_field 列（idempotent ALTER，已建则跳过）。
        loader 用此列做 link_types 入 Registry 的 fk_field 校验。
        v3 patch（P4/E6）：action_runs 加 audit_ref 列（idempotent ALTER）。
        action_runs 引用 audit_log.audit_id 对账，不复制审计真相。
        v4 patch（TD-9）：action_runs.executed_by 补 CHECK 白名单（重建表迁移，
        SQLite 无 ALTER ADD CONSTRAINT；单事务保数据，幂等跳过已迁移库）。
        """
        runtime_note = (
            "MVP 本体运行时 v1：audit_log / ontology_state / schema_version"
        )
        builder_note = (
            "含 builder 子系统 10 表（蓝图 v0.3 §4 / 补丁 v0.3.1）；"
            "v2 patch: link_types.fk_field；v3 patch: action_runs.audit_ref；"
            "v4 patch: action_runs.executed_by CHECK（TD-9）"
        )
        governance_note = (
            "治理段（P1.5）：permission_roles/permission_policies/audit_field_mirror/"
            "mapping_candidates/mapping_review_history + audit_log 加列(prev_hash/"
            "record_hash/retention_class/source) + WORM 触发器 + 枚举 CHECK 同源"
        )
        merged_note = f"{runtime_note}；{builder_note}；{governance_note}"
        conn = self.ontology_conn()
        try:
            conn.executescript(ONTOLOGY_SCHEMA)
            conn.executescript(BUILDER_SCHEMA)
            # v2/v3/v4 幂等补丁单一实现（PRAGMA table_info 返回列序
            # [cid, name, type, notnull, dflt_value, pk]，索引 1 = name）。
            _apply_builder_patches(conn)
            # P1.5 治理段：新表 CREATE IF NOT EXISTS + audit_log 幂等加列
            # （不 bump schema_version，沿用 v2/v3/v4「幂等补丁只追加 note 不升号」先例）。
            conn.executescript(GOVERNANCE_SCHEMA)
            _apply_governance_patches(conn)
            # 单次 INSERT OR REPLACE，note 含两段（red-team E2 修复：避免二次覆盖）
            conn.execute(
                "INSERT OR REPLACE INTO schema_version (version, note, applied_at) "
                "VALUES (?,?,?)",
                (version, merged_note, _now()),
            )
            conn.commit()
        finally:
            conn.close()

    def get_schema_version(self) -> int | None:
        conn = self.ontology_conn()
        try:
            row = conn.execute(
                "SELECT MAX(version) AS v FROM schema_version"
            ).fetchone()
            return row["v"] if row else None
        finally:
            conn.close()


# ----------------------------------------------------------------------
# I3 hook：BUILDER_TABLES 从 BUILDER_SCHEMA DDL 解析（单一来源，red-team I3）
# 必须在 BUILDER_SCHEMA 定义之后执行。
# ----------------------------------------------------------------------
import re as _re

BUILDER_TABLES = tuple(
    _re.findall(r"CREATE TABLE IF NOT EXISTS (\w+)", BUILDER_SCHEMA)
)

# 治理段表单一来源（red-team I3 模式）：从 GOVERNANCE_SCHEMA DDL 自动解析。
GOVERNANCE_TABLES = tuple(
    _re.findall(r"CREATE TABLE IF NOT EXISTS (\w+)", GOVERNANCE_SCHEMA)
)
del _re  # 局部别名，不污染模块命名空间
