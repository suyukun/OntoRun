"""结果比较层：GT vs 两形态答案，数值容差 + 集合判定（设计 §4.2 成功率口径）。"""
from __future__ import annotations

import math
from typing import Any


def _num(v: Any) -> float | None:
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v)
        except ValueError:
            return None
    return None


def close(a: Any, b: Any, rel: float = 5e-3, abs_: float = 1e-3) -> bool:
    """数值按相对容差比对（相对量级 + 绝对 epsilon，避免小数值被相对地板放过）；非数值按字符串精确比对。"""
    na, nb = _num(a), _num(b)
    if na is None or nb is None:
        return str(a).strip() == str(b).strip()
    if math.isnan(na) and math.isnan(nb):
        return True
    return abs(na - nb) <= rel * max(abs(na), abs(nb)) + abs_


def row_close(ga: list[Any], aa: list[Any], key_idx: list[int], val_idx: list[int],
              rel: float = 5e-3) -> bool:
    """单行比对：key 列精确、value 列容差。"""
    for i in key_idx:
        if str(ga[i]).strip() != str(aa[i]).strip():
            return False
    for i in val_idx:
        if not close(ga[i], aa[i], rel):
            return False
    return True


def match_table(gt: list[list[Any]], ans: list[list[Any]], key_idx: list[int],
                val_idx: list[int], rel: float = 5e-3) -> dict:
    """集合判定：行数为金标准集合（无序），逐 GT 行在 answer 中找容差匹配。

    key_idx 非空时按 key 建索引（O(n)，key 通常唯一）；key 为空（标量行）走贪心小集合。
    """
    if len(gt) != len(ans):
        return {"ok": False, "reason": f"行数不一致: GT {len(gt)} vs answer {len(ans)}"}
    if not key_idx:
        unmatched = list(ans)
        for g in gt:
            hit = next((i for i, a in enumerate(unmatched) if row_close(g, a, key_idx, val_idx, rel)), None)
            if hit is None:
                return {"ok": False, "reason": f"GT 行无匹配: {g}"}
            unmatched.pop(hit)
        return {"ok": True, "reason": ""}
    # 按 key 索引（保留重复 key 的行列表）
    index: dict[tuple, list[list[Any]]] = {}
    for a in ans:
        index.setdefault(tuple(str(a[i]) for i in key_idx), []).append(a)
    for g in gt:
        k = tuple(str(g[i]) for i in key_idx)
        bucket = index.get(k)
        if not bucket:
            return {"ok": False, "reason": f"GT key 缺失: {k}"}
        hit = next((i for i, a in enumerate(bucket) if row_close(g, a, key_idx, val_idx, rel)), None)
        if hit is None:
            return {"ok": False, "reason": f"GT key {k} 值不匹配"}
        bucket.pop(hit)
    return {"ok": True, "reason": ""}



def extract_rows(raw: Any) -> list[list[Any]]:
    """把执行结果归一化为行列表（list[list]）。"""
    if raw is None:
        return []
    if isinstance(raw, list):
        rows = []
        for r in raw:
            if isinstance(r, dict):
                rows.append(list(r.values()))
            else:
                rows.append(list(r))
        return rows
    if isinstance(raw, dict):
        # ContractExecutor 的 items / rows / groups / aggregations 形态
        if "items" in raw and isinstance(raw["items"], list):
            out = []
            for it in raw["items"]:
                props = it.get("properties", {})
                out.append([props.get(k) for k in props] if props else [it.get("pk")])
            return out
        if "rows" in raw and isinstance(raw["rows"], list):
            return [list(r.values()) for r in raw["rows"] if isinstance(r, dict)]
        if "groups" in raw and isinstance(raw["groups"], list):
            return [list(g["group"].values()) + [a["value"] for a in g.get("aggregations", [])]
                    for g in raw["groups"]]
        if "aggregations" in raw and isinstance(raw["aggregations"], list):
            return [[a["value"]] for a in raw["aggregations"]]
    return []


def extract_scalar(raw: Any) -> float | None:
    rows = extract_rows(raw)
    if not rows:
        return None
    flat = [v for r in rows for v in r]
    nums = [v for v in flat if _num(v) is not None]
    return _num(nums[0]) if nums else None


def extract_codes(raw: Any) -> list[tuple[str, str, str]]:
    """L3 codes 形态：GT/A 为 (matnr, code_space, value) 行；B 为 items[].codes 数组。"""
    out: list[tuple[str, str, str]] = []
    if isinstance(raw, list):
        for r in raw:
            if isinstance(r, dict) and "codes" in r:  # B 形态 items
                matnr = r.get("pk") or (r.get("properties") or {}).get("matnr")
                for c in r.get("codes", []):
                    out.append((str(matnr), str(c.get("code_space")), str(c.get("value"))))
            elif isinstance(r, dict):
                vals = list(r.values())
                if len(vals) >= 3:
                    out.append((str(vals[0]), str(vals[1]), str(vals[2])))
            elif isinstance(r, (list, tuple)) and len(r) >= 3:
                out.append((str(r[0]), str(r[1]), str(r[2])))
        return out
    if isinstance(raw, dict) and "items" in raw:
        return extract_codes(raw["items"])
    return out
