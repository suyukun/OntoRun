"""对象查询层（B1，技术方案 §3.1 query / §3.2 查询设计）。

- list_objects：等值过滤（MVP：等值与枚举，§3.2）+ 分页（page/page_size），主键升序确定性；
- get_detail：全属性 + 出/入向链接计数（供前端"链接导航"tab）；
- get_links：双向链接遍历（§2.3 / §3.2），direction=out|in。

查询只读内存索引；读错误抛 QueryError 子类，由 API 层映射为信封错误。
"""
from __future__ import annotations

from typing import Any

from src.ontology.registry import Registry
from src.runtime.index import ObjectIndex


class QueryError(Exception):
    """查询层错误基类（API 层映射 HTTP/信封）。"""


class UnknownObjectType(QueryError):
    def __init__(self, type_name: str) -> None:
        self.type_name = type_name
        super().__init__(f"未知对象类型: {type_name}")


class ObjectNotFound(QueryError):
    def __init__(self, type_name: str, pk: str) -> None:
        self.type_name, self.pk = type_name, pk
        super().__init__(f"对象不存在: {type_name}/{pk}")


class LinkNotFound(QueryError):
    def __init__(self, type_name: str, link_name: str) -> None:
        self.type_name, self.link_name = type_name, link_name
        super().__init__(f"链接不存在或不可从 {type_name} 遍历: {link_name}")


class InvalidDirection(QueryError):
    def __init__(self, direction: str) -> None:
        self.direction = direction
        super().__init__(f"非法遍历方向: {direction}（应为 out/in）")


class UnknownFilterField(QueryError):
    def __init__(self, type_name: str, field: str) -> None:
        self.type_name, self.field = type_name, field
        super().__init__(f"过滤字段不存在: {type_name}.{field}")


MAX_PAGE_SIZE = 200


class ObjectQuery:
    """本体对象查询（只读内存索引）。"""

    def __init__(self, index: ObjectIndex, registry: Registry) -> None:
        self._index = index
        self._registry = registry

    def resolve_type(self, type_name: str) -> Any:
        """按类型名（Order）或 api_name（order）解析对象类型定义。"""
        for obj in self._registry.object_types():
            if obj.name == type_name or obj.api_name == type_name:
                return obj
        raise UnknownObjectType(type_name)

    def list_objects(self, type_name: str, filters: dict[str, Any] | None = None,
                     page: int = 1, page_size: int = 20) -> tuple[list[dict], int]:
        """对象列表：等值过滤 + 分页。返回 (items, total)，items 按主键升序。"""
        obj = self.resolve_type(type_name)
        filters = filters or {}
        attrs_list = self._index.list_all(obj.name)
        known = obj.model.model_fields
        for field in filters:
            if field not in known:
                raise UnknownFilterField(obj.name, field)
        if filters:
            attrs_list = [a for a in attrs_list
                          if all(str(a.get(f)) == str(v) for f, v in filters.items())]
        attrs_list.sort(key=lambda a: str(a[obj.pk_field]))
        total = len(attrs_list)
        start = max(page - 1, 0) * page_size
        items = [self._wrap(obj, a) for a in attrs_list[start:start + page_size]]
        return items, total

    def get(self, type_name: str, pk: str) -> dict | None:
        obj = self.resolve_type(type_name)
        attrs = self._index.get(obj.name, str(pk))
        return self._wrap(obj, attrs) if attrs else None

    def get_detail(self, type_name: str, pk: str) -> dict:
        """对象详情：全属性 + 出/入向链接计数。"""
        obj = self.resolve_type(type_name)
        attrs = self._index.get(obj.name, str(pk))
        if attrs is None:
            raise ObjectNotFound(obj.name, str(pk))
        return {
            "object_type": obj.name,
            "pk": str(pk),
            "properties": attrs,
            "links": self._index.get_link_counts(obj.name, str(pk)),
        }

    def get_links(self, type_name: str, pk: str, link_name: str,
                  direction: str = "out") -> list[dict]:
        """链接遍历：direction=out|in，返回另一端对象列表（完整属性）。"""
        if direction not in ("out", "in"):
            raise InvalidDirection(direction)
        obj = self.resolve_type(type_name)
        if self._index.get(obj.name, str(pk)) is None:
            raise ObjectNotFound(obj.name, str(pk))
        other_type = self._other_type(obj.name, link_name, direction)
        if other_type is None:
            raise LinkNotFound(obj.name, link_name)
        others = self._index.get_links(obj.name, str(pk), link_name, direction)
        other_def = self._registry.object_type(other_type)
        return [self._wrap(other_def, a) for a in others]

    def _other_type(self, type_name: str, link_name: str, direction: str) -> str | None:
        """定位另一端对象类型；name/方向不合法返回 None（链接不存在）。"""
        for link in self._registry.link_types():
            if direction == "out":
                if link.name == link_name and link.source_type == type_name:
                    return link.target_type
                if link.inverse_name == link_name and link.target_type == type_name:
                    return link.source_type
            else:
                if link.inverse_name == link_name and link.source_type == type_name:
                    return link.target_type
                if link.name == link_name and link.target_type == type_name:
                    return link.source_type
        return None

    @staticmethod
    def _wrap(obj_def: Any, attrs: dict[str, Any]) -> dict:
        return {"object_type": obj_def.name, "pk": str(attrs[obj_def.pk_field]),
                "properties": attrs}
