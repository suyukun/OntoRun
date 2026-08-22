"""P4 数据权限下沉（设计 §2）：metrics.db 对象级权限视图（DuckDB）。

依据 docs/P4-权限会话审计设计_v0.1.md §2（对象级下沉 + 属性级标注分层）：
- §2.1 分层：语义层（P2 已做）= decide(read) + visible_attributes 过滤返回列（对象/属性级
  标注）；数据层（本模块）= DuckDB 对象级视图强制——按对象类型读权限建可见视图
  （deny 对象不建视图），契约执行器查询强制走视图（对象级强制，属性级仍靠语义层标注）；
- §2.2 实现形态：create_permission_views(...) → DuckDB CREATE VIEW（每对象一张
  perm_<object_type>，内容 = 该对象全部物化表 UNION ALL BY NAME + metric_id 判别列）；
- §6 视图重建时机：demo 规模每次 decide 后重建可接受；执行器查询前 ensure（视图缺失/
  为空 → 对象级 deny 语义 fail-closed 拒答，绝不回落直查物化表，见 executor._metric_source）。

判别列说明：同一对象多指标物化表的列名可碰撞（如 Material 多个指标都有 matnr 维度），
单张视图须可区分行来源 → 每行带 metric_id（查询侧 WHERE 过滤，返回列显式选择不含它），
防串表污染（行为与直查物化表一致）。
"""

from __future__ import annotations

from pathlib import Path

import duckdb

from src.des.contract.permissions import PermissionDecider
from src.des.metrics import MetricDef, MetricRegistry, metric_table_name
from src.runtime.permissions import PermissionSubject

# 权限视图名前缀（设计 §2.2：perm_<object_type>，与物化表 metric_<id> 前缀隔离）
PERMISSION_VIEW_PREFIX = "perm_"


class PermissionViewError(Exception):
    """权限视图创建失败（fail-fast，不静默）。"""


def permission_view_name(object_type: str) -> str:
    """权限视图名：perm_<object_type>（设计 §2.2；对象名为注册表常量，无注入面）。"""
    return PERMISSION_VIEW_PREFIX + object_type


def _sql_literal(value: str) -> str:
    """SQL 字符串字面量（单引号转义；metric_id 为 M7 snake_case 常量，纵深防御）。"""
    return "'" + value.replace("'", "''") + "'"


def _view_sql(object_type: str, obj_metrics: tuple[MetricDef, ...]) -> str:
    """单对象权限视图 SQL：全部物化表 UNION ALL BY NAME + metric_id 判别列（全列透传）。

    列 = 各物化表列并集（BY NAME 对齐，缺失列自动 NULL）；metric_id 为分支常量，
    查询侧按它过滤，防同对象多指标列名碰撞串表（如多个 Material 指标都有 matnr 维度）。
    """
    branches = [
        f"SELECT {_sql_literal(m.metric_id)} AS metric_id, * "
        f"FROM {metric_table_name(m.metric_id)}"
        for m in obj_metrics
    ]
    return (
        f"CREATE OR REPLACE VIEW {permission_view_name(object_type)} AS\n"
        + "\nUNION ALL BY NAME\n".join(branches)
    )


def create_permission_views(
    metrics_db: str | Path,
    metrics: MetricRegistry,
    permission_registry: PermissionDecider,
    subject: PermissionSubject,
) -> dict[str, list[str]]:
    """按对象类型读权限重建 metrics.db 权限视图（设计 §2.2，幂等可重跑）。

    - allow 对象：CREATE OR REPLACE VIEW perm_<object_type>（内容 = 该对象全部物化表
      UNION ALL BY NAME + metric_id 判别列）；
    - deny 对象：DROP VIEW IF EXISTS（不建视图 → 查询路径视图缺失 = fail-closed 拒答）；
    - 返回 {object_type: [metric_id, ...]}（本次建成视图的对象及其覆盖指标）。

    重建时机（设计 §6）：demo 规模每次 decide 后重建可接受；契约执行器查询前 ensure
    视图存在（缺失/为空即对象级 deny 拒答，见 executor._metric_source）。
    """
    db = Path(metrics_db)
    if not db.is_file():
        raise PermissionViewError(f"metrics.db 缺失: {db}（先运行 materialize_metrics）")
    by_object: dict[str, list[MetricDef]] = {}
    for m in metrics.metrics:
        by_object.setdefault(m.object_type, []).append(m)
    con = duckdb.connect(str(db))
    try:
        created: dict[str, list[str]] = {}
        for object_type in sorted(by_object):
            obj_metrics = tuple(by_object[object_type])
            view = permission_view_name(object_type)
            decision = permission_registry.decide(subject, object_type, "read")
            if not decision.allowed:
                con.execute(f"DROP VIEW IF EXISTS {view}")
                continue
            try:
                con.execute(_view_sql(object_type, obj_metrics))
            except Exception as exc:  # 物化表缺失/类型冲突即 fail-fast
                raise PermissionViewError(f"权限视图创建失败 {view}: {exc}") from exc
            created[object_type] = [m.metric_id for m in obj_metrics]
        return created
    finally:
        con.close()


__all__ = [
    "PERMISSION_VIEW_PREFIX",
    "PermissionViewError",
    "create_permission_views",
    "permission_view_name",
]
