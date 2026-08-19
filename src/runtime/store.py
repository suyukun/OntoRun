"""双库连接与 schema 管理（B2，技术方案 §7.3/§7.4）。

- 源系统库（source）：权威（backing datasource，类比 Palantir data layer），动作写回目标；
- 本体库（ontology）：索引 + 本体自有状态（ontology_state）+ 审计（audit_log）+ schema_version；
- 一致性取补偿式（§7.4）：源库事务先提交，本体库后写；本体库失败 → 审计记 failed，可人工对账；
- schema_version：本体演进最小实现（版本号+变更记录，分支/场景发布期，§7.3）。
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1

ONTOLOGY_SCHEMA = """
CREATE TABLE IF NOT EXISTS audit_log (
  audit_id          TEXT PRIMARY KEY,
  ts                TEXT NOT NULL,
  action_name       TEXT NOT NULL,
  actor             TEXT NOT NULL CHECK (actor IN ('human','llm','api')),
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
"""

# ======================================================================
# BUILDER_SCHEMA_V1 —— 本体构建子系统 10 张表（蓝图 v0.3 §4 / 补丁 v0.3.1）
#
# 数据全部落本体库（data/ontology/ontology.db），与运行时段（audit_log /
# ontology_state / schema_version）共库；构建产物在运行时只读（补丁 A2）。
# schema_version 复用本体库单版本号表（v1），注脚追加 builder 段标识。
# ======================================================================

BUILDER_SCHEMA_VERSION = 1

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
  id              TEXT PRIMARY KEY,
  action_type_id  TEXT NOT NULL,
  before_snapshot_json TEXT NOT NULL DEFAULT '{}',
  after_snapshot_json  TEXT NOT NULL DEFAULT '{}',
  status          TEXT NOT NULL CHECK (status IN ('applied','rejected','failed','dry_run')),
  error           TEXT NOT NULL DEFAULT '',
  executed_by     TEXT NOT NULL DEFAULT 'api',
  -- v3 patch（P4/E6）：audit_ref 引用 audit_log.audit_id（对账锚点）。
  -- audit_log 仍是运行时审计权威；action_runs 只引用不复制（单一真相，不双轨漂移）。
  audit_ref       TEXT NOT NULL DEFAULT '',
  created_at      TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_action_runs_type ON action_runs(action_type_id);
CREATE INDEX IF NOT EXISTS idx_action_runs_status ON action_runs(status);
"""


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
    # v2 patch：link_types 加 fk_field（idempotent）。
    cols = {r[1] for r in conn.execute("PRAGMA table_info(link_types)").fetchall()}
    if "fk_field" not in cols:
        conn.execute("ALTER TABLE link_types ADD COLUMN fk_field TEXT NOT NULL DEFAULT ''")
    # v3 patch（P4/E6）：action_runs 加 audit_ref（idempotent）。
    cols = {r[1] for r in conn.execute("PRAGMA table_info(action_runs)").fetchall()}
    if "audit_ref" not in cols:
        conn.execute("ALTER TABLE action_runs ADD COLUMN audit_ref TEXT NOT NULL DEFAULT ''")
    runtime_note = (
        "MVP 本体运行时 v1：audit_log / ontology_state / schema_version"
    )
    builder_note = (
        "含 builder 子系统 10 表（蓝图 v0.3 §4 / 补丁 v0.3.1）；"
        "v2 patch: link_types.fk_field；v3 patch: action_runs.audit_ref"
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
        """
        runtime_note = (
            "MVP 本体运行时 v1：audit_log / ontology_state / schema_version"
        )
        builder_note = (
            "含 builder 子系统 10 表（蓝图 v0.3 §4 / 补丁 v0.3.1）；"
            "v2 patch: link_types.fk_field；v3 patch: action_runs.audit_ref"
        )
        merged_note = f"{runtime_note}；{builder_note}"
        conn = self.ontology_conn()
        try:
            conn.executescript(ONTOLOGY_SCHEMA)
            conn.executescript(BUILDER_SCHEMA)
            # v2 patch：link_types 加 fk_field（idempotent）。
            # PRAGMA table_info 返回列序 [cid, name, type, notnull, dflt_value, pk]，
            # 不依赖 row_factory；索引 1 = name。
            cols = {r[1] for r in conn.execute("PRAGMA table_info(link_types)").fetchall()}
            if "fk_field" not in cols:
                conn.execute("ALTER TABLE link_types ADD COLUMN fk_field TEXT NOT NULL DEFAULT ''")
            # v3 patch（P4/E6）：action_runs 加 audit_ref（idempotent）。
            cols = {r[1] for r in conn.execute("PRAGMA table_info(action_runs)").fetchall()}
            if "audit_ref" not in cols:
                conn.execute(
                    "ALTER TABLE action_runs ADD COLUMN audit_ref TEXT NOT NULL DEFAULT ''"
                )
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
del _re  # 局部别名，不污染模块命名空间
