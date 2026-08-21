"""P3 approved 候选入注册表（设计 §4）：对象/链接注册 + mappings 血缘 + self_check + 审计。

- object：复用 registry_loader._build_dynamic_model 生成 Pydantic 类（补 ownership 标注，
  R4）+ Registry.register_object_type；pk 取自证据/源表列，source_table = 候选源表；
- link：从候选证据解析端点/基数/fk，端点未注册 → 跳过并记 error（R1：演示对象注册等
  Jack 决定，此处只做机制并如实报错）；复用 _derive_inverse_name 推导反向名；
- attribute：不单独注册，归并进所属对象 property_schema（设计 §4.1），仅记血缘；
- 血缘：mapping/repo.create 落 mappings 表（status='published'）；
- 审计：action_name='mapping_publish', source='publish'（P3 引入 source 枚举值，见 store）；
- 发布后跑 registry.self_check()：0 error 才接受（机验，设计 §4.1）。
"""

from __future__ import annotations

import json
import re
from typing import Any

from src.builder.mapping import repo as mapping_repo
from src.builder.mapping.annotate import APPROVED, MappingCandidateService
from src.builder.registry_loader import _build_dynamic_model, _derive_inverse_name
from src.ontology.links import LinkTypeDef
from src.ontology.objects import OWN_SOURCE, ObjectTypeDef
from src.ontology.registry import Registry
from src.runtime.audit import AuditLog, AuditRecord
from src.runtime.permissions import PermissionService, resolve_human_subject
from src.runtime.store import Store

PUBLISH_SOURCE = "publish"
AUDIT_ACTION_PUBLISH = "mapping_publish"
AUDIT_ACTOR = "human"  # audit_log.actor CHECK 白名单 ('human','llm','api')
PAGE_ALL = 1_000_000
SELF_CHECK_ERROR_CODE = "SELF_CHECK_FAILED"  # 发布后自检失败（P2-7 回滚本批）

_API_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")


class PublishError(ValueError):
    """发布前置校验失败（目标缺失/重复/信息不足），跳过并记 error 不静默。"""


def _to_snake(name: str) -> str:
    """PascalCase/任意名 → snake_case api_name（与 object_types.api_name 同算法）。"""
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    s = s.lower()
    s = re.sub(r"[^a-z0-9_]", "_", s)
    s = re.sub(r"_+", "_", s)
    return s.strip("_")


def _mark_source_ownership(model) -> type:
    """补字段 ownership=source-backed 标注（R4：_build_dynamic_model 不自带，
    self_check 的 FIELD_MISSING_OWNERSHIP 靠此通过；DES 源列均为源系统权威）。"""
    for fname in model.model_fields:
        extra = model.model_fields[fname].json_schema_extra or {}
        model.model_fields[fname].json_schema_extra = {
            **extra,
            "ownership": OWN_SOURCE,
        }
    return model


def _minimal_schema(candidate) -> dict:
    """候选无 property_schema 证据时的最小 schema：源字段即 pk 的单字段对象。"""
    field = candidate.source_field or "id"
    return {
        "type": "object",
        "properties": {
            field: {"type": "string", "description": f"源列 {candidate.source_field} 自动派生"}
        },
        "required": [field],
    }


def _build_object_defn(candidate):
    """object 候选 → ObjectTypeDef（property_schema 取证据，缺则最小 schema）。"""
    name = candidate.target
    schema = candidate.evidence_json.get("property_schema") or _minimal_schema(candidate)
    model = _mark_source_ownership(_build_dynamic_model(schema, name))
    api_name = _to_snake(name)
    if not _API_NAME_RE.match(api_name):
        raise PublishError(f"对象 api_name 非法: {api_name!r}（源 name={name!r}）")
    required = schema.get("required") or []
    pk = (
        candidate.evidence_json.get("pk_field")
        or (required[0] if required else None)
        or candidate.source_field
        or "id"
    )
    return ObjectTypeDef(
        name=name,
        api_name=api_name,
        description=f"P3 映射发布：{candidate.source_table}.{candidate.source_field or ''}",
        model=model,
        pk_field=pk,
        title_field=pk,
        source_table=candidate.source_table,
    )


def _build_link_defn(candidate, registry: Registry) -> LinkTypeDef:
    """link 候选 → LinkTypeDef；端点/基数信息从证据取，不足或端点未注册则抛 PublishError。"""
    ev = candidate.evidence_json
    source_type = ev.get("source_type") or ev.get("source_object")
    target_type = ev.get("target_type") or ev.get("target_object")
    cardinality = ev.get("cardinality")
    fk_field = ev.get("fk_field") or candidate.source_field
    if not (source_type and target_type):
        raise PublishError(f"链接端点信息不足（证据缺 source_type/target_type）: {candidate.target}")
    if cardinality not in ("N:1", "1:N"):
        raise PublishError(f"链接基数 {cardinality!r} 超出 MVP（N:1/1:N）: {candidate.target}")
    if not registry.has_object_type(source_type) or not registry.has_object_type(target_type):
        raise PublishError(
            f"链接端点未注册: {source_type} -> {target_type}（先发布端点对象）"
        )
    target_api = registry.object_type(target_type).api_name
    return LinkTypeDef(
        name=candidate.target,
        source_type=source_type,
        target_type=target_type,
        cardinality=cardinality,
        fk_field=fk_field,
        inverse_name=_derive_inverse_name(candidate.target, target_api),
        description=f"P3 映射发布：{candidate.source_table}.{candidate.source_field or ''}",
    )


