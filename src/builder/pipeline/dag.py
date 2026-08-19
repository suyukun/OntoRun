"""DAG 引擎（蓝图 v0.3 §9-P2 / 补丁 C4）。

管道 = DAG：

    节点 = {id, kind, config, next[]}
    kind ∈ {connector, storage, transform, output}
        - connector：拉取数据（CSV/JSON/XML/MD 读取，返回 list[dict]）
        - transform：处理数据（schema_infer / cleanse / flatten / parse_xml / md_to_struct ...）
        - storage   ：写回 / 落盘（curated 落库、文件落 data/curated/...）
        - output    ：终态出口（返回给调用方）

状态机（每节点）：
    pending → running → succeeded | failed | skipped
       pending 表示等待上游完成
       skipped 表示上游 failed/未命中传播条件

执行规则（蓝图 §9-P2）：
    1. 拓扑排序；无环。
    2. 按拓扑序逐节点执行；每节点同步等到上游全部 succeeded 才启动。
    3. 任一节点 failed → 该节点 downstream 全标 skipped；其他无依赖分支继续。
    4. 入口节点（无前驱）若多条并行为同一数据集的不同 connector：分别独立运行。
    5. 终止条件：所有节点进入终态（succeeded / failed / skipped）。

返回值：PipelineRun（节点状态 map + 终态 + 错误汇总）。
"""

from __future__ import annotations

import enum
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

# ----------------------------------------------------------------------
# JSON schema 定义（C4 补丁：本模块是 DAG 结构的单一来源）
# ----------------------------------------------------------------------

NODE_KINDS: tuple[str, ...] = ("connector", "storage", "transform", "output")

DAG_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "OntoRun Builder Pipeline DAG",
    "type": "object",
    "required": ["nodes"],
    "properties": {
        "nodes": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "kind"],
                "properties": {
                    "id": {"type": "string", "minLength": 1},
                    "kind": {"enum": list(NODE_KINDS)},
                    "config": {"type": "object"},
                    "next": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "additionalProperties": False,
            },
        },
    },
    "additionalProperties": False,
}


# ----------------------------------------------------------------------
# 节点状态机
# ----------------------------------------------------------------------


class NodeStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"


TERMINAL: frozenset[NodeStatus] = frozenset(
    {NodeStatus.SUCCEEDED, NodeStatus.FAILED, NodeStatus.SKIPPED}
)


# ----------------------------------------------------------------------
# 数据类
# ----------------------------------------------------------------------


@dataclass(frozen=True)
class Node:
    """DAG 节点（不可变）。"""

    id: str
    kind: str
    config: dict[str, Any] = field(default_factory=dict)
    next: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.kind not in NODE_KINDS:
            raise ValueError(
                f"node {self.id!r} kind 非法: {self.kind!r}（应为 {NODE_KINDS}）"
            )


@dataclass(frozen=True)
class NodeResult:
    """单节点执行结果。"""

    node_id: str
    status: NodeStatus
    error: str | None = None
    output: Any = None  # 任意类型，供下游 transform / output 消费


@dataclass(frozen=True)
class PipelineRun:
    """一次管道执行的总结果。"""

    nodes: dict[str, NodeResult]
    final_status: NodeStatus  # 整体终态：全 succeeded→succeeded；任一 failed→failed；否则 partial
    error: str | None = None


# ----------------------------------------------------------------------
# 异常
# ----------------------------------------------------------------------


class DAGValidationError(ValueError):
    """DAG 拓扑/结构非法：环、孤立节点、id 重复、next 指向不存在节点。"""


# ----------------------------------------------------------------------
# Handler 协议
# ----------------------------------------------------------------------

# Handler 签名：handler(node, upstream_outputs) -> Any
#   - node: 当前 Node
#   - upstream_outputs: dict[upstream_node_id -> output]，用于跨节点数据传递
NodeHandler = Callable[[Node, dict[str, Any]], Any]


# ----------------------------------------------------------------------
# DAG 校验 + 拓扑排序
# ----------------------------------------------------------------------


def validate_dag(nodes: list[Node]) -> dict[str, list[str]]:
    """校验 + 返回 adjacency 与 in-degree 信息。

    raises DAGValidationError：id 重复、next 指向未知 id、自环（直接成环）、整体成环。
    returns: {downstream: {node_id -> [next_node_id]},
              indegree: {node_id -> in-degree}}
    """
    ids: list[str] = [n.id for n in nodes]
    if len(ids) != len(set(ids)):
        seen: set[str] = set()
        dups: list[str] = []
        for i in ids:
            if i in seen:
                dups.append(i)
            seen.add(i)
        raise DAGValidationError(f"DAG 节点 id 重复: {dups}")
    id_set: set[str] = set(ids)
    downstream: dict[str, list[str]] = {i: [] for i in id_set}
    indegree: dict[str, int] = {i: 0 for i in id_set}
    for n in nodes:
        for nxt in n.next:
            if nxt not in id_set:
                raise DAGValidationError(
                    f"节点 {n.id!r} 的 next 指向未知节点 {nxt!r}"
                )
            if nxt == n.id:
                raise DAGValidationError(f"节点 {n.id!r} 存在自环")
            downstream[n.id].append(nxt)
            indegree[nxt] += 1
    return {"downstream": downstream, "indegree": indegree}


