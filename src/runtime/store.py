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

DEFAULT_SOURCE_DB = Path(__file__).resolve().parents[2] / "data" / "sources" / "retail_source.db"
DEFAULT_ONTOLOGY_DB = Path(__file__).resolve().parents[2] / "data" / "ontology" / "ontology.db"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


class Store:
    """双库访问入口：每次调用返回独立连接（SQLite 单写连接 = 天然串行，§3.4）。"""

    def __init__(self, source_path: str | Path | None = None,
                 ontology_path: str | Path | None = None) -> None:
        self._source_path = Path(source_path) if source_path else DEFAULT_SOURCE_DB
        self._ontology_path = Path(ontology_path) if ontology_path else DEFAULT_ONTOLOGY_DB
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
        """建表 + 记录 schema 版本（幂等）。"""
        conn = self.ontology_conn()
        try:
            conn.executescript(ONTOLOGY_SCHEMA)
            conn.execute(
                "INSERT OR REPLACE INTO schema_version (version, note, applied_at) VALUES (?,?,?)",
                (version, "MVP 本体运行时 v1：audit_log / ontology_state / schema_version", _now()))
            conn.commit()
        finally:
            conn.close()

    def get_schema_version(self) -> int | None:
        conn = self.ontology_conn()
        try:
            row = conn.execute("SELECT MAX(version) AS v FROM schema_version").fetchone()
            return row["v"] if row else None
        finally:
            conn.close()
