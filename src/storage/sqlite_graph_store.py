"""SQLite 关系表 GraphStore 实现（蓝图 v0.3 §1.3 / 补丁 v0.3.1 B2）。

设计要点：
- 节点表 graph_nodes(id PK, kind, attrs_json) / 边表 graph_edges(src, dst, kind, attrs_json)；
- 默认存到本体库（data/ontology/ontology.db，与 builder 段共库），也接受外部 db_path 注入；
- 删节点级联删边（PRAGMA foreign_keys=ON + ON DELETE CASCADE）；
- 同一 src/dst/kind 三元组唯一（PK），重复 add_edge 走 INSERT OR REPLACE 覆盖。
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from src.storage.graph_store import Edge, GraphStore, Node


class SQLiteGraphStore(GraphStore):
    """SQLite 关系表实现的 GraphStore（节点/边两张表 + 索引）。"""

    SCHEMA = """
    CREATE TABLE IF NOT EXISTS graph_nodes (
      id          TEXT PRIMARY KEY,
      kind        TEXT NOT NULL DEFAULT 'entity',
      attrs_json  TEXT NOT NULL DEFAULT '{}',
      updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS graph_edges (
      src         TEXT NOT NULL,
      dst         TEXT NOT NULL,
      kind        TEXT NOT NULL DEFAULT 'related',
      attrs_json  TEXT NOT NULL DEFAULT '{}',
      updated_at  TEXT NOT NULL DEFAULT (datetime('now')),
      PRIMARY KEY (src, dst, kind),
      FOREIGN KEY (src) REFERENCES graph_nodes(id) ON DELETE CASCADE,
      FOREIGN KEY (dst) REFERENCES graph_nodes(id) ON DELETE CASCADE
    );
    CREATE INDEX IF NOT EXISTS idx_graph_edges_src ON graph_edges(src);
    CREATE INDEX IF NOT EXISTS idx_graph_edges_dst ON graph_edges(dst);
    """

    def __init__(self, db_path: str | Path) -> None:
        self._path = Path(db_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self._path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.executescript(self.SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def _now(self) -> str:
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def add_node(self, node: Node) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO graph_nodes (id, kind, attrs_json, updated_at) "
            "VALUES (?,?,?,?)",
            (node.id, node.kind, json.dumps(node.attrs, ensure_ascii=False), self._now()),
        )
        self._conn.commit()

    def get_node(self, node_id: str) -> Node | None:
        row = self._conn.execute(
            "SELECT id, kind, attrs_json FROM graph_nodes WHERE id = ?",
            (node_id,),
        ).fetchone()
        if row is None:
            return None
        return Node(
            id=row["id"],
            kind=row["kind"],
            attrs=json.loads(row["attrs_json"] or "{}"),
        )

    def remove_node(self, node_id: str) -> None:
        # PRAGMA foreign_keys=ON 保证级联删边
        self._conn.execute("DELETE FROM graph_nodes WHERE id = ?", (node_id,))
        self._conn.commit()

    def add_edge(self, edge: Edge) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO graph_edges (src, dst, kind, attrs_json, updated_at) "
            "VALUES (?,?,?,?,?)",
            (
                edge.src,
                edge.dst,
                edge.kind,
                json.dumps(edge.attrs, ensure_ascii=False),
                self._now(),
            ),
        )
        self._conn.commit()

    def remove_edge(self, src: str, dst: str, kind: str) -> None:
        self._conn.execute(
            "DELETE FROM graph_edges WHERE src = ? AND dst = ? AND kind = ?",
            (src, dst, kind),
        )
        self._conn.commit()

    def neighbors(self, node_id: str, direction: str = "out") -> list[Node]:
        """一阶邻居查询。direction ∈ out/in/both。"""
        if direction == "out":
            rows = self._conn.execute(
                "SELECT n.id, n.kind, n.attrs_json FROM graph_edges e "
                "JOIN graph_nodes n ON n.id = e.dst "
                "WHERE e.src = ?",
                (node_id,),
            ).fetchall()
        elif direction == "in":
            rows = self._conn.execute(
                "SELECT n.id, n.kind, n.attrs_json FROM graph_edges e "
                "JOIN graph_nodes n ON n.id = e.src "
                "WHERE e.dst = ?",
                (node_id,),
            ).fetchall()
        elif direction == "both":
            rows = self._conn.execute(
                "SELECT n.id, n.kind, n.attrs_json FROM graph_nodes n WHERE n.id IN ("
                "  SELECT dst FROM graph_edges WHERE src = ?"
                "  UNION"
                "  SELECT src FROM graph_edges WHERE dst = ?"
                ")",
                (node_id, node_id),
            ).fetchall()
        else:
            raise ValueError(f"direction 必须为 out/in/both，实测 {direction!r}")
        return [
            Node(
                id=r["id"],
                kind=r["kind"],
                attrs=json.loads(r["attrs_json"] or "{}"),
            )
            for r in rows
        ]