def topological_order(nodes: list[Node]) -> list[str]:
    """Kahn 拓扑排序；遇到环抛 DAGValidationError。"""
    info = validate_dag(nodes)
    indegree: dict[str, int] = dict(info["indegree"])
    downstream: dict[str, list[str]] = info["downstream"]
    by_id: dict[str, Node] = {n.id: n for n in nodes}
    queue: deque[str] = deque(sorted(i for i, d in indegree.items() if d == 0))
    order: list[str] = []
    while queue:
        nid = queue.popleft()
        order.append(nid)
        for nxt in downstream[nid]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    if len(order) != len(by_id):
        cyclic: list[str] = [i for i, d in indegree.items() if d > 0]
        raise DAGValidationError(f"DAG 存在环，未完成拓扑: {cyclic}")
    return order


# ----------------------------------------------------------------------
# 执行
# ----------------------------------------------------------------------


def _propagate_skip(
    node_id: str,
    downstream: dict[str, list[str]],
    states: dict[str, NodeStatus],
) -> None:
    """BFS 把所有受影响的下游标 skipped（仅当尚未终态）。"""
    queue: deque[str] = deque(downstream[node_id])
    while queue:
        nid = queue.popleft()
        if states[nid] in TERMINAL:
            continue
        states[nid] = NodeStatus.SKIPPED
        for nxt in downstream[nid]:
            if states[nxt] not in TERMINAL:
                queue.append(nxt)


def run_pipeline(
    nodes: list[Node],
    handlers: dict[str, NodeHandler],
) -> PipelineRun:
    """同步执行 DAG，按拓扑序逐节点；失败即停传播（下游 SKIPPED）。

    handlers[node_id] = (node, upstream_outputs) -> output
        upstream_outputs = {upstream_node_id -> output_value}

    返回：PipelineRun（每节点 NodeResult，整体终态）。
    """
    info = validate_dag(nodes)
    downstream: dict[str, list[str]] = info["downstream"]
    by_id: dict[str, Node] = {n.id: n for n in nodes}
    order: list[str] = topological_order(nodes)
    states: dict[str, NodeStatus] = {i: NodeStatus.PENDING for i in by_id}
    outputs: dict[str, Any] = {}
    upstream: dict[str, list[str]] = defaultdict(list)
    for nid, deg in info["indegree"].items():
        if deg == 0:
            continue
        for src, dst_list in downstream.items():
            if nid in dst_list:
                upstream[nid].append(src)

    for nid in order:
        if states[nid] != NodeStatus.PENDING:
            continue
        node = by_id[nid]
        handler = handlers.get(nid)
        if handler is None:
            states[nid] = NodeStatus.FAILED
            outputs[nid] = None
            _propagate_skip(nid, downstream, states)
            continue
        states[nid] = NodeStatus.RUNNING
        upstream_outputs = {u: outputs.get(u) for u in upstream[nid]}
        try:
            out = handler(node, upstream_outputs)
        except Exception:  # noqa: BLE001 —— DAG 引擎吞所有节点异常
            states[nid] = NodeStatus.FAILED
            outputs[nid] = None
            _propagate_skip(nid, downstream, states)
            continue
        states[nid] = NodeStatus.SUCCEEDED
        outputs[nid] = out

    status_set = set(states.values())
    if status_set == {NodeStatus.SUCCEEDED}:
        final = NodeStatus.SUCCEEDED
    elif NodeStatus.FAILED in status_set:
        final = NodeStatus.FAILED
    else:
        # 仅 SKIPPED（理论上不会发生，但兜底）→ 视作 partial → failed
        final = NodeStatus.FAILED

    results: dict[str, NodeResult] = {
        nid: NodeResult(
            node_id=nid,
            status=states[nid],
            error=None if states[nid] == NodeStatus.SUCCEEDED else states[nid].value,
            output=outputs.get(nid),
        )
        for nid in by_id
    }
    return PipelineRun(nodes=results, final_status=final)


# ----------------------------------------------------------------------
# Pipeline def 解析（POST /pipelines 的 JSON body -> list[Node]）
# ----------------------------------------------------------------------


def parse_dag(raw: dict[str, Any]) -> list[Node]:
    """把 JSON body 解析为 list[Node]。

    接受两种形态：
      1) {"nodes": [{"id", "kind", "config?", "next?"}, ...]}
      2) {"dag": {"nodes": [...]}}  — 兼容 envelope
    """
    if "dag" in raw and isinstance(raw["dag"], dict):
        raw = raw["dag"]
    nodes_raw = raw.get("nodes")
    if not isinstance(nodes_raw, list) or not nodes_raw:
        raise DAGValidationError("DAG 必须含非空 nodes 列表")
    out: list[Node] = []
    for n in nodes_raw:
        if not isinstance(n, dict):
            raise DAGValidationError(f"node 必须是 dict: {n!r}")
        kind = n.get("kind")
        if kind not in NODE_KINDS:
            raise DAGValidationError(f"node.kind 非法: {kind!r}")
        out.append(
            Node(
                id=str(n["id"]),
                kind=str(kind),
                config=dict(n.get("config") or {}),
                next=tuple(n.get("next") or ()),
            )
        )
    # 一次性校验（id 重复 / next 未知 / 自环 / 环）
    validate_dag(out)
    return out
