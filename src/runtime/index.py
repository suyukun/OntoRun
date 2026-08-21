"""本体对象索引（B1，技术方案 §3.1 index / §3.2 索引设计）。

- 启动：从源系统库全量加载到内存（§7.4 取舍：MVP 无 Funnel 增量管线，千级对象全量足够）；
- 动作后：action_engine 在源库提交后调 refresh()/refresh_many() 增量同步（§3.3 ⑦）；
- derived 计算态（§2.7）：available_qty / line_total_cents 加载时算出、永不写回；
- ontology-owned 本体自有状态（如 cancel_reason）单独存放，get 时合并。

链接索引语义（§2.3 双向链接，§3.2 双向遍历）：
- out[(type, pk)][name]：从该对象出发可到达的另一端对象主键。
  name = L.name（本对象在 source 侧）或 L.inverse_name（本对象在 target 侧）；
- in[(type, pk)][name]：指向该对象的另一端对象主键（"谁引用了我"）。
  name = L.inverse_name（本对象在 source 侧）或 L.name（本对象在 target 侧）。
- 遍历规则：
  direction=out → (L.name + L.source_type==type) 或 (L.inverse_name + L.target_type==type)；
  direction=in  → (L.inverse_name + L.source_type==type) 或 (L.name + L.target_type==type)。
"""

from __future__ import annotations

import sqlite3
from typing import Any

from src.ontology.objects import OWN_ONTOLOGY, field_ownership
from src.ontology.registry import Registry

# derived 字段计算器：<Type>.<field> -> fn(attrs) -> value（与 objects.py OWN_DERIVED 标注对应）
_DERIVED_COMPUTERS: dict[str, Any] = {
    "Inventory.available_qty": lambda a: a["on_hand_qty"] - a["reserved_qty"],
    "OrderItem.line_total_cents": lambda a: a["qty"] * a["unit_price_cents"],
}


