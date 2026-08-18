"""GraphStore 抽象接口（重写蓝图 v0.3 §1.3 / 补丁 v0.3.1 B2）。

最小方法集（业务当前只用到这些，后续按需扩展）：
- add_node / get_node / remove_node：节点 CRUD；
- add_edge / remove_edge：边 CRUD（删除级联到节点时由实现决定）；
- neighbors(node_id, direction)：一/两跳邻居查询（direction ∈ out/in/both）；

设计原则：
- 节点 / 边用 frozen dataclass（不可变，更新返回新对象，对齐项目"数据不可变"规范）；
- 接口不暴露具体存储后端，SQLite/Neo4j 实现零业务改动即可替换；
- attrs / properties 以 JSON 字符串存储（SQLite 简单实现层），抽象层不感知。
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Node:
    """图节点（frozen：不可变，新增/更新走 add_node 覆盖）。"""

    id: str
    kind: str = "entity"
    attrs: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Edge:
    """有向边（frozen；无向关系由两条反向 Edge 表达）。"""

    src: str
    dst: str
    kind: str = "related"
    attrs: dict[str, Any] = field(default_factory=dict)


class GraphStore(abc.ABC):
    """Graph 存储抽象基类（蓝图 §1.3 / 补丁 B2）。"""

    @abc.abstractmethod
    def add_node(self, node: Node) -> None: ...

    @abc.abstractmethod
    def get_node(self, node_id: str) -> Node | None: ...

    @abc.abstractmethod
    def remove_node(self, node_id: str) -> None: ...

    @abc.abstractmethod
    def add_edge(self, edge: Edge) -> None: ...

    @abc.abstractmethod
    def remove_edge(self, src: str, dst: str, kind: str) -> None: ...

    @abc.abstractmethod
    def neighbors(self, node_id: str, direction: str = "out") -> list[Node]: ...

    @abc.abstractmethod
    def close(self) -> None: ...
