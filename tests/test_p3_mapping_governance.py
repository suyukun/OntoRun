"""P3 映射治理门禁测试（docs/P3-映射治理设计_v0.1.md §5 门禁到可机验断言）。

覆盖 P3 门禁（机验口径，全部 tmp_path 临时双库 + 临时 GT 文件，不碰真实 data/）：

1. 候选生成与分级（§1.3）：annotate_mapping_candidates 对 DES 语义 + FK 检测产出候选，
   classify 档位自洽（confidence_level == classify(score)），高（score≥0.9）自动过，
   中/低进审核队列；C4 未注册 object target 进待补录队列（draft，不静默丢弃），
   attribute target 跳过（待补录计数）。
2. 审核流转（§2）：review CLI export（CSV 含 header 快照）→ import accept/reject/conflict
   → 状态机合法 + mapping_review_history 留痕 + audit source='review'；非法裁决（未知
   candidate_id / 非法 decision）fail-fast 记失败不静默；approved 终态锁定不可改；
   approve 权限门（P1-3：无策略 fail-closed、agent reviewer 一律拒 V9）+ 单连接单事务
   原子性（P2-6：中途失败整体回滚）+ corrected_target 格式/C4 校验。
3. 入注册表（§4）：approved link → publish_approved 注册 + self_check 0 error + mappings
   血缘落表 + audit(mapping_publish, source='publish')；同名对象重复注册拒绝（防静默覆盖）；
   approve 权限复核（P1-3 ④）+ self_check 有 error 回滚本批（P2-7）；
   对象注册机制经两注册表路径锁定（C4 与重复检查对同一 registry 互斥，见测试内说明）。
4. 阈值校准（§3）：GT 加载合法/非法 fail-fast；recall@k（full_recall@5≥0.80 门禁 +
   top-5 与 top-1 区分）；auto_recall 与 full_recall 双口径显式（差值=人工审核增量）；
   网格扫描 medium≤high、选择规则（满 recall 下 auto_coverage 最大）、报告含默认行与最优行、
   写 mapping_thresholds.yaml；无解如实回退默认 (0.9,0.6)；auto_precision 分母含非 GT 键
   （P2-5）+ unvalidated 报告；medium 不参与选优报告注明（P2-9）。
5. 变更影响（§4.3）：analyze_change → MappingChangeReport 完整可查（实跑）；管道编排
   （§1.1）run_mapping_pipeline → PipelineReport，C4 跳过显式 skipped_c4 计数。
6. 安全/一致（§5）：审计链 verify_integrity 全绿（含 review/publish 记录后仍自洽）、
   mapping_review_history/audit_log WORM（禁改删）、发布后注册表无孤儿（血缘 entity_class
   均指向已注册对象/链接）、self_check 0 error。

约束：不跑全量 pytest；只跑本文件 + ruff；修实现不修测试。
"""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

import pytest
import yaml

from src.builder.mapping import calibrate as cal
from src.builder.mapping import review as review_mod
from src.builder.mapping.annotate import (
    APPROVED,
    DRAFT,
    REVIEWING,
    MappingCandidate,
    MappingCandidateService,
    annotate_mapping_candidates,
    classify,
)
from src.builder.mapping.fk_detection import DetectedLink
from src.builder.mapping.publish import publish_approved
from src.builder.status_machine import IllegalTransitionError
from src.ontology import build_registry
from src.ontology.objects import OWN_SOURCE, field_ownership
from src.ontology.registry import Registry
from src.runtime.audit import AuditLog, AuditRecord
from src.runtime.store import Store


# ----------------------------------------------------------------------
# 工具 / fixtures
# ----------------------------------------------------------------------
def _cand(
    candidate_id: str,
    *,
    kind: str = "attribute",
    target: str = "name",
    score: float = 0.7,
    source_table: str = "erp.MARA",
    source_field: str = "name",
    evidence_json: dict | None = None,
) -> MappingCandidate:
    """attribute 默认（target 需为已注册对象字段，C4）；object/link 显式传 kind。"""
    return MappingCandidate(
        candidate_id=candidate_id,
        kind=kind,
        source_table=source_table,
        source_field=source_field,
        target=target,
        confidence_score=score,
        confidence_level=classify(score),
        evidence_json=evidence_json or {},
    )


def _attr(candidate_id: str, source_field: str, target: str, score: float) -> MappingCandidate:
    """校准场景用 attribute 候选（erp.MARA 源表，target 为 Material 字段/已注册字段）。"""
    return _cand(candidate_id, target=target, score=score, source_field=source_field)


def _write_csv(path: Path, rows: list[list[str]]) -> None:
    """写裁决 CSV（首行 = header）。"""
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["candidate_id", "decision", "corrected_target", "note"])
        w.writerows(rows)