class ObjectIndex:
    """内存对象索引：PK→对象、链接正/反向索引、ontology-owned 状态合并。"""

    def __init__(self, registry: Registry) -> None:
        self._registry = registry
        self._objects: dict[str, dict[str, dict[str, Any]]] = {}  # type -> pk -> attrs
        self._out: dict[
            tuple[str, str], dict[str, list[str]]
        ] = {}  # 出向（本对象出发）
        self._in: dict[tuple[str, str], dict[str, list[str]]] = {}  # 入向（指向本对象）
        self._ontology_state: dict[
            tuple[str, str, str], Any
        ] = {}  # (type,pk,prop) -> value

    # ---- 加载 ----

    def load_all(self, conn: sqlite3.Connection) -> None:
        """从源系统库全量加载对象类型并重建链接索引。

        本库无该类型的源表时保留空 bucket（如零售库无 DES 物化表 Material/Code），
        保证 list_all 返回空列表而非 KeyError；源表存在才读行。
        """
        self._objects.clear()
        self._out.clear()
        self._in.clear()
        conn.row_factory = sqlite3.Row
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        for obj in self._registry.object_types():
            bucket = self._objects.setdefault(obj.name, {})
            if obj.source_table not in tables:
                continue  # 该类型的源表不在本库 → 本库无实例
            for row in conn.execute(f"SELECT * FROM {obj.source_table}"):
                attrs = dict(row)
                self._apply_derived(obj.name, attrs)
                bucket[str(attrs[obj.pk_field])] = attrs
        self._rebuild_links()

    def load_ontology_state(self, conn: sqlite3.Connection | None) -> None:
        """加载 ontology-owned 状态（本体库 ontology_state 表）；无本体库则跳过。"""
        if conn is None:
            return
        conn.row_factory = sqlite3.Row
        for row in conn.execute(
            "SELECT object_type, pk, prop, value FROM ontology_state"
        ):
            self._ontology_state[(row["object_type"], row["pk"], row["prop"])] = row[
                "value"
            ]

    def set_ontology_state(
        self, type_name: str, pk: str, prop: str, value: Any
    ) -> None:
        """写入/清除一条 ontology-owned 状态（get 时合并）。"""
        if value is None:
            self._ontology_state.pop((type_name, pk, prop), None)
        else:
            self._ontology_state[(type_name, pk, prop)] = value

    def _apply_derived(self, type_name: str, attrs: dict[str, Any]) -> None:
        for field in self._registry.object_type(type_name).model.model_fields:
            fn = _DERIVED_COMPUTERS.get(f"{type_name}.{field}")
            if fn is not None:
                attrs[field] = fn(attrs)

    def _link_object(self, type_name: str, pk: str, attrs: dict[str, Any]) -> None:
        """把单个对象加入正/反向链接索引（端点两侧全覆盖，读时去重）。

        - source 侧（N:1：FK 在本对象，直接取目标；1:N：扫描 target 侧 fk==pk）；
        - target 侧（1:N：FK 在本对象，直接取源；N:1：扫描 source 侧 fk==pk）。
        增量 refresh 与全量 rebuild 共用同一规则，保证任一端点更新后链接完整。
        """
        for link in self._registry.link_types():
            if link.source_type == type_name:
                if link.cardinality == "N:1":
                    tgt = attrs.get(link.fk_field)
                    if tgt is not None:
                        tgt = str(tgt)
                        self._out.setdefault((type_name, pk), {}).setdefault(
                            link.name, []
                        ).append(tgt)
                        # TD-14 修复：source 侧 N:1 补写入向（"谁引用了我"）——
                        # target 对象经 inverse_name 指向本对象，此前缺此数据路径（入向空）
                        self._in.setdefault((type_name, pk), {}).setdefault(
                            link.inverse_name, []
                        ).append(tgt)
                else:
                    targets = [
                        t_pk
                        for t_pk, t_attrs in self._objects.get(
                            link.target_type, {}
                        ).items()
                        if t_attrs.get(link.fk_field) == pk
                    ]
                    for t_pk in targets:
                        self._out.setdefault((type_name, pk), {}).setdefault(
                            link.name, []
                        ).append(t_pk)
                        self._in.setdefault((link.target_type, t_pk), {}).setdefault(
                            link.name, []
                        ).append(pk)
            if link.target_type == type_name:
                if link.cardinality == "N:1":
                    # T 侧：扫描 source 侧 fk==pk → T 出向走 L.inverse_name、T 入向走 L.name
                    sources = [
                        s_pk
                        for s_pk, s_attrs in self._objects.get(
                            link.source_type, {}
                        ).items()
                        if s_attrs.get(link.fk_field) == pk
                    ]
                    for s_pk in sources:
                        self._out.setdefault((type_name, pk), {}).setdefault(
                            link.inverse_name, []
                        ).append(s_pk)
                        self._in.setdefault((type_name, pk), {}).setdefault(
                            link.name, []
                        ).append(s_pk)
                else:
                    src = attrs.get(link.fk_field)
                    if src is not None:
                        src = str(src)
                        self._out.setdefault((type_name, pk), {}).setdefault(
                            link.inverse_name, []
                        ).append(src)
                        self._out.setdefault((link.source_type, src), {}).setdefault(
                            link.name, []
                        ).append(pk)
                        self._in.setdefault((link.source_type, src), {}).setdefault(
                            link.inverse_name, []
                        ).append(pk)

    def _rebuild_links(self) -> None:
        """按 8 条链接定义重建正/反向索引（FK 位置：N:1 在 source、1:N 在 target）。"""
        self._out.clear()
        self._in.clear()
        for obj in self._registry.object_types():
            for pk, attrs in self._objects[obj.name].items():
                self._link_object(obj.name, pk, attrs)

    # ---- 读取 ----

    def list_all(self, type_name: str) -> list[dict[str, Any]]:
        return list(self._objects[type_name].values())

    def get(self, type_name: str, pk: str) -> dict[str, Any] | None:
        """按主键取对象（合并 ontology-owned 状态并补默认值）；不存在返回 None。"""
        attrs = self._objects.get(type_name, {}).get(str(pk))
        if attrs is None:
            return None
        merged = dict(attrs)
        for (t, p, prop), value in self._ontology_state.items():
            if t == type_name and p == str(pk):
                merged[prop] = value
        # ontology-owned 字段未落库时补模型默认值（保持 schema 输出完整，§2.7）
        obj = self._registry.object_type(type_name)
        for fname in obj.model.model_fields:
            if (
                field_ownership(obj.model, fname) == OWN_ONTOLOGY
                and fname not in merged
            ):
                merged[fname] = None
        return merged

    def get_link_counts(self, type_name: str, pk: str) -> dict[str, dict[str, int]]:
        """详情用链接计数：out（本对象出发）/ in（指向本对象），未命中的链接补 0。

        out 名：source 侧 L.name / target 侧 L.inverse_name；
        in 名：source 侧 L.inverse_name / target 侧 L.name（"谁引用了我"）。
        """
        key = (type_name, str(pk))
        out_names, in_names = [], []
        for link in self._registry.link_types():
            if link.source_type == type_name:
                out_names.append(link.name)
                in_names.append(link.inverse_name)
            if link.target_type == type_name:
                out_names.append(link.inverse_name)
                in_names.append(link.name)
        out_map = self._out.get(key, {})
        in_map = self._in.get(key, {})
        out = {name: len(set(out_map.get(name, []))) for name in out_names}
        inn = {name: len(set(in_map.get(name, []))) for name in in_names}
        return {"out": out, "in": inn}

    def get_links(
        self, type_name: str, pk: str, link_name: str, direction: str = "out"
    ) -> list[dict[str, Any]]:
        """链接遍历：direction=out（本对象出发）/ in（指向本对象），返回另一端完整对象。"""
        key = (type_name, str(pk))
        if direction == "out":
            hit = self._find_link(link_name, type_name=type_name, forward=True)
            if hit is None:
                return []
            link, side = hit
            idx_key = link.name if side == "source" else link.inverse_name
            other_type = link.target_type if side == "source" else link.source_type
        elif direction == "in":
            hit = self._find_link(link_name, type_name=type_name, forward=False)
            if hit is None:
                return []
            link, side = hit
            idx_key = link.inverse_name if side == "source" else link.name
            other_type = link.target_type if side == "source" else link.source_type
        else:
            raise ValueError(f"非法 direction: {direction}")
        bucket = self._objects.get(other_type, {})
        idx = self._out if direction == "out" else self._in
        seen: set[str] = set()
        result = []
        for p in idx.get(key, {}).get(idx_key, []):
            if p in bucket and p not in seen:
                seen.add(p)
                result.append(bucket[p])
        return result

    def _find_link(
        self, link_name: str, *, type_name: str, forward: bool
    ) -> tuple | None:
        """按遍历名定位链接；forward=True=出向。返回 (link, side)；side ∈ {source, target}。

        出向：L.name+source 侧，或 L.inverse_name+target 侧；
        入向：L.inverse_name+source 侧，或 L.name+target 侧。
        """
        for link in self._registry.link_types():
            if forward:
                if link.name == link_name and link.source_type == type_name:
                    return (link, "source")
                if link.inverse_name == link_name and link.target_type == type_name:
                    return (link, "target")
            else:
                if link.inverse_name == link_name and link.source_type == type_name:
                    return (link, "source")
                if link.name == link_name and link.target_type == type_name:
                    return (link, "target")
        return None

    # ---- 增量更新（§3.3 ⑦：源库提交后同步索引） ----

    def refresh(self, type_name: str, pk: str, conn: sqlite3.Connection) -> None:
        """从源库重读单行并更新对象与链接（FK 变更也能正确处理）。"""
        obj = self._registry.object_type(type_name)
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            f"SELECT * FROM {obj.source_table} WHERE {obj.pk_field}=?", (str(pk),)
        ).fetchone()
        if row is None:
            self._remove_object(type_name, str(pk))
            return
        attrs = dict(row)
        self._apply_derived(type_name, attrs)
        self._objects.setdefault(type_name, {})[str(pk)] = attrs
        self._reindex_object(type_name, str(pk), attrs)

    def refresh_many(
        self, pairs: list[tuple[str, str]], conn: sqlite3.Connection
    ) -> None:
        for type_name, pk in pairs:
            self.refresh(type_name, pk, conn)

    def _remove_object(self, type_name: str, pk: str) -> None:
        self._objects.get(type_name, {}).pop(pk, None)
        for idx in (self._out, self._in):
            idx.pop((type_name, pk), None)
            for (t, p), links in list(idx.items()):
                for name, pks in list(links.items()):
                    if pk in pks:
                        links[name] = [v for v in pks if v != pk]
                        if not links[name]:
                            del links[name]
                if not links:
                    del idx[(t, p)]

    def _reindex_object(self, type_name: str, pk: str, attrs: dict[str, Any]) -> None:
        """清除该对象旧链接条目并按当前 FK 重建。"""
        self._remove_object(type_name, pk)
        self._objects.setdefault(type_name, {})[pk] = attrs
        self._link_object(type_name, pk, attrs)
