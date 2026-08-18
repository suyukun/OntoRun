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

BUILDER_TABLES: tuple[str, ...] = (
    "object_types",
    "link_types",
    "datasets",
    "pipelines",
    "curated_datasets",
    "mappings",
    "extraction_tasks",
    "logic_rules",
    "action_types",
    "action_runs",
)

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
  created_at      TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_action_runs_type ON action_runs(action_type_id);
CREATE INDEX IF NOT EXISTS idx_action_runs_status ON action_runs(status);
"""


def init_builder_schema(conn: sqlite3.Connection) -> None:
    """建 builder 10 张表（幂等，CREATE TABLE IF NOT EXISTS 风格）。

    与 schema_version 共用本体库单版本号表（v1），注脚追加 builder 段标识。
    后续阶段引入破坏性变更时升 version（蓝图 §10 schema_version 演进）。
    裸调用场景下若 schema_version 尚未建，本函数自包含建表（不依赖 ONTOLOGY_SCHEMA
    已先执行），避免调用方耦合。
    """
    # schema_version 在 BUILDER_SCHEMA 内被 INSERT 引用，先确保它存在
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_version ("
        "version INTEGER PRIMARY KEY, note TEXT NOT NULL, applied_at TEXT NOT NULL)"
    )
    conn.executescript(BUILDER_SCHEMA)
    conn.execute(
        "INSERT OR REPLACE INTO schema_version (version, note, applied_at) "
        "VALUES (?,?,?)",
        (
            BUILDER_SCHEMA_VERSION,
            "MVP 本体运行时 v1：含 builder 子系统 10 表（蓝图 v0.3 §4 / 补丁 v0.3.1）",
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
        与 builder 段（10 张表 + BUILDER_SCHEMA_VERSION）。get_schema_version
        返回 MAX(version)，因 v1 行被两段共享，行为不变。
        """
        conn = self.ontology_conn()
        try:
            conn.executescript(ONTOLOGY_SCHEMA)
            conn.execute(
                "INSERT OR REPLACE INTO schema_version (version, note, applied_at) VALUES (?,?,?)",
                (
                    version,
                    "MVP 本体运行时 v1：audit_log / ontology_state / schema_version",
                    _now(),
                ),
            )
            # builder 段在 v1 行追加标识（共用版本号，note 标记子系统）
            conn.executescript(BUILDER_SCHEMA)
            conn.execute(
                "INSERT OR REPLACE INTO schema_version (version, note, applied_at) "
                "VALUES (?,?,?)",
                (
                    BUILDER_SCHEMA_VERSION,
                    "MVP 本体运行时 v1：含 builder 子系统 10 表（蓝图 v0.3 §4 / 补丁 v0.3.1）",
                    _now(),
                ),
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