def _lineage_kwargs(candidate, defn: Any) -> dict:
    """mapping/repo.create 血缘行参数（按 kind 分派）。"""
    if candidate.kind == "object":
        return {
            "entity_class": defn.name,
            "field_mapping": [
                {
                    "column": candidate.source_field or candidate.target,
                    "property_name": defn.pk_field,
                    "is_technical": False,
                    "inferred_type": "string",
                    "is_pk": True,
                }
            ],
        }
    return {
        "entity_class": candidate.target,
        "field_mapping": [],
        "fk_mappings": [
            {
                "link_id": candidate.target,
                "source_field": candidate.source_field,
                "target_field": defn.fk_field,
                "target_table": defn.target_type,
                "cardinality": defn.cardinality,
                "detection_method": candidate.evidence_json.get("method", "publish"),
            }
        ],
        "cardinalities": {candidate.target: defn.cardinality},
    }


def _audit_publish_on(
    conn, audit: AuditLog, actor: str, candidate, defn: Any, outcome: str, error_code: str | None = None,
) -> None:
    """落 source='publish' 审计（P2-7：走调用方单事务，commit 由外部负责）。"""
    audit.append_on(
        conn,
        AuditRecord(
            action_name=AUDIT_ACTION_PUBLISH,
            actor=AUDIT_ACTOR,
            actor_detail=f"cli:{actor}",
            outcome=outcome,
            error_code=error_code,
            detail_json=json.dumps(
                {
                    "candidate_id": candidate.candidate_id,
                    "kind": candidate.kind,
                    "target": candidate.target,
                    "registered": defn.name,
                    "source_table": candidate.source_table,
                },
                ensure_ascii=False,
            ),
            source=PUBLISH_SOURCE,
        ),
    )


def _permission_service(store: Store) -> PermissionService:
    """默认 approve 权限判定器：从 store 的 permission_policies 表加载（gate 恒开）。"""
    return PermissionService(store, Registry())


def _prepare_object(cand, registry: Registry) -> ObjectTypeDef:
    """object 候选前置校验（P1-3 ④ + §4.1）：去重 / pk / source_table，通过即返回 defn。"""
    if registry.has_object_type(cand.target):
        raise PublishError(f"对象已注册，拒绝重复注册（防静默覆盖）: {cand.target}")
    defn = _build_object_defn(cand)
    if defn.pk_field not in defn.model.model_fields:
        raise PublishError(f"对象 pk {defn.pk_field} 不在模型字段（OBJECT_PK_MISSING 前置挡）")
    if not defn.source_table:
        raise PublishError(f"对象缺 source_table（OBJECT_NO_SOURCE_TABLE 前置挡）: {cand.target}")
    return defn


def _prepare_link(cand, registry: Registry) -> LinkTypeDef:
    """link 候选前置校验（§4.1）：端点已注册 / 基数 / 去重，通过即返回 defn。"""
    defn = _build_link_defn(cand, registry)
    if any(l.name == defn.name for l in registry.link_types()):
        raise PublishError(f"链接已注册，拒绝重复注册: {defn.name}")
    return defn


def _prepare_publish_batch(rows, perm, subject, registry: Registry, report: dict) -> list[tuple]:
    """阶段 0：逐个候选过 approve 门 + 去重/pk/source/端点；失败记 error 不入批，返回本批 (cand, defn)。"""
    prepared: list[tuple] = []
    for cand in rows:
        try:
            if cand.kind not in ("object", "link"):
                report["skipped"].append(
                    {
                        "candidate_id": cand.candidate_id,
                        "reason": "attribute 归并进所属对象 property_schema，不单独注册",
                    }
                )
                continue
            if not perm.decide(subject, cand.target, "approve").allowed:
                raise PublishError(
                    f"发布前 approve 权限复核失败: {subject.id} 对 {cand.target} 无 approve 权限"
                )
            if cand.kind == "object":
                defn = _prepare_object(cand, registry)
            else:
                defn = _prepare_link(cand, registry)
            prepared.append((cand, defn))
        except PublishError as exc:
            report["errors"].append(
                {"candidate_id": cand.candidate_id, "kind": cand.kind, "reason": str(exc)}
            )
        except ValueError as exc:
            report["errors"].append(
                {"candidate_id": cand.candidate_id, "kind": cand.kind, "reason": f"注册失败: {exc}"}
            )
    return prepared


