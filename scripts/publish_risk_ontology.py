"""S3：风险本体 33 对象 / 37 链接 从 builder draft 态批量 review/publish。

背景（Jack 验收口径）：
- scripts/seed_builder_from_risk_ontology.py 已把风险本体行以 draft 态 seed 进
  builder 存储（默认 data/ontology/ontology.db，行 id ot_s3_* / lt_s3_*）；
- 本脚本沿 E4 状态机（draft -> reviewed -> published）对每行依序执行既有
  review / publish 服务函数（object_types.transition_status /
  link_types.transition_status + publish_validator + conflict 校验），
  不绕过校验直接 UPDATE 库表；幂等可重跑：已 published 行零变更零报错。

运行时边界（重要）：
- 风险本体归属 S3 独立运行时（RiskStore + build_risk_source_registry +
  /risk-objects）；registry_loader 按 id 前缀 ot_s3_/lt_s3_ 把风险行挡在
  S1 共享 Registry 之外，故 /meta/schema 与 S1 浏览页不受污染；
- 图谱页经 /api/v1/builder/graph 聚合展示（内置零售段 + 已发布风险行）。

用法：
    python3 scripts/publish_risk_ontology.py [--ontology-db PATH] [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.builder import conflict as conflict_mod
from src.builder import link_types as lt_repo
from src.builder import object_types as ot_repo
from src.builder.publish_validator import (
    validate_link_type,
    validate_object_type,
)
from src.builder.status_machine import DRAFT, PUBLISHED, REVIEWED
from src.runtime.store import DEFAULT_ONTOLOGY_DB

# 与 seed 脚本约定的确定性 id 前缀（识别风险行）
OT_ID_PREFIX = "ot_s3_"
LT_ID_PREFIX = "lt_s3_"


def _new_stats() -> dict:
    return {
        "reviewed": 0,
        "published": 0,
        "skipped": 0,
        "failed": 0,
        "failures": [],  # [(row_id, reason)]
    }


def _risk_ot_rows(conn: sqlite3.Connection) -> list:
    rows, _ = ot_repo.list_all(conn, page_size=10_000)
    return [r for r in rows if r.id.startswith(OT_ID_PREFIX)]


def _risk_lt_rows(conn: sqlite3.Connection) -> list:
    rows, _ = lt_repo.list_all(conn, page_size=10_000)
    return [r for r in rows if r.id.startswith(LT_ID_PREFIX)]


def _published_ot_keys(conn: sqlite3.Connection) -> set[str]:
    """publish link 的已知端点集合：已发布 object_type 的 id + name（与 API 端一致）。"""
    known: set[str] = set()
    for o in ot_repo.list_published(conn):
        known.add(o.id)
        known.add(o.name)
    return known


def _review_then_publish_ot(
    conn: sqlite3.Connection,
    row: Any,
    stats: dict,
    *,
    dry_run: bool,
    projected: set[str] | None = None,
) -> None:
    """对单条 ot_s3_* 行执行 review(+publish)；校验失败记 failed 不落库。

    projected：dry-run 时累计"将要 published"的 ot id+name 集合，供链接投影校验。
    """
    if row.status == PUBLISHED:
        stats["skipped"] += 1
        return
    conflict = conflict_mod.check_object_type_name_conflict(conn, row.name)
    if conflict:
        stats["failed"] += 1
        stats["failures"].append((row.id, conflict["message"]))
        return
    err = validate_object_type(row)
    if err:
        stats["failed"] += 1
        stats["failures"].append((row.id, err))
        return
    if dry_run:
        stats["reviewed"] += 1
        stats["published"] += 1
        if projected is not None:
            projected.add(row.id)
            projected.add(row.name)
        return
    if row.status == DRAFT:
        ot_repo.transition_status(conn, row.id, REVIEWED)
        stats["reviewed"] += 1
    ot_repo.transition_status(conn, row.id, PUBLISHED)
    stats["published"] += 1


def _review_then_publish_lt(
    conn: sqlite3.Connection,
    row: Any,
    stats: dict,
    *,
    dry_run: bool,
    projected: set[str] | None = None,
) -> None:
    """对单条 lt_s3_* 行执行 review(+publish)；端点未 published 记 failed。

    端点校验：真实模式读 DB 已 published 集合（对象先于链接发布）；
    dry-run 用 projected（已投影发布的 ot id+name）。
    """
    if row.status == PUBLISHED:
        stats["skipped"] += 1
        return
    if conflict_mod.check_link_type_name_conflict(conn, row.name):
        stats["failed"] += 1
        stats["failures"].append((row.id, "与内置链接同名，拒绝 publish"))
        return
    known = projected if dry_run else _published_ot_keys(conn)
    err = validate_link_type(row, known)
    if err:
        stats["failed"] += 1
        stats["failures"].append((row.id, err))
        return
    if dry_run:
        stats["reviewed"] += 1
        stats["published"] += 1
        return
    if row.status == DRAFT:
        lt_repo.transition_status(conn, row.id, REVIEWED)
        stats["reviewed"] += 1
    lt_repo.transition_status(conn, row.id, PUBLISHED)
    stats["published"] += 1


def publish(ontology_path: str | Path, *, dry_run: bool = False) -> dict:
    """对 ot_s3_*/lt_s3_* 行依序执行既有 review/publish 服务函数到 published。

    幂等：已 published 行跳过（零变更零报错）。返回摘要 dict。
    """
    path = Path(ontology_path)
    if not path.exists():
        raise SystemExit(
            f"[publish-risk-ontology] 本体库不存在: {path} —— 先跑 seed 脚本"
            f"（scripts/seed_builder_from_risk_ontology.py）或先启动演示服务"
        )
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    ot_stats = _new_stats()
    lt_stats = _new_stats()
    # dry-run 投影：累计"将要 published"的 ot id+name，供链接端点校验
    projected: set[str] = set()
    if dry_run:
        projected = _published_ot_keys(conn)
    try:
        # 先对象后链接：link publish 校验要求两端对象已 published
        for row in _risk_ot_rows(conn):
            _review_then_publish_ot(
                conn, row, ot_stats, dry_run=dry_run, projected=projected
            )
        for row in _risk_lt_rows(conn):
            _review_then_publish_lt(
                conn, row, lt_stats, dry_run=dry_run, projected=projected
            )
    finally:
        conn.close()

    # 行数 = skipped + failed + published（每行至多一次 publish 动作；reviewed 是流转子步骤）
    total = {
        "objects": ot_stats["skipped"] + ot_stats["failed"] + ot_stats["published"],
        "links": lt_stats["skipped"] + lt_stats["failed"] + lt_stats["published"],
    }
    return {
        "db": str(path),
        "dry_run": dry_run,
        "object_types": ot_stats,
        "link_types": lt_stats,
        "summary": {
            "objects": total["objects"],
            "links": total["links"],
            "reviewed": ot_stats["reviewed"] + lt_stats["reviewed"],
            "published": ot_stats["published"] + lt_stats["published"],
            "skipped": ot_stats["skipped"] + lt_stats["skipped"],
            "failed": ot_stats["failed"] + lt_stats["failed"],
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--ontology-db",
        default=str(DEFAULT_ONTOLOGY_DB),
        help=f"目标本体库（默认演示库 {DEFAULT_ONTOLOGY_DB}）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只投影将要 review/publish 的行数与校验结果，不落库",
    )
    args = parser.parse_args(argv)
    print(
        json.dumps(
            publish(args.ontology_db, dry_run=args.dry_run),
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
