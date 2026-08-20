"""P4 验收测试（蓝图 v0.3 §9-P4 / 补丁 v0.3.1 A2/B4）。

覆盖：
  1. T1 逻辑规则真实推导（禁模板化，蓝图 §10 决策 1.1.3）
     1.1 反模板化：不同 schema 推导出不同规则；规则内容来自真实 schema 数据
     1.2 无约束 schema -> 零规则（不硬塞条数）
     1.3 状态机流转：描述箭头链解析 + evaluate_transition 非法流转拒绝
     1.4 E4 状态机：discover -> review -> publish；非法流转 4xx；
         只接受已发布 object_types
     1.5 幂等：同 schema 重复 discover 跳过既有规则
  2. T2 action_types 对接 runtime（单一事实来源 = 引擎声明）
     2.1 启动同步：6 内置动作登记（parameters/criteria/effects 来自引擎）
     2.2 submission_criteria 引用 published 逻辑规则（数据结构打通 +
         悬空/未发布引用拒绝执行）
     2.3 错误路径：未知动作 404 / 未发布 400 / A2 动态动作 400 / 非法 actor 400
  3. T3 E6 快照审计（P4 验收核心）
     3.1 applied：源库真变 + after 反映变更 + audit_ref 对账 audit_log
     3.2 dry_run：源库零变更 + simulated 快照 + 无 runtime 审计引用
     3.3 rejected：before 有值 after==before 源库零变更 + 审计仍落
     3.4 failed：error 非空 + action_runs 落库（引擎失败路径）
     3.5 runs 历史列表含快照与 audit_ref
  4. TD-6 provider achat 双轨（chat 同步兼容 / 异步入口真不阻塞语义）
  5. TD-3 MockProvider 响应 fixture 精确断言（E2E 断言精确可控）

fixtures：seed 源库 + 临时本体库；对象类型经 builder API 建 + review + publish。
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# seed 中的确定性样本（data/seed_retail_source.py 顶部注释）
ORDER_CONFIRMED = "ORD-1001"  # confirmed（可取消演示样本）
ORDER_SHIPPED = "ORD-2007"  # shipped（已发货拦截样本）
ORDER_PENDING = "ORD-0001"  # pending

# 采购单 schema（含必填/枚举/数值边界/状态流转链四类约束）
SCHEMA_PURCHASE_ORDER = {
    "type": "object",
    "properties": {
        "order_id": {"type": "string"},
        "status": {
            "type": "string",
            "enum": ["pending", "confirmed", "shipped", "cancelled"],
            "description": "订单状态；流转：pending->confirmed->shipped；pending/confirmed->cancelled",
        },
        "total_cents": {"type": "integer", "minimum": 0, "maximum": 100000000},
    },
    "required": ["order_id"],
}

# 供应商档案 schema（约束集合不同 -> 推导结果必须不同；tier 非状态语义字段）
SCHEMA_SUPPLIER_PROFILE = {
    "type": "object",
    "properties": {
        "supplier_id": {"type": "string"},
        "tier": {"type": "string", "enum": ["a", "b", "c"]},
        "rating": {"type": "number", "minimum": 1, "maximum": 5},
        "note": {"type": "string"},
    },
    "required": ["supplier_id"],
}

# 无约束 schema（无 required/enum/边界/流转 -> 零规则）
SCHEMA_PLAIN = {
    "type": "object",
    "properties": {
        "ref_id": {"type": "string"},
        "memo": {"type": "string"},
    },
}


def _build_client(tmp: Path) -> TestClient:
    """seed 源库 + 临时本体库 -> TestClient（fixture 共用构造）。"""
    from data import seed_retail_source as seed
    from src.api.main import create_app

    source = tmp / "source.db"
    seed.build_database(source)
    app = create_app(source_db=source, ontology_db=tmp / "ontology.db")
    return TestClient(app)


@pytest.fixture
def client(tmp_path: Path):
    """function 级隔离：会改源库/本体状态的测试用（run / discovery 计数类）。"""
    c = _build_client(tmp_path)
    with c:
        yield c


@pytest.fixture(scope="class")
def shared_client(tmp_path_factory):
    """class 级共享：只读或互不冲突的测试类用（降低每测试 ~2s 的 app 构建成本）。"""
    c = _build_client(tmp_path_factory.mktemp("p4_shared"))
    with c:
        yield c


def _publish_object_type(client: TestClient, name: str, schema: dict) -> str:
    """经 builder API 建 + review + publish 一个对象类型，返回 ot_id。"""
    r = client.post(
        "/api/v1/builder/object-types",
        headers={"X-Actor": "api"},
        json={
            "name": name,
            "category": "domain",
            "property_schema": schema,
        },
    )
    assert r.status_code == 200, r.text
    ot_id = r.json()["data"]["id"]
    r = client.post(
        f"/api/v1/builder/object-types/{ot_id}/review", headers={"X-Actor": "api"}
    )
    assert r.status_code == 200, r.text
    r = client.post(
        f"/api/v1/builder/object-types/{ot_id}/publish", headers={"X-Actor": "api"}
    )
    assert r.status_code == 200, r.text
    assert r.json()["data"]["status"] == "published"
    return ot_id


def _source_row(client: TestClient, sql: str, params: tuple = ()) -> dict | None:
    store = client.app.state.runtime.store
    with store.source_conn() as conn:
        cur = conn.execute(sql, params)
        cols = [c[0] for c in cur.description]
        row = cur.fetchone()
        return dict(zip(cols, row)) if row else None


def _audit_row(client: TestClient, audit_id: str) -> dict | None:
    store = client.app.state.runtime.store
    with store.ontology_conn() as conn:
        row = conn.execute(
            "SELECT * FROM audit_log WHERE audit_id = ?", (audit_id,)
        ).fetchone()
        return dict(row) if row else None


# ======================================================================
# 1. T1 逻辑规则真实推导
# ======================================================================


class TestLogicDiscovery:
    """真实推导：规则内容来自 schema 约束（反模板化断言）。"""

    def test_discover_from_purchase_order_schema(self, client) -> None:
        """四类约束各产一条规则，expression 是结构化可机器执行 JSON。"""
        _publish_object_type(client, "PurchaseOrder", SCHEMA_PURCHASE_ORDER)
        r = client.post(
            "/api/v1/builder/logic/discover",
            headers={"X-Actor": "api"},
            json={"object_type": "PurchaseOrder"},
        )
        assert r.status_code == 200, r.text
        data = r.json()["data"]
        # 4 条：required + enum + range + state_machine（条数由 schema 决定）
        assert data["created"] == 4, data
        rules = {rule["name"]: rule for rule in data["rules"]}
        assert "PurchaseOrder.order_id_required" in rules
        assert "PurchaseOrder.status_enum_domain" in rules
        assert "PurchaseOrder.total_cents_range" in rules
        assert "PurchaseOrder.status_state_machine" in rules
        # logic_type / severity 按蓝图 §4
        assert rules["PurchaseOrder.order_id_required"]["logic_type"] == "precondition"
        assert rules["PurchaseOrder.status_enum_domain"]["logic_type"] == "invariant"
        assert rules["PurchaseOrder.total_cents_range"]["logic_type"] == "threshold"
        assert (
            rules["PurchaseOrder.status_state_machine"]["logic_type"] == "state_machine"
        )
        # expression 结构化（kind/object_type/field + kind 专属字段，非自然语言）
        expr = rules["PurchaseOrder.total_cents_range"]["expression"]
        assert expr["kind"] == "range"
        assert expr["object_type"] == "PurchaseOrder"
        assert expr["field"] == "total_cents"
        assert expr["minimum"] == 0 and expr["maximum"] == 100000000
        assert rules["PurchaseOrder.status_enum_domain"]["expression"]["values"] == [
            "pending",
            "confirmed",
            "shipped",
            "cancelled",
        ]

    def test_anti_template_different_schemas_different_rules(self, client) -> None:
        """反模板化：两个 schema 推导出的规则集合必须不同（名字+内容）。"""
        _publish_object_type(client, "PurchaseOrder", SCHEMA_PURCHASE_ORDER)
        _publish_object_type(client, "SupplierProfile", SCHEMA_SUPPLIER_PROFILE)
        r1 = client.post(
            "/api/v1/builder/logic/discover",
            headers={"X-Actor": "api"},
            json={"object_type": "PurchaseOrder"},
        )
        r2 = client.post(
            "/api/v1/builder/logic/discover",
            headers={"X-Actor": "api"},
            json={"object_type": "SupplierProfile"},
        )
        assert r1.status_code == 200 and r2.status_code == 200
        rules_a = {rule["name"]: rule for rule in r1.json()["data"]["rules"]}
        rules_b = {rule["name"]: rule for rule in r2.json()["data"]["rules"]}
        # 名字集合不相交（带对象类型前缀）
        assert not (set(rules_a) & set(rules_b))
        # A 有状态机规则（status 字段 + 描述流转链）；B 的 tier 无状态语义 -> 无
        assert any(r["logic_type"] == "state_machine" for r in rules_a.values())
        assert not any(r["logic_type"] == "state_machine" for r in rules_b.values())
        # 数值边界不同（内容来自真实 schema，不是模板常量）
        range_a = rules_a["PurchaseOrder.total_cents_range"]["expression"]
        range_b = rules_b["SupplierProfile.rating_range"]["expression"]
        assert range_a["minimum"] == 0 and range_a["maximum"] == 100000000
        assert range_b["minimum"] == 1 and range_b["maximum"] == 5
        # 枚举值域不同
        enum_a = rules_a["PurchaseOrder.status_enum_domain"]["expression"]["values"]
        enum_b = rules_b["SupplierProfile.tier_enum_domain"]["expression"]["values"]
        assert enum_a != enum_b
        # 无 required 约束的字段不产必填规则（note/memo 无规则）
        assert "SupplierProfile.note_required" not in rules_b

    def test_unconstrained_schema_produces_no_rules(self, client) -> None:
        """无约束 schema -> 零规则（不硬塞固定条数）。"""
        _publish_object_type(client, "PlainRecord", SCHEMA_PLAIN)
        r = client.post(
            "/api/v1/builder/logic/discover",
            headers={"X-Actor": "api"},
            json={"object_type": "PlainRecord"},
        )
        assert r.status_code == 200, r.text
        data = r.json()["data"]
        assert data["discovered"] == 0
        assert data["created"] == 0
        assert data["rules"] == []

    def test_discover_requires_published_object_type(self, client) -> None:
        """draft 对象类型不参与推导（400）。"""
        r = client.post(
            "/api/v1/builder/object-types",
            headers={"X-Actor": "api"},
            json={
                "name": "DraftOt",
                "category": "domain",
                "property_schema": SCHEMA_PURCHASE_ORDER,
            },
        )
        assert r.status_code == 200
        r = client.post(
            "/api/v1/builder/logic/discover",
            headers={"X-Actor": "api"},
            json={"object_type": "DraftOt"},
        )
        assert r.status_code == 400
        assert r.json()["error"]["code"] == "BUILDER_OBJECT_TYPE_NOT_PUBLISHED"

    def test_discover_idempotent_same_schema(self, client) -> None:
        """同 schema 重复 discover：跳过同名同 expression 既有规则。"""
        _publish_object_type(client, "PurchaseOrder", SCHEMA_PURCHASE_ORDER)
        r1 = client.post(
            "/api/v1/builder/logic/discover",
            headers={"X-Actor": "api"},
            json={"object_type": "PurchaseOrder"},
        )
        assert r1.json()["data"]["created"] == 4
        r2 = client.post(
            "/api/v1/builder/logic/discover",
            headers={"X-Actor": "api"},
            json={"object_type": "PurchaseOrder"},
        )
        data = r2.json()["data"]
        assert data["discovered"] == 4
        assert data["created"] == 0
        assert data["skipped_existing"] == 4

    def test_discover_all_published_when_no_ref(self, client) -> None:
        """缺省 object_type：对全部已发布对象类型推导。"""
        _publish_object_type(client, "PurchaseOrder", SCHEMA_PURCHASE_ORDER)
        _publish_object_type(client, "SupplierProfile", SCHEMA_SUPPLIER_PROFILE)
        r = client.post(
            "/api/v1/builder/logic/discover", headers={"X-Actor": "api"}, json={}
        )
        assert r.status_code == 200, r.text
        data = r.json()["data"]
        assert sorted(data["object_types_scanned"]) == [
            "PurchaseOrder",
            "SupplierProfile",
        ]
        assert data["created"] == 7  # 4 + 3

    def test_list_and_get_logic_rules(self, client) -> None:
        _publish_object_type(client, "PurchaseOrder", SCHEMA_PURCHASE_ORDER)
        client.post(
            "/api/v1/builder/logic/discover", headers={"X-Actor": "api"}, json={}
        )
        r = client.get("/api/v1/builder/logic", params={"status": "draft"})
        assert r.status_code == 200
        assert r.json()["data"]["total"] == 4
        # 单条（by name）
        r = client.get("/api/v1/builder/logic/PurchaseOrder.status_state_machine")
        assert r.status_code == 200
        assert r.json()["data"]["logic_type"] == "state_machine"
        # 筛选 logic_type
        r = client.get("/api/v1/builder/logic", params={"logic_type": "threshold"})
        assert r.json()["data"]["total"] == 1
        # 404
        r = client.get("/api/v1/builder/logic/no_such_rule")
        assert r.status_code == 404
        assert r.json()["error"]["code"] == "BUILDER_LOGIC_RULE_NOT_FOUND"


class TestLogicStateMachine:
    """状态机规则：流转链来自字段描述（不凭空造）+ 非法流转拒绝。"""

    def test_derived_transitions_from_description(self) -> None:
        """流转链解析自 property description，两端都在 enum 值域内。"""
        from src.builder.logic import discovery as disc

        rules = disc.derive_rules_from_schema(
            _row_like("PurchaseOrder", SCHEMA_PURCHASE_ORDER)
        )
        sm = next(r for r in rules if r.logic_type == "state_machine")
        transitions = {tuple(t) for t in sm.expression["transitions"]}
        assert transitions == {
            ("pending", "confirmed"),
            ("confirmed", "shipped"),
            ("pending", "cancelled"),
            ("confirmed", "cancelled"),
        }
        assert sm.expression["states"] == [
            "pending",
            "confirmed",
            "shipped",
            "cancelled",
        ]

    def test_illegal_transition_rejected(self) -> None:
        """状态机流转非法拒绝：pending->shipped 不在流转表内。"""
        from src.builder.logic import discovery as disc

        rules = disc.derive_rules_from_schema(
            _row_like("PurchaseOrder", SCHEMA_PURCHASE_ORDER)
        )
        sm = next(r for r in rules if r.logic_type == "state_machine")
        assert disc.evaluate_transition(sm.expression, "pending", "confirmed") is True
        assert disc.evaluate_transition(sm.expression, "pending", "cancelled") is True
        # 非法流转：跳态 / 未知态 / 终态回退
        assert disc.evaluate_transition(sm.expression, "pending", "shipped") is False
        assert disc.evaluate_transition(sm.expression, "cancelled", "pending") is False
        assert disc.evaluate_transition(sm.expression, "pending", "unknown") is False

    def test_no_state_machine_rule_without_transition_chain(self) -> None:
        """enum 字段但描述无流转链 -> 不产 state_machine 规则（不凭空造）。"""
        from src.builder.logic import discovery as disc

        schema = {
            "type": "object",
            "properties": {
                "ref_id": {"type": "string"},
                "status": {
                    "type": "string",
                    "enum": ["open", "closed"],
                    "description": "状态字段但未描述流转",
                },
            },
            "required": ["ref_id"],
        }
        rules = disc.derive_rules_from_schema(_row_like("Ticket", schema))
        kinds = [r.expression["kind"] for r in rules]
        assert "state_transitions" not in kinds
        assert "enum_domain" in kinds  # 取值域规则仍产出

    def test_expression_machine_execution(self) -> None:
        """表达式机器执行：required/enum/range 对记录求值。"""
        from src.builder.logic import discovery as disc

        rules = disc.derive_rules_from_schema(
            _row_like("PurchaseOrder", SCHEMA_PURCHASE_ORDER)
        )
        by_kind = {r.expression["kind"]: r.expression for r in rules}
        # required
        ok, _ = disc.evaluate_expression(by_kind["required"], {"order_id": "PO-1"})
        assert ok is True
        ok, viol = disc.evaluate_expression(by_kind["required"], {"order_id": None})
        assert ok is False and viol["reason"] == "missing"
        # enum_domain
        ok, _ = disc.evaluate_expression(by_kind["enum_domain"], {"status": "pending"})
        assert ok is True
        ok, viol = disc.evaluate_expression(by_kind["enum_domain"], {"status": "void"})
        assert ok is False and viol["reason"] == "not_in_domain"
        # range
        ok, _ = disc.evaluate_expression(by_kind["range"], {"total_cents": 500})
        assert ok is True
        ok, viol = disc.evaluate_expression(by_kind["range"], {"total_cents": -1})
        assert ok is False and viol["reason"] == "below_minimum"
        ok, viol = disc.evaluate_expression(by_kind["range"], {"total_cents": 10**9})
        assert ok is False and viol["reason"] == "above_maximum"

    def test_rule_lifecycle_and_illegal_transition_4xx(self, client) -> None:
        """E4 状态机：draft->reviewed->published；draft 直 publish -> 400。"""
        _publish_object_type(client, "PurchaseOrder", SCHEMA_PURCHASE_ORDER)
        r = client.post(
            "/api/v1/builder/logic/discover", headers={"X-Actor": "api"}, json={}
        )
        rule = r.json()["data"]["rules"][0]
        # draft -> publish 非法
        r = client.post(
            f"/api/v1/builder/logic/{rule['id']}/publish", headers={"X-Actor": "api"}
        )
        assert r.status_code == 400
        assert r.json()["error"]["code"] == "BUILDER_INVALID_STATUS_TRANSITION"
        # draft -> reviewed -> published 合法
        r = client.post(
            f"/api/v1/builder/logic/{rule['id']}/review", headers={"X-Actor": "api"}
        )
        assert r.status_code == 200
        assert r.json()["data"]["status"] == "reviewed"
        r = client.post(
            f"/api/v1/builder/logic/{rule['id']}/publish", headers={"X-Actor": "api"}
        )
        assert r.status_code == 200
        assert r.json()["data"]["status"] == "published"
        # published 终态：再 review -> 400
        r = client.post(
            f"/api/v1/builder/logic/{rule['id']}/review", headers={"X-Actor": "api"}
        )
        assert r.status_code == 400
        # 未知规则 404
        r = client.post(
            "/api/v1/builder/logic/lr_none/review", headers={"X-Actor": "api"}
        )
        assert r.status_code == 404


def _row_like(name: str, schema: dict):
    """构造 discovery 纯函数可用的 object_type 行替身。"""
    from src.builder.object_types import ObjectTypeRow

    return ObjectTypeRow(
        id=f"ot_{name}",
        ontology_id="default",
        name=name,
        name_cn="",
        description="",
        category="domain",
        property_schema=schema,
        status="published",
        pk_field="id",
        title_field="id",
        source_table="",
        created_at="",
        updated_at="",
    )


# ======================================================================
# 2. T2 action_types 对接 runtime
# ======================================================================


class TestActionTypesSync:
    """启动同步：runtime 内置动作登记为 action_types 元数据。"""

    def test_six_builtin_actions_registered(self, shared_client) -> None:
        r = shared_client.get("/api/v1/builder/actions")
        assert r.status_code == 200
        data = r.json()["data"]
        names = {item["name"] for item in data["items"]}
        assert names == {
            "create_order",
            "confirm_order",
            "cancel_order",
            "create_shipment",
            "adjust_inventory",
            "approve_refund",
        }
        by_name = {item["name"]: item for item in data["items"]}
        cancel = by_name["cancel_order"]
        # 元数据来自引擎声明（单一事实来源）：参数 schema + 前置规则 + 效果
        assert cancel["parameters"]["properties"]["order_id"]["type"] == "string"
        pc_codes = [
            pc["error_code"] for pc in cancel["submission_criteria"]["preconditions"]
        ]
        assert pc_codes == [
            "ORDER_NOT_FOUND",
            "ORDER_NOT_CANCELLABLE",
            "SHIPPED_ORDER_CANNOT_BE_CANCELLED",
        ]
        assert "Order.status" in cancel["effects"]["source_backed"]
        assert "Inventory.reserved_qty" in cancel["effects"]["source_backed"]
        # 内置动作已在引擎上线 -> 登记即 published
        assert cancel["status"] == "published"

    def test_action_detail_resolves_criteria(self, shared_client) -> None:
        r = shared_client.get("/api/v1/builder/actions/cancel_order")
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["name"] == "cancel_order"
        resolved = data["resolved_criteria"]
        assert resolved["error"] is None
        assert len(resolved["preconditions"]) == 3
        assert resolved["logic_rules"] == []  # 无 published 规则时为空（结构打通）

    def test_action_detail_not_found(self, shared_client) -> None:
        r = shared_client.get("/api/v1/builder/actions/no_such_action")
        assert r.status_code == 404
        assert r.json()["error"]["code"] == "BUILDER_ACTION_TYPE_NOT_FOUND"


class TestActionRunErrors:
    """run 错误路径：未知动作 404 / 未发布 400 / A2 动态动作 400 / actor 400。"""

    def test_run_unknown_action_404(self, shared_client) -> None:
        r = shared_client.post(
            "/api/v1/builder/actions/no_such_action/run",
            headers={"X-Actor": "api"},
            json={"params": {}},
        )
        assert r.status_code == 404
        assert r.json()["error"]["code"] == "BUILDER_ACTION_TYPE_NOT_FOUND"

    def test_run_draft_action_not_published(self, shared_client) -> None:
        """E3 式 draft 动作（表里有行、未发布）不可执行。"""
        from src.builder.logic import action_types as at_repo

        store = shared_client.app.state.runtime.store
        with store.ontology_conn() as conn:
            at_repo.create(
                conn,
                ontology_id="default",
                name="extracted_op",
                parameters={"type": "object", "properties": {}},
                submission_criteria={"preconditions": [], "logic_rules": []},
                effects={"source_backed": [], "ontology_owned": [], "derived": []},
            )
        r = shared_client.post(
            "/api/v1/builder/actions/extracted_op/run",
            headers={"X-Actor": "api"},
            json={"params": {}},
        )
        assert r.status_code == 400
        assert r.json()["error"]["code"] == "BUILDER_ACTION_NOT_PUBLISHED"

    def test_run_dynamic_action_a2_todo(self, shared_client) -> None:
        """A2 边界：published 的动态动作（引擎无实现）-> 400 BUILDER_ACTION_NOT_EXECUTABLE。"""
        from src.builder.logic import action_types as at_repo
        from src.builder.status_machine import PUBLISHED

        store = shared_client.app.state.runtime.store
        with store.ontology_conn() as conn:
            at_repo.create(
                conn,
                ontology_id="default",
                name="dynamic_op",
                parameters={"type": "object", "properties": {}},
                submission_criteria={"preconditions": [], "logic_rules": []},
                effects={"source_backed": [], "ontology_owned": [], "derived": []},
                status=PUBLISHED,
            )
        r = shared_client.post(
            "/api/v1/builder/actions/dynamic_op/run",
            headers={"X-Actor": "api"},
            json={"params": {}},
        )
        assert r.status_code == 400
        assert r.json()["error"]["code"] == "BUILDER_ACTION_NOT_EXECUTABLE"

    def test_run_invalid_actor_400(self, shared_client) -> None:
        r = shared_client.post(
            "/api/v1/builder/actions/cancel_order/run",
            headers={"X-Actor": "hacker"},
            json={"params": {"order_id": ORDER_CONFIRMED}},
        )
        assert r.status_code == 400
        assert r.json()["error"]["code"] == "INVALID_ACTOR"


# ======================================================================
# 3. T3 E6 快照审计（P4 验收核心）
# ======================================================================


class TestActionRunApplied:
    """applied：源库真变 + before/after 快照 + audit_ref 对账。"""

    def test_cancel_order_applied_e2e(self, client) -> None:
        """动作 E2E：经 action_types 元数据触发现有引擎动作，源库真变。"""
        r = client.post(
            "/api/v1/builder/actions/cancel_order/run",
            headers={"X-Actor": "human"},
            json={"params": {"order_id": ORDER_CONFIRMED, "reason": "E6 验收"}},
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["outcome"] == "applied"
        data = body["data"]
        assert data["status"] == "applied"
        assert data["executed_by"] == "human"
        assert data["error"] == ""
        # before：执行前相关对象状态（order=confirmed）
        before_order = data["before_snapshot"]["objects"]["order"]
        assert before_order["order_id"] == ORDER_CONFIRMED
        assert before_order["status"] == "confirmed"
        # after：源记录重读反映真实变更（cancelled）
        after_order = data["after_snapshot"]["records"]["Order"][ORDER_CONFIRMED]
        assert after_order["status"] == "cancelled"
        assert after_order["status"] != before_order["status"]
        # effects 含 Order.status 与 Inventory.reserved_qty
        effect_keys = {(e["object_type"], e["prop"]) for e in data["effects"]}
        assert ("Order", "status") in effect_keys
        assert ("Inventory", "reserved_qty") in effect_keys
        # 源库真的变了（直查源库，三问测试 2 铁证）
        row = _source_row(
            client, "SELECT status FROM orders WHERE order_id=?", (ORDER_CONFIRMED,)
        )
        assert row["status"] == "cancelled"
        # audit_ref 对账：action_runs 引用的 audit_log 记录存在且一致
        assert data["audit_ref"]
        audit = _audit_row(client, data["audit_ref"])
        assert audit is not None
        assert audit["action_name"] == "cancel_order"
        assert audit["outcome"] == "applied"
        assert audit["actor"] == "human"
        # run 落表（GET /runs 可见）
        r = client.get("/api/v1/builder/actions/cancel_order/runs")
        assert r.status_code == 200
        items = r.json()["data"]["items"]
        assert any(i["id"] == data["run_id"] for i in items)


class TestActionRunDryRun:
    """dry_run：管道全走但零写回，simulated 快照，无 runtime 审计引用。"""

    def test_cancel_order_dry_run(self, client) -> None:
        r = client.post(
            "/api/v1/builder/actions/cancel_order/run",
            headers={"X-Actor": "api"},
            json={"params": {"order_id": ORDER_CONFIRMED}, "dry_run": True},
        )
        assert r.status_code == 200, r.text
        data = r.json()["data"]
        assert data["status"] == "dry_run"
        assert data["dry_run"] is True
        # 源库零变更（仍 confirmed）
        row = _source_row(
            client, "SELECT status FROM orders WHERE order_id=?", (ORDER_CONFIRMED,)
        )
        assert row["status"] == "confirmed"
        # simulated 快照：would-be 状态 = cancelled（与源库现状对照）
        after = data["after_snapshot"]
        assert after["simulated"] is True
        sim_order = after["records"]["Order"][ORDER_CONFIRMED]
        assert sim_order["status"] == "cancelled"
        # effects 已算出（将发生的变更）
        assert any(
            e["object_type"] == "Order" and e["prop"] == "status"
            for e in data["effects"]
        )
        # dry_run 无 runtime 审计记录（audit_log 无 dry_run 语义）
        assert data["audit_ref"] == ""
        # action_runs 有 dry_run 证据
        assert data["run_id"]


class TestActionRunRejected:
    """rejected：before 有值 after==before，源库零变更，审计仍落。"""

    def test_cancel_shipped_order_rejected(self, shared_client) -> None:
        """已发货订单取消被拦（三问测试 3）+ 快照断言。"""
        r = shared_client.post(
            "/api/v1/builder/actions/cancel_order/run",
            headers={"X-Actor": "llm"},
            json={"params": {"order_id": ORDER_SHIPPED}},
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["outcome"] == "rejected"
        data = body["data"]
        assert data["status"] == "rejected"
        assert data["error_code"] == "SHIPPED_ORDER_CANNOT_BE_CANCELLED"
        assert "SHIPPED_ORDER_CANNOT_BE_CANCELLED" in data["error"]
        assert data["executed_by"] == "llm"
        # before 有值（order=shipped 且关联 shipment）
        before = data["before_snapshot"]
        assert before["objects"]["order"]["status"] == "shipped"
        assert before["objects"]["shipments"]  # 关联发货单进入快照
        # after == before（源库零变更）
        assert data["after_snapshot"] == before
        # 源库零变更
        row = _source_row(
            shared_client,
            "SELECT status FROM orders WHERE order_id=?",
            (ORDER_SHIPPED,),
        )
        assert row["status"] == "shipped"
        # 拒绝路径仍落审计（引擎早退仍审计），audit_ref 可对账
        assert data["audit_ref"]
        audit = _audit_row(shared_client, data["audit_ref"])
        assert audit is not None and audit["outcome"] == "rejected"

    def test_cancel_unknown_order_rejected(self, shared_client) -> None:
        """ORDER_NOT_FOUND 拒绝：before.objects.order 为 None，after==before。"""
        r = shared_client.post(
            "/api/v1/builder/actions/cancel_order/run",
            headers={"X-Actor": "api"},
            json={"params": {"order_id": "ORD-9999"}},
        )
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["status"] == "rejected"
        assert data["error_code"] == "ORDER_NOT_FOUND"
        assert data["before_snapshot"]["objects"]["order"] is None
        assert data["after_snapshot"] == data["before_snapshot"]

    def test_invalid_params_rejected_and_recorded(self, shared_client) -> None:
        """LLM 输出视为不可信输入：非法参数被 Pydantic 拦 + run 仍落审计证据。"""
        r = shared_client.post(
            "/api/v1/builder/actions/cancel_order/run",
            headers={"X-Actor": "llm"},
            json={"params": {"order_id": 12345}},  # 类型非法（v2 不做 int->str）
        )
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["status"] == "rejected"
        assert data["error_code"] == "INVALID_PARAMS"
        # 参数校验在快照前早退：无 objects；after==before
        assert "objects" not in data["before_snapshot"]
        assert data["after_snapshot"] == data["before_snapshot"]
        # 源库零变更 + action_runs 有记录
        row = _source_row(
            shared_client,
            "SELECT status FROM orders WHERE order_id=?",
            (ORDER_CONFIRMED,),
        )
        assert row["status"] == "confirmed"

    def test_dry_run_rejected_combination(self, client) -> None:
        """TD-13(b)：dry_run + 前置被拒组合 -> status=rejected 且 audit_ref 非空。

        拒绝优先于 dry_run 模拟（引擎早退语义不变）：dry_run 请求 + 前置不满足
        = rejected（非 dry_run），审计照落，audit_ref 可对账，源库零变更。
        """
        r = client.post(
            "/api/v1/builder/actions/cancel_order/run",
            headers={"X-Actor": "llm"},
            json={"params": {"order_id": ORDER_SHIPPED}, "dry_run": True},
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["outcome"] == "rejected"
        data = body["data"]
        assert data["status"] == "rejected"
        assert data["dry_run"] is True  # 请求是 dry_run，但拒绝路径优先
        assert data["error_code"] == "SHIPPED_ORDER_CANNOT_BE_CANCELLED"
        assert "SHIPPED_ORDER_CANNOT_BE_CANCELLED" in data["error"]
        # 拒绝路径审计照落：audit_ref 非空且可对账（对账锚点不缺失）
        assert data["audit_ref"]
        audit = _audit_row(client, data["audit_ref"])
        assert audit is not None and audit["outcome"] == "rejected"
        # 源库零变更 + 快照语义（after == before）
        row = _source_row(
            client, "SELECT status FROM orders WHERE order_id=?", (ORDER_SHIPPED,)
        )
        assert row["status"] == "shipped"
        assert data["after_snapshot"] == data["before_snapshot"]


class TestActionRunFailed:
    """failed：引擎异常路径也落 action_runs（error 非空 + 审计可对账）。"""

    def test_engine_failure_records_run(self, client, monkeypatch) -> None:
        """F1：failed 对外 error 只含稳定安全摘要，不回显原始异常文本（SQL/运行时细节）。"""
        rt = client.app.state.runtime
        handler = rt.engine._handlers["cancel_order"]
        monkeypatch.setattr(
            handler,
            "load_snapshot",
            lambda snapshot, params: (_ for _ in ()).throw(RuntimeError("boom")),
        )
        r = client.post(
            "/api/v1/builder/actions/cancel_order/run",
            headers={"X-Actor": "api"},
            json={"params": {"order_id": ORDER_CONFIRMED}},
        )
        assert r.status_code == 200, r.text
        data = r.json()["data"]
        assert data["status"] == "failed"
        assert data["error"]  # 错误信息非空
        # F1 red-team：原始异常文本不得泄漏到对外 error/message（含 SQL 等内部细节）
        assert "boom" not in data["error"]
        assert "RuntimeError" not in data["error"]
        assert data["error_code"] == "EXECUTION_FAILED"
        assert "EXECUTION_FAILED" in data["error"]
        assert data["audit_ref"]  # 引擎失败路径仍审计
        audit = _audit_row(client, data["audit_ref"])
        assert audit is not None and audit["outcome"] == "failed"
        # audit_log.message 同为安全摘要（/audit 查询同样对外暴露 message 字段）
        assert "boom" not in (audit["message"] or "")
        assert "RuntimeError" not in (audit["message"] or "")
        # 源库零变更（引擎回滚）
        row = _source_row(
            client, "SELECT status FROM orders WHERE order_id=?", (ORDER_CONFIRMED,)
        )
        assert row["status"] == "confirmed"

    def test_failed_with_effects_after_rereads_source_new_value(
        self, client, monkeypatch
    ) -> None:
        """TD-13(a)：failed + 有 effects 分支（源库已提交但本体同步失败）。

        引擎 ⑦ 同步失败 -> FAILED_CODE_SYNC + effects 存在 -> after 重读源库新值
        （cancelled），源库状态如实反映，audit_ref 可对账（对账缺口测试）。
        """
        rt = client.app.state.runtime
        monkeypatch.setattr(
            rt.engine.index,
            "refresh_many",
            lambda *a, **k: (_ for _ in ()).throw(RuntimeError("sync-boom")),
        )
        r = client.post(
            "/api/v1/builder/actions/cancel_order/run",
            headers={"X-Actor": "api"},
            json={"params": {"order_id": ORDER_CONFIRMED, "reason": "TD-13a"}},
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["outcome"] == "failed"
        data = body["data"]
        assert data["status"] == "failed"
        assert data["error_code"] == "ONTOLOGY_SYNC_FAILED"
        # effects 存在（failed 且 pairs 非空 -> after 走重读分支）
        assert data["effects"], "failed 分支必须带 effects（源库已提交）"
        effect_keys = {(e["object_type"], e["prop"]) for e in data["effects"]}
        assert ("Order", "status") in effect_keys
        # after 重读源库新值：cancelled（源库已变，如实反映）
        after_order = data["after_snapshot"]["records"]["Order"][ORDER_CONFIRMED]
        assert after_order["status"] == "cancelled"
        before_order = data["before_snapshot"]["objects"]["order"]
        assert after_order["status"] != before_order["status"]
        # audit_ref 对账：failed 审计存在
        assert data["audit_ref"]
        audit = _audit_row(client, data["audit_ref"])
        assert audit is not None and audit["outcome"] == "failed"
        # 源库状态如实：cancelled（本体库同步失败不掩盖源库已变）
        row = _source_row(
            client, "SELECT status FROM orders WHERE order_id=?", (ORDER_CONFIRMED,)
        )
        assert row["status"] == "cancelled"

    def test_snapshot_reread_failure_records_failed_run(
        self, client, monkeypatch
    ) -> None:
        """TD-11 回归：after 快照重读异常不冒泡丢行——降级 failed run + 对账闭合。

        注入重读异常（applied 已提交 + 审计已落）：action_runs 必须仍有 failed 行，
        audit_ref 保留引擎侧审计锚点可对账，error 用 F1 安全摘要（不回显原始异常），
        源库状态如实反映（cancelled）。
        """
        import src.builder.logic.action_runs as ar

        def _boom(store, registry, pairs):
            raise RuntimeError("boom-snapshot")

        monkeypatch.setattr(ar, "_reread_records", _boom)
        r = client.post(
            "/api/v1/builder/actions/cancel_order/run",
            headers={"X-Actor": "api"},
            json={"params": {"order_id": ORDER_CONFIRMED, "reason": "TD-11"}},
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["outcome"] == "failed"
        data = body["data"]
        assert data["status"] == "failed"
        # F1 口径：error 只含稳定安全摘要，不回显原始异常文本
        assert "boom-snapshot" not in data["error"]
        assert "EXECUTION_FAILED" in data["error"]
        assert data["error_code"] == "EXECUTION_FAILED"
        # after_snapshot 显式降级标记（不伪造数据）
        assert data["after_snapshot"]["degraded"] is True
        # 不丢行：GET /runs 可见该 failed 行（TD-11 对账缺口修复的核心）
        r2 = client.get("/api/v1/builder/actions/cancel_order/runs")
        assert r2.status_code == 200
        items = r2.json()["data"]["items"]
        assert any(i["id"] == data["run_id"] and i["status"] == "failed" for i in items)
        # audit_ref 对账：引擎侧审计（applied）已落，failed run 引用它 -> 对账闭合
        assert data["audit_ref"]
        audit = _audit_row(client, data["audit_ref"])
        assert audit is not None
        assert audit["action_name"] == "cancel_order"
        assert audit["outcome"] == "applied"  # 源库已提交，审计如实为 applied
        # 源库状态如实反映（不因快照失败而掩盖已发生的写回）
        row = _source_row(
            client, "SELECT status FROM orders WHERE order_id=?", (ORDER_CONFIRMED,)
        )
        assert row["status"] == "cancelled"


class TestActionRunsListing:
    """runs 历史：含快照 + audit_ref + 分页。"""

    def test_runs_history_contains_snapshots(self, client) -> None:
        # 产生 3 条 run：applied / rejected / dry_run
        client.post(
            "/api/v1/builder/actions/cancel_order/run",
            headers={"X-Actor": "api"},
            json={"params": {"order_id": ORDER_PENDING}},
        )
        client.post(
            "/api/v1/builder/actions/cancel_order/run",
            headers={"X-Actor": "api"},
            json={"params": {"order_id": ORDER_SHIPPED}},
        )
        client.post(
            "/api/v1/builder/actions/cancel_order/run",
            headers={"X-Actor": "api"},
            json={"params": {"order_id": ORDER_CONFIRMED}, "dry_run": True},
        )
        r = client.get("/api/v1/builder/actions/cancel_order/runs")
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["total"] == 3
        statuses = {item["status"] for item in data["items"]}
        assert statuses == {"applied", "rejected", "dry_run"}
        for item in data["items"]:
            assert "before_snapshot" in item and "after_snapshot" in item
            assert "executed_by" in item and "audit_ref" in item
        # dry_run 条目 audit_ref 为空；applied/rejected 非空
        by_status = {item["status"]: item for item in data["items"]}
        assert by_status["dry_run"]["audit_ref"] == ""
        assert by_status["applied"]["audit_ref"]
        assert by_status["rejected"]["audit_ref"]

    def test_runs_unknown_action_404(self, client) -> None:
        r = client.get("/api/v1/builder/actions/no_such/runs")
        assert r.status_code == 404


# ======================================================================
# submission_criteria 引用 published 逻辑规则（数据结构打通）
# ======================================================================


class TestSubmissionCriteriaLinkage:
    """published 规则可被动作 submission_criteria 引用 + 引用完整性拒绝。"""

    def _publish_rule(self, client: TestClient, rule_name: str) -> None:
        r = client.post(
            f"/api/v1/builder/logic/{rule_name}/review", headers={"X-Actor": "api"}
        )
        assert r.status_code == 200, r.text
        r = client.post(
            f"/api/v1/builder/logic/{rule_name}/publish", headers={"X-Actor": "api"}
        )
        assert r.status_code == 200, r.text

    def test_criteria_reference_published_rule(self, client) -> None:
        """登记侧引用 published 规则：详情解析可见 + run 透传引用。"""
        from data import seed_retail_source as seed
        from src.builder.logic import action_types as at_repo

        _publish_object_type(client, "SupplierProfile", SCHEMA_SUPPLIER_PROFILE)
        r = client.post(
            "/api/v1/builder/logic/discover", headers={"X-Actor": "api"}, json={}
        )
        rules = r.json()["data"]["rules"]
        rule_names = [rule["name"] for rule in rules]
        self._publish_rule(client, rule_names[0])
        # 把 published 规则挂到 adjust_inventory 的 submission_criteria
        store = client.app.state.runtime.store
        with store.ontology_conn() as conn:
            at_row = at_repo.get_by_name(conn, "adjust_inventory")
            at_repo.update_submission_criteria(conn, at_row.id, [rule_names[0]])
        # 详情：resolved_criteria 解析出 published 规则
        r = client.get("/api/v1/builder/actions/adjust_inventory")
        resolved = r.json()["data"]["resolved_criteria"]
        assert resolved["error"] is None
        assert [rr["name"] for rr in resolved["logic_rules"]] == [rule_names[0]]
        # run：响应透传引用（运行时强制执行属现有引擎职责）
        r = client.post(
            "/api/v1/builder/actions/adjust_inventory/run",
            headers={"X-Actor": "human"},
            json={
                "params": {
                    "warehouse_id": seed.MAIN_WAREHOUSE_ID,
                    "product_id": "SKU-003",
                    "new_on_hand_qty": 1234,
                    "reason": "criteria 引用验收",
                }
            },
        )
        assert r.status_code == 200, r.text
        data = r.json()["data"]
        assert data["status"] == "applied"
        assert data["logic_rules"] == [rule_names[0]]

    def test_criteria_dangling_reference_blocks_run(self, client) -> None:
        """引用 draft 规则 -> 拒绝执行（引用完整性）。"""
        from src.builder.logic import action_types as at_repo

        _publish_object_type(client, "SupplierProfile", SCHEMA_SUPPLIER_PROFILE)
        r = client.post(
            "/api/v1/builder/logic/discover", headers={"X-Actor": "api"}, json={}
        )
        draft_rule = r.json()["data"]["rules"][0]["name"]  # 不 review/publish
        store = client.app.state.runtime.store
        with store.ontology_conn() as conn:
            at_row = at_repo.get_by_name(conn, "cancel_order")
            at_repo.update_submission_criteria(conn, at_row.id, [draft_rule])
        r = client.post(
            "/api/v1/builder/actions/cancel_order/run",
            headers={"X-Actor": "api"},
            json={"params": {"order_id": ORDER_CONFIRMED}},
        )
        assert r.status_code == 400
        body = r.json()
        assert body["error"]["code"] == "BUILDER_LOGIC_RULE_NOT_PUBLISHED"
        assert draft_rule in json.dumps(body["error"]["detail"], ensure_ascii=False)
        # 源库零变更
        row = _source_row(
            client, "SELECT status FROM orders WHERE order_id=?", (ORDER_CONFIRMED,)
        )
        assert row["status"] == "confirmed"

    def test_criteria_reference_missing_rule_blocks_run(self, client) -> None:
        """引用不存在的规则名 -> 拒绝执行。"""
        from src.builder.logic import action_types as at_repo

        store = client.app.state.runtime.store
        with store.ontology_conn() as conn:
            at_row = at_repo.get_by_name(conn, "cancel_order")
            at_repo.update_submission_criteria(conn, at_row.id, ["no_such_rule"])
        r = client.post(
            "/api/v1/builder/actions/cancel_order/run",
            headers={"X-Actor": "api"},
            json={"params": {"order_id": ORDER_CONFIRMED}},
        )
        assert r.status_code == 400
        assert r.json()["error"]["code"] == "BUILDER_LOGIC_RULE_NOT_PUBLISHED"


# ======================================================================
# 4. TD-6 provider achat 双轨
# ======================================================================


class TestProviderAsync:
    """TD-6：chat 保持同步兼容；achat 异步入口（真 DeepSeek 走线程池）。"""

    def test_mock_achat_returns_scripted(self, make_mock_provider) -> None:
        from src.agent.provider import ChatMessage, achat

        mock = make_mock_provider("clean_two_entities")
        resp = asyncio.run(achat(mock, [ChatMessage(role="user", content="提取")]))
        assert resp.content is not None
        assert json.loads(resp.content)["entities"][0]["name"] == "ACME"

    def test_mock_chat_still_sync(self, make_mock_provider) -> None:
        """存量同步调用方零改动（chat 仍是同步方法）。"""
        from src.agent.provider import ChatMessage

        mock = make_mock_provider("clean_two_entities")
        resp = mock.chat([ChatMessage(role="user", content="提取")])
        assert resp.content is not None

    def test_deepseek_achat_with_stub_client(self, monkeypatch) -> None:
        """DeepSeek achat：stub client 下可 await（to_thread 路径），映射不变。"""
        from types import SimpleNamespace

        from src.agent.provider import ChatMessage, DeepSeekProvider, achat

        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-fake-key")

        class Completions:
            def create(self, **kwargs):
                return SimpleNamespace(
                    choices=[
                        SimpleNamespace(
                            message=SimpleNamespace(content="异步回复", tool_calls=None)
                        )
                    ]
                )

        p = DeepSeekProvider()
        p._client = SimpleNamespace(chat=SimpleNamespace(completions=Completions()))
        resp = asyncio.run(p.achat([ChatMessage(role="user", content="hi")]))
        assert resp.content == "异步回复"
        # 模块级分发器走同一异步路径
        resp2 = asyncio.run(achat(p, [ChatMessage(role="user", content="hi")]))
        assert resp2.content == "异步回复"

    def test_achat_fallback_sync_only_provider(self) -> None:
        """仅实现同步 chat 的 duck-typed provider：分发器回退 to_thread。"""
        from src.agent.provider import ChatMessage, ChatResponse, achat

        class SyncOnly:
            def chat(self, messages, tools=None):
                return ChatResponse(content="sync-only")

        resp = asyncio.run(achat(SyncOnly(), [ChatMessage(role="user", content="x")]))
        assert resp.content == "sync-only"

    def test_extract_from_text_async(self, make_mock_provider) -> None:
        """异步提取入口与同步入口行为一致（E2E 经 achat）。"""
        from src.builder.extraction.extractor import (
            extract_from_text,
            extract_from_text_async,
        )

        mock = make_mock_provider("clean_two_entities")
        schema = {
            "entity_types_whitelist": ["company", "person"],
            "relation_types_whitelist": ["contact_of"],
        }
        result = asyncio.run(
            extract_from_text_async(
                "some doc", provider=mock, source_path="t.md", schema=schema
            )
        )
        assert len(result.payload.entities) == 2
        assert result.validation_report.has_fatal is False
        # 同步入口保持兼容（独立 provider 实例）
        mock2 = make_mock_provider("clean_two_entities")
        sync = extract_from_text(
            "some doc", provider=mock2, source_path="t.md", schema=schema
        )
        assert sync.payload.entities == result.payload.entities


# ======================================================================
# 5. TD-3 MockProvider 响应 fixture 精确断言
# ======================================================================


class TestExtractionFixturePrecision:
    """冻结响应 fixture：E2E 断言对 LLM 响应内容精确可控。"""

    def test_golden_scenario_exact_counts(self, make_mock_provider) -> None:
        from src.builder.extraction.extractor import extract_from_text

        mock = make_mock_provider("golden_with_problems")
        result = extract_from_text(
            "doc",
            provider=mock,
            source_path="supplier_memo.md",
            schema={
                "entity_types_whitelist": [
                    "company",
                    "person",
                    "product",
                    "logistics_provider",
                    "business_rule",
                    "approval_role",
                    "sku",
                    "order_amount_band",
                ],
            },
        )
        # 精确计数（fixture 固定）：19 干净 + marketing + dup + 重复陈志强 = 22
        assert len(result.payload.entities) == 22
        # V3 fatal（LR-999）+ V4 error（陈志强）+ V5 warning（marketing_artifact）
        assert result.validation_report.has_fatal is True
        assert result.validation_report.has_error is True

    def test_clean_scenario_exact(self, make_mock_provider) -> None:
        from src.builder.extraction.extractor import extract_from_text

        mock = make_mock_provider("clean_two_entities")
        result = extract_from_text(
            "doc",
            provider=mock,
            source_path="t.md",
            schema={"entity_types_whitelist": ["company", "person"]},
        )
        assert len(result.payload.entities) == 2
        assert result.validation_report.has_fatal is False
        assert result.validation_report.has_error is False


# ======================================================================
# 回归护栏：引擎 dry_run/observer 扩展不破坏既有 execute 语义
# ======================================================================


class TestEngineExtensionCompat:
    """execute 扩展参数缺省关闭，存量行为不变。"""

    def test_execute_without_new_params_unchanged(self, client) -> None:
        """不带 dry_run/observer 的直调引擎路径照常工作。"""
        rt = client.app.state.runtime
        result = rt.engine.execute(
            "confirm_order",
            {"order_id": ORDER_PENDING},
            actor="api",
        )
        assert result.outcome == "applied"
        row = _source_row(
            client, "SELECT status FROM orders WHERE order_id=?", (ORDER_PENDING,)
        )
        assert row["status"] == "confirmed"

    def test_snapshot_observer_called_before_reject(self, client) -> None:
        """observer 在拒绝路径早退前已回调（before 快照可拿到）。"""
        rt = client.app.state.runtime
        seen: dict = {}

        def observe(snapshot: dict) -> None:
            seen.update(snapshot)

        result = rt.engine.execute(
            "cancel_order",
            {"order_id": ORDER_SHIPPED},
            actor="api",
            snapshot_observer=observe,
        )
        assert result.outcome == "rejected"
        assert seen["order"]["status"] == "shipped"
        # 源库零变更
        row = _source_row(
            client, "SELECT status FROM orders WHERE order_id=?", (ORDER_SHIPPED,)
        )
        assert row["status"] == "shipped"


# ======================================================================
# TD-9：action_runs.executed_by CHECK 白名单（schema 层收口）
# ======================================================================


class TestExecutedByCheck:
    """TD-9：executed_by 白名单 CHECK（与 audit_log.actor 同源）在 DDL 层生效。"""

    def test_illegal_executed_by_direct_insert_rejected(self, client) -> None:
        """绕过应用层直插白名单外 executed_by -> IntegrityError（schema 兜底）。"""
        import sqlite3

        store = client.app.state.runtime.store
        with store.ontology_conn() as conn:
            with pytest.raises(sqlite3.IntegrityError, match="CHECK"):
                conn.execute(
                    "INSERT INTO action_runs (id, action_type_id, before_snapshot_json, "
                    "after_snapshot_json, status, error, executed_by, audit_ref, "
                    "created_at) VALUES (?,?,?,?,?,?,?,?,?)",
                    (
                        "arun_illegal_actor",
                        "at_cancel_order",
                        "{}",
                        "{}",
                        "applied",
                        "",
                        "robot",
                        "",
                        "2026-08-20 00:00:00",
                    ),
                )
            conn.rollback()  # 失败事务回滚，保持连接干净

    def test_legal_executed_by_values_accepted(self, client) -> None:
        """白名单内三个值均可直插（human/llm/api）。"""
        store = client.app.state.runtime.store
        with store.ontology_conn() as conn:
            for i, actor in enumerate(("human", "llm", "api")):
                conn.execute(
                    "INSERT INTO action_runs (id, action_type_id, before_snapshot_json, "
                    "after_snapshot_json, status, error, executed_by, audit_ref, "
                    "created_at) VALUES (?,?,?,?,?,?,?,?,?)",
                    (
                        f"arun_ok_{i}",
                        "at_cancel_order",
                        "{}",
                        "{}",
                        "dry_run",
                        "",
                        actor,
                        "",
                        "2026-08-20 00:00:00",
                    ),
                )
            conn.commit()
        with store.ontology_conn() as conn:
            got = {
                r["executed_by"]
                for r in conn.execute(
                    "SELECT executed_by FROM action_runs WHERE id LIKE 'arun_ok_%'"
                ).fetchall()
            }
        assert got == {"human", "llm", "api"}

    def test_check_values_same_source_as_allowed_actors(self) -> None:
        """同源机器检查：audit_log / action_runs 的 CHECK 值 == ALLOWED_ACTORS 派生值。"""
        from src.runtime import store as store_mod
        from src.runtime.action_engine import ALLOWED_ACTORS

        assert ALLOWED_ACTORS is store_mod.ALLOWED_ACTORS, "运行时校验必须与 store 单一来源"
        values_sql = "(" + ",".join(repr(a) for a in ALLOWED_ACTORS) + ")"
        assert f"CHECK (actor IN {values_sql})" in store_mod.ONTOLOGY_SCHEMA
        assert f"CHECK (executed_by IN {values_sql})" in store_mod.BUILDER_SCHEMA

    def test_migrate_rebuilds_action_runs_with_check_preserving_data(
        self, tmp_path
    ) -> None:
        """存量库（无 CHECK）经 Store.migrate 重建 action_runs：数据保留 + 约束生效。"""
        import sqlite3

        from src.runtime.store import Store

        db = tmp_path / "legacy_ontology.db"
        conn = sqlite3.connect(db)
        # 旧版 action_runs（TD-9 之前：无 executed_by CHECK）+ audit_log
        conn.executescript(
            "CREATE TABLE audit_log ("
            "audit_id TEXT PRIMARY KEY, ts TEXT NOT NULL, action_name TEXT NOT NULL, "
            "actor TEXT NOT NULL CHECK (actor IN ('human','llm','api')), "
            "actor_detail TEXT NOT NULL DEFAULT '', request_id TEXT NOT NULL DEFAULT '', "
            "params_json TEXT NOT NULL, preconditions_json TEXT NOT NULL DEFAULT '[]', "
            "effects_json TEXT NOT NULL DEFAULT '[]', writeback_json TEXT NOT NULL DEFAULT '[]', "
            "outcome TEXT NOT NULL CHECK (outcome IN ('applied','rejected','failed')), "
            "error_code TEXT, message TEXT, detail_json TEXT, duration_ms INTEGER NOT NULL DEFAULT 0"
            ");"
        )
        conn.executescript(
            "CREATE TABLE action_runs ("
            "id TEXT PRIMARY KEY, action_type_id TEXT NOT NULL, "
            "before_snapshot_json TEXT NOT NULL DEFAULT '{}', "
            "after_snapshot_json TEXT NOT NULL DEFAULT '{}', "
            "status TEXT NOT NULL CHECK (status IN ('applied','rejected','failed','dry_run')), "
            "error TEXT NOT NULL DEFAULT '', executed_by TEXT NOT NULL DEFAULT 'api', "
            "audit_ref TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL"
            ");"
        )
        conn.execute(
            "INSERT INTO action_runs (id, action_type_id, before_snapshot_json, "
            "after_snapshot_json, status, error, executed_by, audit_ref, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (
                "arun_legacy",
                "at_cancel_order",
                "{}",
                "{}",
                "applied",
                "",
                "llm",
                "audit_legacy",
                "2026-08-01 00:00:00",
            ),
        )
        conn.commit()
        conn.close()

        Store(ontology_path=db).migrate()

        conn = sqlite3.connect(db)
        (ddl,) = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='action_runs'"
        ).fetchone()
        assert "CHECK (executed_by IN" in ddl, "迁移后必须带 executed_by CHECK"
        row = conn.execute(
            "SELECT executed_by, audit_ref, status FROM action_runs WHERE id=?",
            ("arun_legacy",),
        ).fetchone()
        assert tuple(row) == ("llm", "audit_legacy", "applied"), "存量数据必须保留"
        with pytest.raises(sqlite3.IntegrityError, match="CHECK"):
            conn.execute(
                "INSERT INTO action_runs (id, action_type_id, before_snapshot_json, "
                "after_snapshot_json, status, error, executed_by, audit_ref, created_at) "
                "VALUES (?,?,?,?,?,?,?,?,?)",
                (
                    "arun_bad",
                    "x",
                    "{}",
                    "{}",
                    "applied",
                    "",
                    "robot",
                    "",
                    "2026-08-20 00:00:00",
                ),
            )
        conn.close()
