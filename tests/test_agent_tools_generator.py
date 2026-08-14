"""A2 验收测试：本体 schema → OpenAI function-calling tools（技术方案 §5.2）。

验收点：
- 6 个动作各生成 1 个 function tool，参数 schema 直接映射动作 params_schema；
- 至少 1 个只读查询工具（search_objects，对象类型枚举 = 注册表 8 类型）；
- golden 快照比对（6 动作 + 1 只读工具），schema 与 registry 一致；
- 结构性防注入：无泛化 update/任意字段工具（D-T3 / §5.2 约束 1）。
"""

import json
from pathlib import Path

import pytest

from src.agent.tools_generator import READ_TOOL_NAME, build_tools
from src.ontology import build_registry

GOLDEN = Path(__file__).resolve().parent / "golden" / "agent_tools_golden.json"

REG = build_registry()
EXPECTED_ACTION_NAMES = {a.name for a in REG.actions()}


@pytest.fixture(scope="module")
def tools() -> list[dict]:
    return build_tools(REG)


def _names(tools: list[dict]) -> list[str]:
    return [t["function"]["name"] for t in tools]


# ---------- 数量与命名 ----------


def test_build_tools_count(tools):
    """6 动作工具 + 1 只读工具 = 7。"""
    assert len(tools) == 7


def test_action_tool_names_match_registry(tools):
    action_names = set(_names(tools)) - {READ_TOOL_NAME}
    assert action_names == EXPECTED_ACTION_NAMES


def test_read_tool_present(tools):
    assert READ_TOOL_NAME in _names(tools)


# ---------- schema 与 registry 一致 ----------


def test_action_params_schema_maps_registry(tools):
    """动作工具 parameters == 动作 params_model 的 JSON Schema（一处定义四处消费）。"""
    by_name = {t["function"]["name"]: t["function"] for t in tools}
    for action in REG.actions():
        fn = by_name[action.name]
        assert fn["parameters"] == action.params_model.model_json_schema()
        assert fn["description"] == action.description  # 描述含前置规则摘要


def test_read_tool_object_type_enum(tools):
    read_fn = next(t for t in tools if t["function"]["name"] == READ_TOOL_NAME)[
        "function"
    ]
    enum = read_fn["parameters"]["properties"]["object_type"]["enum"]
    assert enum == sorted(o.api_name for o in REG.object_types())
    assert read_fn["parameters"]["required"] == ["object_type"]


def test_action_descriptions_contain_precondition_hints(tools):
    """§5.2 约束 3：动作描述含前置规则摘要，让 LLM 一次说对。"""
    by_name = {t["function"]["name"]: t["function"]["description"] for t in tools}
    assert "已发货" in by_name["cancel_order"]  # 已发货拦截提示
    assert "双签" in by_name["approve_refund"] or "确认" in by_name["approve_refund"]
    assert (
        "confirmed" in by_name["create_shipment"]
        or "已确认" in by_name["create_shipment"]
    )


# ---------- 结构性防注入（§5.2 约束 1：无泛化写工具） ----------


def test_no_generic_update_tool(tools):
    names = _names(tools)
    assert not any(
        n.startswith(("update_", "set_", "write_", "delete_", "insert_")) for n in names
    ), f"发现泛化写工具: {names}"
    # 动作工具名必须全部来自注册表（防 Action Sprawl，anti-pattern 6）
    assert set(names) == EXPECTED_ACTION_NAMES | {READ_TOOL_NAME}


def test_no_arbitrary_field_parameters(tools):
    """写工具参数必须白名单化：无自由对象透传字段（防任意字段写入，D-T3）。"""
    by_name = {t["function"]["name"]: t["function"] for t in tools}
    for action in REG.actions():
        params = by_name[action.name]["parameters"]
        props = {k: v for k, v in params["properties"].items() if not k.startswith("$")}
        assert props, f"{action.name} 参数不应为空"
        for fname, schema in props.items():
            # type=object 且无 properties 约束 = 自由对象透传 → 允许任意字段写入，禁止
            assert not (
                schema.get("type") == "object" and "properties" not in schema
            ), f"{action.name}.{fname} 是自由对象透传字段（防 Action Sprawl）"


# ---------- golden 快照 ----------


def test_golden_snapshot(tools):
    """golden 快照比对：改动 schema 必须同步更新 golden（验收：快照一致）。"""
    assert GOLDEN.exists(), f"golden 文件缺失: {GOLDEN}"
    actual = json.dumps(tools, ensure_ascii=False, indent=2, sort_keys=True)
    expected = GOLDEN.read_text(encoding="utf-8")
    assert actual == expected, (
        "tools JSON 与 golden 快照不一致（改 schema 需同步更新 golden）"
    )