def _write_lineage(store: Store, prepared: list[tuple]) -> list[str]:
    """阶段 1：血缘先落（单连接单事务）；任一步失败整批回滚（Registry 未注册，无孤儿）。"""
    lineage_ids: list[str] = []
    if not prepared:
        return lineage_ids
    conn = store.ontology_conn()
    try:
        for cand, defn in prepared:
            row = mapping_repo.create(
                conn,
                ontology_id="default",
                source_table=(
                    defn.source_table if cand.kind == "object" else cand.source_table
                ),
                status="published",
                commit=False,
                **_lineage_kwargs(cand, defn),
            )
            lineage_ids.append(row.id)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    return lineage_ids


def _register_batch(registry: Registry, prepared: list[tuple], report: dict) -> None:
    """阶段 2：注册后置（血缘已落，才注册内存 Registry）。"""
    for cand, defn in prepared:
        if cand.kind == "object":
            registry.register_object_type(defn)
            report["published_objects"].append(cand.target)
        else:
            registry.register_link_type(defn)
            report["published_links"].append(cand.target)


def _rollback_batch(store: Store, registry: Registry, audit, actor, prepared, lineage_ids) -> None:
    """阶段 3 error 回滚：卸载注册 + 删除血缘 + 落 failed 审计（设计 §4.1：0 error 才接受）。"""
    for cand, defn in prepared:
        if cand.kind == "object":
            registry.unregister_object_type(defn.name)
        else:
            registry.unregister_link_type(defn.name)
    conn = store.ontology_conn()
    try:
        for lid in lineage_ids:
            conn.execute("DELETE FROM mappings WHERE id=?", (lid,))
        for cand, defn in prepared:
            _audit_publish_on(conn, audit, actor, cand, defn, "failed", SELF_CHECK_ERROR_CODE)
        conn.commit()
    finally:
        conn.close()


def _audit_publish_applied(store: Store, audit, actor, prepared) -> None:
    """阶段 3 ok：自检通过才落 applied 审计（单事务；血缘已先落）。"""
    if not prepared:
        return
    conn = store.ontology_conn()
    try:
        for cand, defn in prepared:
            _audit_publish_on(conn, audit, actor, cand, defn, "applied")
        conn.commit()
    finally:
        conn.close()


def publish_approved(
    store: Store,
    registry: Registry,
    *,
    actor: str = "cli",
    permission: PermissionService | None = None,
) -> dict[str, Any]:
    """发布 approved 候选入注册表：血缘先落 → 注册后置 → 自检回滚（P2-7，§4.1）。

    前置校验（P1-3 ④ + §4.1）：待发布候选（对象/链接）复核 approve 权限与 human 来源（V9）、
    去重/pk/source/端点；血缘同事务先落库；自检 error 回滚本批并落 failed 审计。
    attribute 不单独注册（随对象 property_schema 归并）。
    """
    service = MappingCandidateService(store, registry)
    rows, total = service.list(status=APPROVED, page=1, page_size=PAGE_ALL)
    audit = AuditLog(store)
    perm = permission or _permission_service(store)
    subject = resolve_human_subject(actor)  # V9：发布 actor 必须解析为 human（agent 拒）
    report: dict[str, Any] = {
        "scanned": total,
        "published_objects": [],
        "published_links": [],
        "skipped": [],
        "errors": [],
        "rolled_back": False,
    }
    # 阶段 0：前置校验（approve 门 + 去重 + pk/source/端点），失败记 error 不入批。
    # attribute 不单独注册 → 先跳过（不要求 approve 策略），对象/链接逐个过门。
    prepared = _prepare_publish_batch(rows, perm, subject, registry, report)
    # 阶段 1：血缘先落（同事务）——全部本批候选血缘，任一步失败整批回滚（Registry 未注册）
    lineage_ids = _write_lineage(store, prepared)
    # 阶段 2：注册后置（血缘已落，才注册内存 Registry）
    _register_batch(registry, prepared, report)
    # 阶段 3：自检（设计 §4.1：0 error 才接受）；error → 回滚本批
    error_issues = [i for i in registry.self_check() if i.severity == "error"]
    if prepared and error_issues:
        _rollback_batch(store, registry, audit, actor, prepared, lineage_ids)
        report["published_objects"] = []  # 已回滚，published 语义 = 最终持久
        report["published_links"] = []
        report["rolled_back"] = True
    elif prepared:
        _audit_publish_applied(store, audit, actor, prepared)  # 自检通过才落 applied 审计
    report["self_check"] = {
        "ok": not error_issues,
        "error_issues": [i.model_dump() for i in error_issues],
    }
    return report


__all__ = [
    "PUBLISH_SOURCE",
    "PublishError",
    "publish_approved",
]
