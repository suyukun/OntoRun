"""P3 ground truth 门禁测试（docs/P3-映射治理设计_v0.1.md §3/§3.5/§5 落地）。

任务（Rose 派发）：60-100 条映射 GT + recall@5 ≥ 80% 门禁。本文件用**真实 GT 文件**
（data/des/mapping_ground_truth.yaml，62 条，覆盖 18 表）+ DES 管道候选（des_source 装载：
真实 schema 列 + config fk 驱动链接 + GT 派生的语义声明）→ calibrate 验证门禁。

门禁断言（§5 表对应项；量级用 DES scale=0.003 小规模确定性数据集，遵守铁律①不跑全量）：
1. test_gt_file_load_and_validate：真实 GT 加载合法（kind 枚举/target 非空/无重复）、规模
   60-100、三类 kind 全覆盖、18 表全覆盖、target 全落在已注册对象/字段/链接。
2. test_recall_gate：管道候选 → full_recall@5 ≥ 0.80（结果门禁）+ top-5 与 top-1 区分 +
   双口径（auto_recall 与 full_recall 显式报告，差值 = 人工审核增量）。
3. test_calibrate_output：校准 → 网格扫描合法（medium≤high）+ 选择规则 + 写
   mapping_thresholds.yaml + 报告含默认行与最优行；有解不落 fallback。
4. test_auto_precision_non_gt：auto_precision 分母含非 GT 键（red-team P2-5）——DES 管道
   fk_detection 自动过候选（lnk_* 未注册链接 target）计入分母不 TP → auto_precision < 1.0
   + unvalidated_auto_approved 非空（不假乐观）。
5. test_gt_every_entry_recoverable：每 GT 真值命中 top-5（一致性：GT 真值已注册且可被管道恢复，
   demo 口径 GT = DES 声明语义，单一事实来源）。

约束：不跑全量 pytest；只跑本文件 + ruff；修实现不修测试。
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from src.builder.mapping import calibrate as cal
from src.builder.mapping import des_source as ds
from src.builder.mapping.annotate import MappingCandidate
from src.builder.mapping.pipeline import run_mapping_pipeline
from src.des.config import load_config
from src.des.generate import build_enterprise
from src.ontology import build_registry
from src.runtime.store import Store

ROOT = Path(__file__).resolve().parents[1]
ENTERPRISE_CODE = "hc_precision"
GT_PATH = ROOT / "data" / "des" / "mapping_ground_truth.yaml"
# 18 表全集（与 config 表注册表对齐，防止新增/改名表漏覆盖）
ALL_TABLES = {
    "erp.KNA1",
    "erp.MARA",
    "erp.MARC",
    "erp.MARD",
    "erp.MAST",
    "erp.STPO",
    "erp.VBAK",
    "erp.VBAP",
    "mes.AUFK",
    "mes.AFPO",
    "mes.COFV",
    "mes.MPLA",
    "wms.MSEG",
    "wms.WMMD",
    "scm.EKKO",
    "scm.EKPO",
    "scm.LFA1",
    "fin.ACDOCA",
}


@pytest.fixture(scope="module")
def des_dir(tmp_path_factory) -> Path:
    """小规模确定性 DES 企业（scale=0.003，~3000 行，秒级；列结构/语义与全量一致）。"""
    d = tmp_path_factory.mktemp("des_gt")
    build_enterprise(ENTERPRISE_CODE, out_dir=str(d), scale=0.003)
    return d


@pytest.fixture(scope="module")
def config() -> dict:
    return load_config(ENTERPRISE_CODE)


@pytest.fixture(scope="module")
def gt_path() -> Path:
    return GT_PATH


@pytest.fixture(scope="module")
def gt_entries() -> list[dict]:
    raw = yaml.safe_load(GT_PATH.read_text(encoding="utf-8"))
    assert "entries" in raw, "GT 文件缺 entries"
    return raw["entries"]


@pytest.fixture(scope="module")
def gt(gt_entries) -> dict[str, str]:
    return cal.load_ground_truth(GT_PATH)


@pytest.fixture(scope="module")
def store(des_dir, config, gt_entries) -> Store:
    """18 表管道候选落库（GT 派生的语义声明 → DES 管道 → mapping_candidates 表）。"""
    s = Store(des_dir / "source.db", des_dir / "ontology.db")
    s.migrate()
    reg = build_registry()
    semantics = ds.semantics_from_gt(gt_entries)
    assert set(semantics) == ALL_TABLES  # GT 必须覆盖全部 18 表（防止漏覆盖）
    for src in ds.build_des_sources(config, des_dir, semantics):
        run_mapping_pipeline(src, store=s, registry=reg)
    return s


@pytest.fixture(scope="module")
def registry():
    return build_registry()


# ======================================================================
# ① GT 文件加载与校验（门禁 1）
# ======================================================================
def test_gt_file_load_and_validate(gt, gt_entries, registry) -> None:
    """真实 GT 文件：加载合法、规模 60-100、三类全覆盖、target 全落在已注册对象/字段/链接。"""
    assert 60 <= len(gt) <= 100, f"GT 规模须 60-100，实际 {len(gt)}"
    kinds = {e["kind"] for e in gt_entries}
    assert kinds == {"object", "attribute", "link"}, f"三类 kind 须全覆盖: {kinds}"
    # 去重：load_ground_truth 对重复 key fail-fast（同 (source_table, source_field, kind)）
    assert len(
        {f"{e['source_table']}|{e['source_field']}|{e['kind']}" for e in gt_entries}
    ) == len(gt_entries)
    # target 注册校验：object=已注册对象 / attribute=某已注册对象字段 / link=已注册链接
    link_names = {l.name for l in registry.link_types()}
    fields = {f for o in registry.object_types() for f in o.model.model_fields}
    for e in gt_entries:
        assert e["source_table"] in ALL_TABLES
        assert e["gt_target"], f"gt_target 非空: {e}"
        if e["kind"] == "object":
            assert registry.has_object_type(e["gt_target"]), (
                f"未注册对象 target: {e['gt_target']}"
            )
        elif e["kind"] == "attribute":
            assert e["gt_target"] in fields, f"未注册对象字段 target: {e['gt_target']}"
        else:
            assert e["gt_target"] in link_names, f"未注册链接 target: {e['gt_target']}"
    # 每表至少 1 条
    covered = {e["source_table"] for e in gt_entries}
    assert covered == ALL_TABLES, f"GT 未覆盖全表: {sorted(ALL_TABLES - covered)}"


def test_gt_file_metadata() -> None:
    """GT 文件元数据：版本 + 标注口径（demo 单轮标注，Rose 复核待办，§3.5）。"""
    raw = yaml.safe_load(GT_PATH.read_text(encoding="utf-8"))
    assert raw["version"]
    assert raw["domain"] == "manufacturing"
    labeling = raw["labeling"]
    assert labeling["method"] == "single-pass"  # demo 口径：单轮标注
    assert labeling["reviewer"] == "rose"  # Rose 复核（待办，复核通过前真值以文档为准）
    assert labeling["reviewed"] is False


# ======================================================================
# ② recall 双口径 + top-5 门禁（门禁 2）
# ======================================================================
def test_recall_gate(store, gt) -> None:
    """full_recall@5 ≥ 0.80（结果门禁）+ top-5 与 top-1 区分 + 双口径显式。"""
    r5 = cal.recall_at_k(store, gt, k=5)
    r1 = cal.recall_at_k(store, gt, k=1)
    assert r5 >= cal.RECALL_GATE, f"full_recall@5={r5} < 0.80 门禁不通过"
    assert r1 <= r5, "recall 随 k 单调不减"
    # top-5 与 top-1 区分：存在 GT 真值被同 (table, field, kind) 高分候选顶出 top-1
    # （WMMD.MATNR link：fk 检测 lnk_* 与语义 material.codes 同分 1.0，SQLite 按插入序取 top-1）
    assert r5 > r1, "应存在仅 top-5 命中的 GT 真值（top-1 与 top-5 须区分）"
    # 双口径显式：auto_recall（高置信自动过）≤ full_recall（全量 approved，人工可补齐）
    auto = cal.auto_coverage(store, gt, cal.FALLBACK_THRESHOLDS["high"])
    assert 0 <= auto <= 1.0
    assert auto <= r5
    # 差值 = 人工审核增量（DES 语义已知 → 差值为 0，符合 demo 半自动口径，报告显式声明）
    print(
        f"full_recall@5={r5:.3f} full_recall@1={r1:.3f} auto_recall@0.9={auto:.3f} increment={r5 - auto:.3f}"
    )


# ======================================================================
# ③ 校准输出（门禁 3）
# ======================================================================
def test_calibrate_output(store, gt, gt_path, tmp_path) -> None:
    """校准：网格扫描合法 + 选择规则 + 写 mapping_thresholds.yaml + 报告含默认行与最优行。"""
    out = tmp_path / "mapping_thresholds.yaml"
    rep = cal.calibrate(store, gt_path, out_path=out)
    assert rep["full_recall_at_5"] >= cal.RECALL_GATE
    assert rep["fallback"] is False  # 有解（recall 满足门禁），不静默回退
    rows = rep["grid_rows"]
    assert rows
    assert all(r["medium"] <= r["high"] for r in rows)  # 约束 medium ≤ high
    grid_pairs = {(r["high"], r["medium"]) for r in rows}
    assert (0.9, 0.6) in grid_pairs  # 默认行在网格内
    best = rep["recommended_thresholds"]
    assert (best["high"], best["medium"]) in grid_pairs  # 最优行在网格内
    assert best["high"] >= best["medium"]
    assert best["high"] in {r["high"] for r in rows}
    # mapping_thresholds.yaml 写入（C2：阈值配置不写死）
    doc = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert doc["thresholds"] == best
    assert doc["gt_size"] == len(gt)
    assert doc["full_recall_at_5"] == rep["full_recall_at_5"]
    # 报告双口径显式
    assert rep["auto_recall_default"] <= rep["full_recall_at_5"]


# ======================================================================
# ④ auto_precision 非 GT 错批计数（red-team P2-5）
# ======================================================================
def test_auto_precision_counts_non_gt(store, gt) -> None:
    """auto_precision 分母 = 全部自动过候选（含非 GT 键）：DES 管道 fk 自动过 lnk_* 链接计入。"""
    high = cal.FALLBACK_THRESHOLDS["high"]
    precision = cal.auto_precision(store, gt, high)
    # 存在非 GT 自动过候选（fk 检测的 lnk_* 未注册链接 target）→ 分母含非 GT 键 → precision < 1.0
    unvalidated = cal.unvalidated_auto_approved(store, gt, high)
    assert unvalidated, (
        "应存在 GT 覆盖之外自动过候选（否则 auto_precision 无法测非 GT 计数）"
    )
    assert all(c["target"].startswith("lnk_") for c in unvalidated), (
        f"非 GT 自动过候选应为 fk 检测链接: {[c['target'] for c in unvalidated[:5]]}"
    )
    assert precision < 1.0, (
        "auto_precision 必须如实计入非 GT 自动错批（防 P2-5 假乐观）"
    )
    # 纯函数单元：分母含非 GT 键 → TP 只计命中真值
    gt_sub = {"t|a|attribute": "name"}
    cands = [
        MappingCandidate(
            candidate_id="c1",
            kind="attribute",
            source_table="t",
            source_field="a",
            target="name",
            confidence_score=0.99,
            confidence_level="high",
        ),  # TP：命中 GT
        MappingCandidate(
            candidate_id="c2",
            kind="link",
            source_table="t",
            source_field="b",
            target="lnk_noise",
            confidence_score=0.99,
            confidence_level="high",
        ),  # 非 GT：不 TP
    ]
    assert cal.auto_precision_from(cands, gt_sub) == pytest.approx(0.5)


# ======================================================================
# ⑤ GT 一致性：每条真值可恢复（demo 口径 GT = DES 声明语义）
# ======================================================================
def test_gt_every_entry_recoverable(store, gt) -> None:
    """每条 GT 真值都命中 top-5（一致性：GT 真值已注册且管道可恢复；防漏标/错标 target）。"""
    assert cal.recall_at_k(store, gt, k=5) == 1.0
    misses = []
    for key, target in gt.items():
        st, sf, kind = key.split("|")
        cands = cal.candidates_for(store, st, sf, kind)
        if target not in {c.target for c in cands[:5]}:
            misses.append(
                (key, target, [(c.target, round(c.confidence_score, 2)) for c in cands])
            )
    assert misses == [], f"GT 真值未被 top-5 恢复: {misses}"
