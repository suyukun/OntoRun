"""Central config: paths, .env loading, LLM switches, data coverage metadata."""

import os
import sqlite3
from functools import lru_cache
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data" / "fortune"

# Overridable via env so tests can pin isolated tmp stores.
FORTUNE_DB = Path(os.environ.get("FORTUNE_DB") or DATA_DIR / "fortune.db")
APP_DB = Path(os.environ.get("SEMANTIC_APP_DB") or DATA_DIR / "app.db")
TRACE_LOG = Path(os.environ.get("SEMANTIC_TRACE_LOG") or DATA_DIR / "trace_log.jsonl")

LLM_MODEL = os.environ.get("SEMANTIC_LLM_MODEL", "deepseek-chat")
LLM_TIMEOUT_S = float(os.environ.get("SEMANTIC_LLM_TIMEOUT_S", "6"))
HEARTBEAT_S = float(os.environ.get("SEMANTIC_HEARTBEAT_S", "14"))  # SSE comment ping (appendix A: 15s)
HISTORY_DEFAULT_LIMIT = 50


def _parse_dotenv(path: Path) -> dict:
    """Zero-dependency .env parser (KEY=VALUE lines only), same semantics as the demo."""
    env: dict = {}
    if not path.is_file():
        return env
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip().strip('"').strip("'")
    return env


_ENV = _parse_dotenv(ROOT_DIR / ".env")


def get_env(key: str, default: str | None = None) -> str | None:
    """os.environ wins over project-root .env (export override, matches conftest)."""
    val = os.environ.get(key)
    if val is not None:
        return val
    return _ENV.get(key, default)


def llm_disabled() -> bool:
    """SEMANTIC_DISABLE_LLM=1 forces keyword routing (tests / demo mode / rate-limit fallback)."""
    return (get_env("SEMANTIC_DISABLE_LLM") or "").strip().lower() in ("1", "true", "yes")


@lru_cache(maxsize=1)
def data_range() -> dict:
    """Sample data coverage derived from the data itself (semantic-layer metadata,
    not hardcoded) — powers the out_of_range rejection copy (product doc §4.2 #5)."""
    conn = sqlite3.connect(FORTUNE_DB)
    try:
        lo, hi = conn.execute(
            "SELECT MIN(d), MAX(d) FROM ("
            "  SELECT MIN(data_dt) AS d FROM dwd_tr_rgst_df"
            "  UNION ALL SELECT MIN(rgst_dt) FROM dim_cu_usr_info_df"
            "  UNION ALL SELECT MAX(data_dt) FROM dwd_tr_rgst_df"
            "  UNION ALL SELECT MAX(rgst_dt) FROM dim_cu_usr_info_df)"
        ).fetchone()
    finally:
        conn.close()
    return {"min": lo or "0001-01-01", "max": hi or "9999-12-31"}
