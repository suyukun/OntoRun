"""DES 生成器 CLI 入口（设计 §5 目录/存储，对外 argparse 接口）。

用法示例：
    python -m src.des --enterprise hc_precision                          # 全量 100 万行
    python -m src.des --enterprise hc_precision --seed 20260821 --out /tmp/des_out
    python -m src.des --scale 0.003 --out /tmp/des_small                 # 小规模 ~3000 行快速验证
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from .generate import build_enterprise


def main(argv: Sequence[str] | None = None) -> None:
    """argparse 入口：--enterprise/--seed/--scale/--out（默认输出企业目录）。

    --scale：行数缩放系数（如 0.003 → 总行数 ~3000，常规测试小规模快速跑；None 全量 100 万行）。
    """
    parser = argparse.ArgumentParser(description="DES 确定性企业数据生成器（S2 P1b：9 主数据 + 9 事务表；--scale 缩放行数，None=全量 100 万行）")
    parser.add_argument("--enterprise", default="hc_precision", help="企业编码（目录名），默认 hc_precision")
    parser.add_argument("--seed", type=int, default=None, help="覆盖企业配置中的生成 seed")
    parser.add_argument("--scale", type=float, default=None, help="行数缩放系数（如 0.003 → 总行数 ~3000；默认 None 全量 100 万行）")
    parser.add_argument("--out", default=None, help="输出目录（默认 <data/des/enterprises>/<enterprise>）")
    args = parser.parse_args(argv)
    result = build_enterprise(args.enterprise, out_dir=args.out, seed=args.seed, scale=args.scale)
    tables = ", ".join(f"{tid}={n}" for tid, n in result["tables"].items())
    print(f"已生成企业数据: {result['enterprise']}（seed={result['seed']}，合计 {result['total_rows']} 行，注入 {result['injected']} 行）")
    print(f"表行数: {tables}")
    print(f"输出目录: {result['out']}")


if __name__ == "__main__":
    main()