def _write_gt(path: Path, entries: list[dict]) -> None:
    """写 GT 文件（设计 §3.1 entries 列表形态）。"""
    path.write_text(
        yaml.safe_dump(
            {"version": "0.1", "domain": "manufacturing", "entries": entries},
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _grant_approve(
    store: Store, object_type: str, subject_id: str = "jack", policy_id: str | None = None
) -> None:
    """直接落 approve 策略（绕过 V1：目标为 link/属性名等非对象字符串，直插 permission_policies）。

    门禁测试在测「approve 门本身」，policy 的创建走直插（PermissionService.create 的 V1
    对象校验不适用 link/属性目标）。
    """
    conn = store.ontology_conn()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO permission_policies (policy_id, object_type, operation, "
            "effect, subject_kind, subject_id, role_id, scope, attributes_json, version, "
            "created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                policy_id or f"appr-{object_type}-{subject_id}",
                object_type,
                "approve",
                "allow",
                "human",
                subject_id,
                "",
                "object",
                "[]",
                1,
                "",
                "",
            ),
        )
        conn.commit()
    finally:
        conn.close()


def _seed_calibration(service: MappingCandidateService) -> list[dict]:
    """构造 10 条 GT 场景候选（设计 §3.2 双口径数据）：
    - 5 条正确高置信（score 0.95，自动覆盖）；
    - 3 条正确中置信（score 0.75，进队列人工补，非自动覆盖）；
    - plm_code 前额外一条高分错误候选（order_id@0.99）→ 验证 top-5 语义（hit@5 但 miss@1）；
    - 1 条仅错误候选（matnr：order_id@0.95，已注册字段但目标不对）→ recall 漏报；
    - 1 条 link（material.codes@0.5）。
    返回全部 GT entries（10 条）。
    """
    correct_high = [
        ("name", "name"), ("base_unit", "base_unit"),
        ("material_group", "material_group"), ("material_type", "material_type"),
        ("old_code", "old_code"),
    ]
    correct_med = [("plm_code", "plm_code"), ("mes_code", "mes_code"), ("created_date", "created_date")]
    wrong_only = [("matnr", "matnr")]  # 仅错误候选（目标错误但字段已注册，C4 可建）
    for i, (sf, tgt) in enumerate(correct_high):
        service.create(_attr(f"ch{i}", sf, tgt, 0.95))
    for i, (sf, tgt) in enumerate(correct_med):
        service.create(_attr(f"cm{i}", sf, tgt, 0.75))
    # plm_code 前压一条高分错误候选（top-1 被顶掉，验证 hit@5 vs hit@1）
    service.create(_attr("plm_wrong", "plm_code", "order_id", 0.99))
    for i, (sf, _tgt) in enumerate(wrong_only):
        service.create(_attr(f"w{i}", sf, "order_id", 0.95))
    service.create(
        MappingCandidate(
            candidate_id="lk0", kind="link", source_table="erp.MARA",
            source_field="matnr", target="material.codes",
            confidence_score=0.5, confidence_level=classify(0.5),
        )
    )
    entries: list[dict] = [
        {"source_table": "erp.MARA", "source_field": sf, "kind": "attribute", "gt_target": tgt}
        for sf, tgt in correct_high + correct_med + wrong_only
    ]
    entries.append({"source_table": "erp.MARA", "source_field": "matnr", "kind": "link", "gt_target": "material.codes"})
    return entries


@pytest.fixture
def store(tmp_path) -> Store:
    """每个测试独立临时双库（source + ontology），绝不碰真实 data/。"""
    s = Store(tmp_path / "source.db", tmp_path / "ontology.db")
    s.migrate()
    return s


@pytest.fixture
def registry() -> Registry:
    return build_registry()


@pytest.fixture
def service(store, registry) -> MappingCandidateService:
    return MappingCandidateService(store, registry)


@pytest.fixture
def audit(store) -> AuditLog:
    return AuditLog(store)


# ======================================================================
# ① 候选生成与分级（门禁 1）
# ======================================================================
def test_candidate_generation_des_and_links(store, registry) -> None:
    """DES 语义高置信自动过；FK 检测中/低进队列；C4 未注册 target 与命名列跳过。"""
    source = {
        "source_table": "erp.MARA",
        "columns": [
            {"column": "name", "inferred_type": "string", "is_technical": False},
            {"column": "material_type", "inferred_type": "string", "is_technical": False},
            {"column": "etl_loaded_at", "inferred_type": "datetime", "is_technical": True},
        ],
        "des_mappings": [
            {"kind": "object", "target": "Material"},
            {"kind": "attribute", "target": "matnr", "source_field": "material_number"},
            {"kind": "object", "target": "GhostObj"},  # C4 未注册 → 跳过
        ],
        "detected_links": [
            DetectedLink(
                link_id="lnk_med", source_field="customer_id", target_field="customer_id",
                cardinality="N:1", detection_method="exact_match",
                match_summary={"direct_match_rows": 20, "format_normalized_match_rows": 5,
                               "unmatched_rows": 5, "total_rows": 30},
            ),
            DetectedLink(
                link_id="lnk_low", source_field="matnr", target_field="matnr",
                cardinality="N:1", detection_method="exact_match",
                match_summary={"direct_match_rows": 2, "format_normalized_match_rows": 1,
                               "unmatched_rows": 27, "total_rows": 30},
            ),
        ],
    }
    persisted = annotate_mapping_candidates(source, registry, store=store)
    # 2 des（object/attribute）+ 2 fk link + GhostObj（object 未注册 → 待补录 draft）
    assert len(persisted) == 5
    kinds = {c.kind for c in persisted}
    assert kinds == {"object", "attribute", "link"}
    objs = [c for c in persisted if c.kind == "object"]
    attrs = [c for c in persisted if c.kind == "attribute"]
    links = sorted((c for c in persisted if c.kind == "link"), key=lambda c: c.confidence_score, reverse=True)
    assert [c.target for c in objs] == ["Material", "GhostObj"]
    assert [c.target for c in attrs] == ["matnr"]
    assert [c.target for c in links] == ["lnk_med", "lnk_low"]
    # 档位自洽：confidence_level == classify(score)
    for c in persisted:
        assert c.confidence_level == classify(c.confidence_score)
    # 已注册 object（Material）高置信自动过；未注册 object（GhostObj）进待补录 draft 不自动过
    mat = next(c for c in objs if c.target == "Material")
    ghost = next(c for c in objs if c.target == "GhostObj")
    assert mat.confidence_level == "high" and mat.review_status == APPROVED and mat.auto_approved
    assert ghost.review_status == DRAFT and not ghost.auto_approved
    assert ghost.evidence_json.get("c4") == "pending_registration"  # 待补录标记（不静默丢弃）
    # attribute 高置信（DES score 1.0）自动过
    for c in attrs:
        assert c.confidence_level == "high"
        assert c.review_status == APPROVED and c.auto_approved is True
    # 中/低进审核队列
    assert links[0].confidence_level == "medium" and links[0].review_status == DRAFT
    assert links[1].confidence_level == "low" and links[1].review_status == DRAFT
    assert all(not c.auto_approved for c in links)
    # 自动过留 auto 历史
    svc = MappingCandidateService(store, registry)
    hist = svc.list_history(mat.candidate_id)
    assert len(hist) == 1 and hist[0]["reviewer"] == "auto"
    # 命名 attribute 未入表（C4 跳过 → 待补录，attribute 不进队只计数）
    assert all(c.target not in ("Name", "MaterialType") for c in persisted)


def test_routing_auto_approved_iff_high(service) -> None:
    """管道级机验（设计 §1.3 机验 ②③ 重断言）：auto_approved ⟺ (score≥high ∧ approved ∧ 历史含 auto)。"""
    high = service.create(_cand("c-high", kind="object", target="Order", score=0.95))
    med = service.create(_cand("c-med", kind="object", target="Order", score=0.7))
    low = service.create(_cand("c-low", kind="object", target="Order", score=0.3))
    assert high.confidence_level == "high" and high.review_status == APPROVED and high.auto_approved
    assert [h["reviewer"] for h in service.list_history("c-high")] == ["auto"]
    assert med.confidence_level == "medium" and med.review_status == DRAFT and not med.auto_approved
    assert low.confidence_level == "low" and low.review_status == DRAFT and not low.auto_approved
    assert service.list_history("c-med") == []
    # 队列按 score 降序
    queued, total = service.list(status=DRAFT)
    assert total == 2
    assert [c.candidate_id for c in queued] == ["c-med", "c-low"]


# ======================================================================
# ② 审核流转（门禁 2）
# ======================================================================
def test_review_cli_export_import(tmp_path, store, service, audit) -> None:
    """导出 CSV 含 header 快照 → 导入 accept/reject/conflict → 状态机合法 + history + audit + 链完好。"""
    service.create(_cand("c-acc", target="order_id", source_field="order_no", score=0.7))
    service.create(_cand("c-rej", target="note", source_field="note", score=0.5))
    service.create(_cand("c-conf", target="total_cents", source_field="amount", score=0.6))
    # export：CSV 含 header（9 列快照）
    out = tmp_path / "batch.csv"
    res = review_mod.export_candidates(store, out, status="draft")
    assert res["exported"] == 3
    with open(out, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert list(rows[0].keys()) == review_mod.EXPORT_COLUMNS
    assert {r["candidate_id"] for r in rows} == {"c-acc", "c-rej", "c-conf"}
    # import：accept / reject / conflict（approve 权限门：jack 对三个目标均有 approve 策略）
    _grant_approve(store, "order_id", "jack")
    _grant_approve(store, "note", "jack")
    _grant_approve(store, "total_cents", "jack")
    dec = tmp_path / "decisions.csv"
    _write_csv(dec, [
        ["c-acc", "accept", "", "证据充分"],
        ["c-rej", "reject", "", "目标错误"],
        ["c-conf", "conflict", "", "二义性"],
    ])
    report = review_mod.import_decisions(store, dec, reviewer="jack")
    assert report["processed"] == 3
    assert report["accepted"] == 1 and report["rejected"] == 1 and report["conflicts"] == 1
    assert report["failed"] == 0
    # 状态机合法
    assert service.get("c-acc").review_status == APPROVED
    assert service.get("c-rej").review_status == "rejected"
    assert service.get("c-conf").review_status == DRAFT  # 冲突不流转，留队列
    # history 留痕（reject 走 draft→reviewing→rejected 两跳）
    assert len(service.list_history("c-acc")) == 1
    assert [h["to_status"] for h in service.list_history("c-rej")] == [REVIEWING, "rejected"]
    assert service.list_history("c-conf") == []
    # audit：source='review' 逐条落痕，conflict 带 MAPPING_CONFLICT
    rev, total = audit.query(action="mapping_review")
    assert total == 3
    assert all(a["source"] == "review" for a in rev)
    conflict_audit = [a for a in rev if a.get("error_code") == "MAPPING_CONFLICT"]
    assert len(conflict_audit) == 1
    assert conflict_audit[0]["outcome"] == "rejected"
    # 哈希链含 review 记录后仍自洽
    assert audit.verify_integrity()["ok"] is True


def test_review_import_invalid_fail_fast(tmp_path, store, service, audit) -> None:
    """非法裁决（未知 candidate_id / 非法 decision）fail-fast：记失败不静默，无部分成功。"""
    service.create(_cand("c-ok", target="order_id", score=0.7))
    dec = tmp_path / "bad.csv"
    _write_csv(dec, [
        ["ghost-id", "accept", "", ""],
        ["c-ok", "bogus", "", ""],
    ])
    report = review_mod.import_decisions(store, dec, reviewer="jack")
    assert report["failed"] == 2 and report["processed"] == 0
    reasons = " | ".join(f["reason"] for f in report["failures"])
    assert "候选不存在" in reasons and "非法/缺失 decision" in reasons
    # 无部分静默成功：c-ok 未被误处理
    assert service.get("c-ok").review_status == DRAFT
    assert audit.verify_integrity()["ok"] is True


def test_review_accept_corrected_registers(tmp_path, store, service, registry, audit) -> None:
    """accept + corrected_target：target 更新 + approved + 留痕；随后 publish 入注册表（链接）。"""
    service.create(
        _cand("c-link", kind="link", target="order.p3_customer", score=0.8,
              source_field="customer_id",
              evidence_json={"method": "fk_detection.detect_links", "source_type": "Order",
                             "target_type": "Customer", "cardinality": "N:1", "fk_field": "customer_id"})
    )
    # approve 权限门：jack 对 corrected 目标有 approve 策略；发布 actor 'cli' 同样需策略
    _grant_approve(store, "order.p3_supplier", "jack")
    _grant_approve(store, "order.p3_supplier", "cli")
    dec = tmp_path / "corrected.csv"
    _write_csv(dec, [["c-link", "accept", "order.p3_supplier", "修正目标"]])
    report = review_mod.import_decisions(store, dec, reviewer="jack")
    assert report["accepted"] == 1 and report["failed"] == 0
    c = service.get("c-link")
    assert c.target == "order.p3_supplier" and c.review_status == APPROVED
    assert len(service.list_history("c-link")) == 1
    # 发布阶段入注册表
    rep = publish_approved(store, registry)
    assert "order.p3_supplier" in rep["published_links"]
    assert rep["self_check"]["ok"] is True
    assert any(l.name == "order.p3_supplier" for l in registry.link_types())
    assert audit.verify_integrity()["ok"] is True


def test_approved_terminal_and_no_target_change(tmp_path, store, service) -> None:
    """approved 终态锁定（状态机不可流转）；CLI 对 approved 改 target 拒绝（变更走新候选）。"""
    service.create(_cand("c-t", target="order_id", score=0.7))
    service.transition("c-t", APPROVED, reviewer="jack")
    with pytest.raises(IllegalTransitionError):
        service.transition("c-t", "rejected", reviewer="jack")
    with pytest.raises(IllegalTransitionError):
        service.transition("c-t", DRAFT, reviewer="jack")
    # CLI：approved 上 accept + 不同 corrected_target → 拒绝该行
    dec = tmp_path / "t.csv"
    _write_csv(dec, [["c-t", "accept", "other_target", "想改"]])
    report = review_mod.import_decisions(store, dec, reviewer="jack")
    assert report["failed"] == 1
    assert any("approved 终态不可改 target" in f["reason"] for f in report["failures"])
    assert service.get("c-t").target == "order_id"  # 未变


# ======================================================================
# ③ 入注册表（门禁 3）
# ======================================================================
def test_approved_to_registry(store, service, registry, audit) -> None:
    """approved → 注册链接 + self_check 0 error + mappings 血缘落表 + audit(mapping_publish)。"""
    service.create(
        _cand("c-lnk", kind="link", target="order.p3_customer", score=0.8,
              source_field="customer_id",
              evidence_json={"method": "fk_detection.detect_links", "source_type": "Order",
                             "target_type": "Customer", "cardinality": "N:1", "fk_field": "customer_id"})
    )
    service.transition("c-lnk", APPROVED, reviewer="jack")
    service.create(_cand("c-attr", target="matnr", score=1.0))          # attribute → skip
    service.create(_cand("c-obj", kind="object", target="Material", score=1.0))  # 已注册 → error
    # publish actor 'cli' 的 approve 权限复核（P1-3 ④）
    _grant_approve(store, "order.p3_customer", "cli")
    _grant_approve(store, "Material", "cli")
    report = publish_approved(store, registry)
    assert "order.p3_customer" in report["published_links"]
    assert report["self_check"]["ok"] is True
    # 注册表可查
    assert any(l.name == "order.p3_customer" for l in registry.link_types())
    # mappings 血缘（status='published'）
    conn = store.ontology_conn()
    try:
        rows = conn.execute("SELECT entity_class, status FROM mappings").fetchall()
    finally:
        conn.close()
    assert any(r["entity_class"] == "order.p3_customer" and r["status"] == "published" for r in rows)
    # audit(mapping_publish, source='publish')
    pub, total = audit.query(action="mapping_publish")
    assert total == 1 and pub[0]["source"] == "publish"
    assert audit.verify_integrity()["ok"] is True


def test_registry_duplicate_rejected(store, service, registry) -> None:
    """同名对象重复注册拒绝（防静默覆盖）：已注册 target 的 object 候选发布报错，注册表无变化。"""
    before = sorted(o.name for o in registry.object_types())
    service.create(_cand("c-obj", kind="object", target="Material", score=1.0))
    _grant_approve(store, "Material", "cli")
    report = publish_approved(store, registry)
    assert report["published_objects"] == []
    assert any("已注册" in e["reason"] for e in report["errors"])
    assert sorted(o.name for o in registry.object_types()) == before


def test_publish_object_mechanism(tmp_path, store, registry) -> None:
    """对象注册机制：approved object → 新对象注册（api_name/pk/source_table/ownership）+ self_check 0 error。

    背景（设计 §4.1 vs C4）：C4 要求 object target 在 create 时已注册、publish 又拒绝已注册
    target，同一 registry 下两者互斥（R1 演示对象注册待 Jack 决定）。本测试用 create 时含 target
    的 registry 建候选（过 C4），发布时用不含 target 的 registry（过重复检查），锁定
    _publish_object 的注册机制本身（不把「未实现路径」当「通过」）。
    """
    reg_a = build_registry()  # 含 Material → C4 校验通过
    svc_a = MappingCandidateService(store, reg_a)
    svc_a.create(
        _cand("c-obj", kind="object", target="Material", score=1.0,
              source_field="matnr", evidence_json={"pk_field": "matnr"})
    )
    reg_b = Registry()  # 不含 Material → 重复检查通过，可注册
    _grant_approve(store, "Material", "cli")
    report = publish_approved(store, reg_b)
    assert report["published_objects"] == ["Material"]
    assert report["errors"] == []
    assert report["self_check"]["ok"] is True
    obj = reg_b.object_type("Material")
    assert obj.api_name == "material" and obj.pk_field == "matnr"
    assert obj.source_table == "erp.MARA"
    # R4：动态 model 字段 ownership 标注 source-backed（FIELD_MISSING_OWNERSHIP 靠此过）
    assert field_ownership(obj.model, "matnr") == OWN_SOURCE
    # 血缘落表
    conn = store.ontology_conn()
    try:
        row = conn.execute("SELECT entity_class, status FROM mappings").fetchone()
    finally:
        conn.close()
    assert row is not None and row["entity_class"] == "Material" and row["status"] == "published"


# ======================================================================
# ④ 阈值校准（门禁 4）
# ======================================================================
def test_gt_load_and_validate(tmp_path) -> None:
    """GT 加载合法（entries 列表 + 纯映射 dict 两种形态）；非法 fail-fast（kind/空 target/重复）。"""
    p = tmp_path / "gt.yaml"
    _write_gt(p, [{"source_table": "erp.MARA", "source_field": "name", "kind": "attribute", "gt_target": "name"}])
    gt = cal.load_ground_truth(p)
    assert gt == {"erp.MARA|name|attribute": "name"}
    # 纯映射 dict 形态（docstring：{candidate_key: true_target}）
    p2 = tmp_path / "gt_dict.yaml"
    p2.write_text(yaml.safe_dump({"erp.MARA|name|attribute": "name"}), encoding="utf-8")
    assert cal.load_ground_truth(p2) == gt
    # kind 枚举非法 → fail-fast
    p3 = tmp_path / "bad_kind.yaml"
    p3.write_text(yaml.safe_dump({"entries": [{"source_table": "t", "source_field": "f", "kind": "bogus", "gt_target": "x"}]}), encoding="utf-8")
    with pytest.raises(ValueError):
        cal.load_ground_truth(p3)
    # gt_target 空 → fail-fast
    p4 = tmp_path / "empty_target.yaml"
    p4.write_text(yaml.safe_dump({"entries": [{"source_table": "t", "source_field": "f", "kind": "attribute", "gt_target": "  "}]}), encoding="utf-8")
    with pytest.raises(ValueError):
        cal.load_ground_truth(p4)
    # 同 (source_table, source_field, kind) 重复 → fail-fast（设计 §3.1 不重复）
    p5 = tmp_path / "dup.yaml"
    p5.write_text(yaml.safe_dump({"entries": [
        {"source_table": "t", "source_field": "f", "kind": "attribute", "gt_target": "x"},
        {"source_table": "t", "source_field": "f", "kind": "attribute", "gt_target": "y"},
    ]}), encoding="utf-8")
    with pytest.raises(ValueError, match="重复"):
        cal.load_ground_truth(p5)


def test_recall_metrics(tmp_path, store, service) -> None:
    """recall@k 门禁：full_recall@5 ≥ 0.80；top-5 与 top-1 区分（高分错误候选顶掉 top-1）。"""
    entries = _seed_calibration(service)
    _write_gt(tmp_path / "gt.yaml", entries)
    gt = cal.load_ground_truth(tmp_path / "gt.yaml")
    assert len(gt) == 10
    r5 = cal.recall_at_k(store, gt, k=5)
    r1 = cal.recall_at_k(store, gt, k=1)
    # 9 条正确（5 high + 3 med + 1 link）命中 top-5；plm_code 被高分错误候选顶掉 top-1
    assert r5 == pytest.approx(9 / 10)
    assert r1 == pytest.approx(8 / 10)
    assert r5 >= cal.RECALL_GATE  # 门禁 full_recall@5 ≥ 0.80 保留
    assert r5 > r1  # top-5 语义可见（hit@5 ≠ hit@1）


def test_recall_auto_vs_full(tmp_path, store, service) -> None:
    """recall 双口径显式化（设计 §3.2）：auto_recall（仅高置信自动过）< full_recall（全量 approved）。"""
    entries = _seed_calibration(service)
    _write_gt(tmp_path / "gt.yaml", entries)
    gt = cal.load_ground_truth(tmp_path / "gt.yaml")
    full = cal.recall_at_k(store, gt, k=5)
    auto = cal.auto_coverage(store, gt, cal.FALLBACK_THRESHOLDS["high"])  # 默认 0.9 口径
    assert full == pytest.approx(0.9)
    assert auto == pytest.approx(0.5)  # 仅 5 条高置信自动过
    assert auto < full  # 差值 0.4 = 人工审核增量
    # 校准报告双口径显式
    rep = cal.calibrate(store, tmp_path / "gt.yaml")
    assert rep["full_recall_at_5"] == pytest.approx(0.9)
    assert rep["auto_recall_default"] == pytest.approx(0.5)
    assert (rep["full_recall_at_5"] - rep["auto_recall_default"]) > 0  # 差值非负显式


def test_calibrate_thresholds(tmp_path, store, service) -> None:
    """网格扫描合法（medium≤high）+ 选择规则（满 recall 下 auto_coverage 最大）+ 报告与 yaml 写入。"""
    entries = _seed_calibration(service)
    _write_gt(tmp_path / "gt.yaml", entries)
    gt = cal.load_ground_truth(tmp_path / "gt.yaml")
    scan = cal.grid_scan(store, gt)
    assert scan["rows"]
    assert all(r["medium"] <= r["high"] for r in scan["rows"])  # 约束 medium ≤ high
    assert scan["full_recall_at_5"] >= cal.RECALL_GATE
    best = scan["best"]
    assert best is not None
    # 选择规则：best = 满足约束下 auto_coverage 最大
    qualifying = [r for r in scan["rows"] if r["full_recall_at_5"] >= cal.RECALL_GATE]
    max_cov = max(r["auto_coverage"] for r in qualifying)
    assert best["auto_coverage"] == pytest.approx(max_cov)
    assert best["auto_coverage"] == pytest.approx(0.8)
    assert best["high"] == pytest.approx(0.7)
    # 报告含默认行 (0.9,0.6) 与最优行；阈值写入 mapping_thresholds.yaml
    out = tmp_path / "mapping_thresholds.yaml"
    rep = cal.calibrate(store, tmp_path / "gt.yaml", out_path=out)
    grid_pairs = {(r["high"], r["medium"]) for r in rep["grid_rows"]}
    assert (0.9, 0.6) in grid_pairs  # 默认行
    assert (best["high"], best["medium"]) in grid_pairs  # 最优行
    assert rep["recommended_thresholds"] == {"high": best["high"], "medium": best["medium"]}
    assert rep["fallback"] is False
    yaml_doc = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert yaml_doc["thresholds"] == rep["recommended_thresholds"]
    assert yaml_doc["gt_size"] == 10


def test_calibrate_no_solution_fallback(tmp_path) -> None:
    """无解回退：full_recall@5 < 0.80 → 如实回退默认 (0.9,0.6)，fallback=True 不静默。"""
    store = Store(tmp_path / "s.db", tmp_path / "o.db")
    store.migrate()
    service = MappingCandidateService(store, build_registry())
    service.create(_attr("x0", "name", "name", 0.95))
    _write_gt(tmp_path / "gt.yaml", [
        {"source_table": "erp.MARA", "source_field": sf, "kind": "attribute", "gt_target": sf}
        for sf in ("name", "base_unit", "material_group", "material_type", "old_code")
    ])
    rep = cal.calibrate(store, tmp_path / "gt.yaml", out_path=tmp_path / "mapping_thresholds.yaml")
    assert rep["fallback"] is True
    assert rep["recommended_thresholds"] == {"high": 0.9, "medium": 0.6}
    assert rep["full_recall_at_5"] < cal.RECALL_GATE
    yaml_doc = yaml.safe_load((tmp_path / "mapping_thresholds.yaml").read_text(encoding="utf-8"))
    assert yaml_doc["fallback"] is True
    assert yaml_doc["thresholds"] == {"high": 0.9, "medium": 0.6}


# ======================================================================
# ④b 审核 approve 权限门（P1-3）/ 原子性（P2-6）
# ======================================================================
def test_review_import_approve_gate_fail_closed(tmp_path, store, service, audit) -> None:
    """P1-3 ①：无 approve 策略 → accept 被拒（fail-closed），无部分成功、无审计。"""
    service.create(_cand("c-gate", target="order_id", source_field="order_no", score=0.7))
    dec = tmp_path / "gate.csv"
    _write_csv(dec, [["c-gate", "accept", "", "无权限"]])
    report = review_mod.import_decisions(store, dec, reviewer="jack")
    assert report["failed"] == 1 and report["processed"] == 0
    assert any("approve 权限不足" in f["reason"] for f in report["failures"])
    assert service.get("c-gate").review_status == DRAFT
    assert service.list_history("c-gate") == []
    _rev, total = audit.query(action="mapping_review")
    assert total == 0  # 被拒不落审计


def test_review_import_agent_reviewer_rejected(tmp_path, store, service) -> None:
    """P1-3 ② V9：reviewer 解析为 agent → 一律拒（审=人专属），状态不变。"""
    _grant_approve(store, "order_id", "jack")
    service.create(_cand("c-v9", target="order_id", source_field="order_no", score=0.7))
    dec = tmp_path / "v9.csv"
    _write_csv(dec, [["c-v9", "accept", "", ""]])
    report = review_mod.import_decisions(store, dec, reviewer="agent:procurement_agent")
    assert report["failed"] == 1
    assert any("V9" in f["reason"] and "agent" in f["reason"] for f in report["failures"])
    assert service.get("c-v9").review_status == DRAFT


def test_review_import_atomic_rollback(tmp_path, store, service, audit) -> None:
    """P2-6 原子性：单行事务中途失败（已拒绝候选再 accept → 非法流转）整体回滚，无中间态。"""
    _grant_approve(store, "order_id", "jack")
    service.create(_cand("c-at", target="order_id", source_field="order_no", score=0.7))
    dec1 = tmp_path / "rej.csv"
    _write_csv(dec1, [["c-at", "reject", "", "先拒绝"]])
    report1 = review_mod.import_decisions(store, dec1, reviewer="jack")
    assert report1["rejected"] == 1
    assert service.get("c-at").review_status == "rejected"
    hist_before = len(service.list_history("c-at"))
    # 已 rejected 再 accept：rejected→approved 非法流转 → 事务中途抛错，整体回滚
    dec2 = tmp_path / "acc.csv"
    _write_csv(dec2, [["c-at", "accept", "", "想翻案"]])
    report2 = review_mod.import_decisions(store, dec2, reviewer="jack")
    assert report2["failed"] == 1
    assert any("IllegalTransitionError" in f["reason"] for f in report2["failures"])
    assert service.get("c-at").review_status == "rejected"  # 状态未变
    assert len(service.list_history("c-at")) == hist_before  # 历史未增
    _rev, total = audit.query(action="mapping_review")
    assert total == 1  # 仅 reject 一次审计；失败的 accept 未落
    assert audit.verify_integrity()["ok"] is True


def test_review_import_corrected_target_validated(tmp_path, store, service) -> None:
    """P1-3 ③：corrected_target 写入前 C4/格式校验（未注册属性 / 非法格式 → 拒，不落库）。"""
    _grant_approve(store, "order_id", "jack")
    service.create(_cand("c-c4", target="order_id", source_field="order_no", score=0.7))
    dec = tmp_path / "c4.csv"
    _write_csv(dec, [["c-c4", "accept", "ghost_attr", "未注册字段"]])
    report = review_mod.import_decisions(store, dec, reviewer="jack")
    assert report["failed"] == 1
    assert any("C4" in f["reason"] for f in report["failures"])
    c = service.get("c-c4")
    assert c.target == "order_id" and c.review_status == DRAFT  # 未改
    assert service.list_history("c-c4") == []
    # 非法格式（attribute 目标非 snake_case）
    dec2 = tmp_path / "fmt.csv"
    _write_csv(dec2, [["c-c4", "accept", "Bad Target!", ""]])
    report2 = review_mod.import_decisions(store, dec2, reviewer="jack")
    assert report2["failed"] == 1
    assert any("格式非法" in f["reason"] for f in report2["failures"])
    assert service.get("c-c4").target == "order_id"


def test_review_accept_corrected_registered_field(tmp_path, store, service) -> None:
    """P1-3 ③ 正向路径：corrected_target 为已注册对象字段（C4 放行）→ 修正生效。"""
    _grant_approve(store, "note", "jack")
    service.create(_cand("c-pos", target="order_id", source_field="order_no", score=0.7))
    dec = tmp_path / "pos.csv"
    _write_csv(dec, [["c-pos", "accept", "note", "修正到已注册字段"]])
    report = review_mod.import_decisions(store, dec, reviewer="jack")
    assert report["accepted"] == 1 and report["failed"] == 0
    c = service.get("c-pos")
    assert c.target == "note" and c.review_status == APPROVED
    assert len(service.list_history("c-pos")) == 1


def test_publish_requires_approve_permission(store, service) -> None:
    """P1-3 ④：publish 前复核 approve 权限——无策略 → 候选记 error 不入批、不注册。"""
    reg = build_registry()
    svc = MappingCandidateService(store, reg)
    svc.create(
        _cand("c-obj", kind="object", target="Material", score=1.0,
              source_field="matnr", evidence_json={"pk_field": "matnr"})
    )
    report = publish_approved(store, reg)
    assert report["published_objects"] == []
    assert report["published_links"] == []
    assert report["rolled_back"] is False
    assert any("approve 权限" in e["reason"] for e in report["errors"])


def test_publish_self_check_rollback(store, service, registry, audit) -> None:
    """P2-7：发布后 self_check 有 error（LINK_FK_MISSING）→ 回滚本批（卸载注册+删血缘+failed 审计）。"""
    _grant_approve(store, "order.p3_bad_link", "cli")
    service.create(
        _cand("c-bad", kind="link", target="order.p3_bad_link", score=0.8,
              source_field="customer_id",
              evidence_json={"method": "fk_detection.detect_links", "source_type": "Order",
                             "target_type": "Customer", "cardinality": "N:1", "fk_field": "ghost_fk"})
    )
    service.transition("c-bad", APPROVED, reviewer="jack")
    report = publish_approved(store, registry)
    assert report["rolled_back"] is True
    assert report["published_links"] == []  # published 语义 = 最终持久
    assert report["self_check"]["ok"] is False
    assert not any(l.name == "order.p3_bad_link" for l in registry.link_types())  # 已卸载
    conn = store.ontology_conn()
    try:
        rows = conn.execute(
            "SELECT entity_class FROM mappings WHERE entity_class='order.p3_bad_link'"
        ).fetchall()
        pub = conn.execute(
            "SELECT outcome, error_code FROM audit_log WHERE action_name='mapping_publish'"
        ).fetchall()
    finally:
        conn.close()
    assert rows == []  # 血缘已删
    assert len(pub) == 1 and pub[0]["outcome"] == "failed"
    assert pub[0]["error_code"] == "SELF_CHECK_FAILED"
    assert audit.verify_integrity()["ok"] is True


def test_create_thresholds_override(store, registry, service) -> None:
    """P1-4（§1.3）：create(thresholds=...) 覆盖 classify——0.9 分候选在 high=0.95 下降档。"""
    c = service.create(_cand("c-t1", target="order_id", score=0.9), thresholds=(0.95, 0.6))
    assert c.confidence_level == "medium" and c.review_status == DRAFT and not c.auto_approved
    c2 = service.create(_cand("c-t2", target="order_id", score=0.9))
    assert c2.confidence_level == "high" and c2.review_status == APPROVED and c2.auto_approved


# ======================================================================
# ⑤ 变更影响分析（门禁 5） + 管道编排（设计 §1.1）
# ======================================================================
def test_change_impact_analysis(tmp_path, store, service) -> None:
    """门禁 5（设计 §4.3 实跑）：analyze_change → MappingChangeReport 完整可查。"""
    from src.builder.mapping.impact import analyze_change
    from src.des.config import load_config
    from src.des.metrics import load_metrics

    metrics = load_metrics(config=load_config("hc_precision"))
    cand = _cand(
        "c-imp", kind="object", target="Material", score=0.95,
        source_field="matnr", source_table="erp.MARA",
    )
    report = analyze_change(cand, store=store, registry=build_registry(), metrics=metrics)
    assert report["change"]["candidate_id"] == "c-imp"
    assert report["change"]["target_to"] == "Material"
    assert report["change"]["target_from"] is None  # approved 终态不可改 → 变更 = 新增候选
    assert "Material" in report["affected"]["objects"]
    assert report["affected"]["metrics"]  # object_type=Material 的指标反向引用（读侧受影响）
    assert "v0.2 metric" in report["affected"]["contracts"]
    assert report["affected"]["audit_chain_ok"] is True
    assert report["risk"] in ("high", "medium", "low")
    assert report["risk"] == "high"  # 读侧指标受影响 → 需重物化


def test_run_mapping_pipeline_report(store, registry) -> None:
    """P1-4（设计 §1.1）：run_mapping_pipeline → PipelineReport，C4 跳过显式 skipped_c4 计数。"""
    from src.builder.mapping.pipeline import run_mapping_pipeline

    source = {
        "source_table": "erp.MARA",
        "columns": [
            {"column": "name", "inferred_type": "string", "is_technical": False},
            {"column": "etl_loaded_at", "inferred_type": "datetime", "is_technical": True},
        ],
        "des_mappings": [
            {"kind": "object", "target": "Material"},
            {"kind": "attribute", "target": "matnr", "source_field": "material_number"},
            {"kind": "object", "target": "GhostObj"},  # C4 未注册 → skipped_c4
        ],
        "detected_links": [
            DetectedLink(
                link_id="lnk_p", source_field="matnr", target_field="matnr",
                cardinality="N:1", detection_method="exact_match",
                match_summary={"direct_match_rows": 20, "format_normalized_match_rows": 5,
                               "unmatched_rows": 5, "total_rows": 30},
            ),
        ],
    }
    report = run_mapping_pipeline(source, store=store, registry=registry)
    assert report["source_table"] == "erp.MARA"
    assert report["total_candidates"] == 4  # Material + matnr + lnk_p + GhostObj（object 待补录 draft）
    assert report["auto_approved"] == 2     # Material + matnr（DES score 1.0 高置信自动过）
    assert report["in_queue"] == 2          # lnk_p medium + GhostObj（object 未注册 → 待补录 draft）
    assert report["by_level"] == {"high": 3, "medium": 1, "low": 0}  # GhostObj 1.0 → high（但 draft）
    assert report["skipped_c4"] == ["GhostObj", "Name"]  # object 待补录 + attribute 跳过均显式计数


# ======================================================================
# ⑥ 安全 / 一致性（门禁 6）
# ======================================================================
def test_audit_history_worm_and_integrity(store, service, audit) -> None:
    """审核痕迹 append-only（WORM 禁改删）+ 审计哈希链 verify_integrity 全绿。"""
    service.create(_cand("c1", target="order_id", score=0.7))
    service.transition("c1", REVIEWING, reviewer="jack", note="接单")
    service.transition("c1", APPROVED, reviewer="jack", note="通过")
    # 先落一条审计记录，确保 WORM 触发器有行可拦（service.transition 只写 history 不写 audit_log）
    audit.append(
        AuditRecord(action_name="mapping_review", actor="human", outcome="applied", source="review")
    )
    assert audit.verify_integrity()["ok"] is True
    conn = store.ontology_conn()
    try:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("UPDATE mapping_review_history SET reviewer='hack'")
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("DELETE FROM mapping_review_history")
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("UPDATE audit_log SET actor='hack'")
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("DELETE FROM audit_log")
    finally:
        conn.close()


def test_registry_no_orphan_after_publish(store, service, registry, audit) -> None:
    """入注册表后引用一致：self_check 0 error；mappings 血缘 entity_class 均指向已注册对象/链接（无孤儿）。"""
    service.create(
        _cand("c-lnk", kind="link", target="order.p3_customer", score=0.8,
              source_field="customer_id",
              evidence_json={"method": "fk_detection.detect_links", "source_type": "Order",
                             "target_type": "Customer", "cardinality": "N:1", "fk_field": "customer_id"})
    )
    service.transition("c-lnk", APPROVED, reviewer="jack")
    _grant_approve(store, "order.p3_customer", "cli")
    report = publish_approved(store, registry)
    assert report["self_check"]["ok"] is True
    conn = store.ontology_conn()
    try:
        rows = conn.execute("SELECT entity_class FROM mappings WHERE status='published'").fetchall()
    finally:
        conn.close()
    link_names = {l.name for l in registry.link_types()}
    assert rows
    for r in rows:
        assert r["entity_class"] in link_names or registry.has_object_type(r["entity_class"])
    # 发布自检后审计链仍自洽
    assert audit.verify_integrity()["ok"] is True
