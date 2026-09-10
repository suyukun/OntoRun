"""CLI 查询入口：.venv/bin/python -m src.fortune_semantic.query '<json>'。

成功：打印 SQL + 结果（JSON）；失败：stderr 打印结构化错误 JSON，退出码 2。
"""

import json
import sys
from typing import Any

from src.fortune_semantic.compiler import parse_request, run_query
from src.fortune_semantic.registry import SemanticError

USAGE = (
    "用法: .venv/bin/python -m src.fortune_semantic.query "
    '\'{"measure": "reg_user_cnt", "dimensions": ["channel_l2", '
    '"time_grain=month"], "time_from": "2026-07-01", '
    '"time_to": "2026-08-31"}\''
)


def _emit(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else list(argv)
    if len(args) != 1:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        raw = json.loads(args[0])
    except json.JSONDecodeError as exc:
        print(
            _emit(
                {"error": {"code": "INVALID_JSON", "message": str(exc), "details": {}}}
            ),
            file=sys.stderr,
        )
        return 2
    try:
        result = run_query(parse_request(raw))
    except SemanticError as exc:
        print(_emit(exc.to_dict()), file=sys.stderr)
        return 2
    print("=== SQL ===")
    print(result["sql"])
    print("=== ROWS ===")
    print(_emit({"columns": result["columns"], "rows": result["rows"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
