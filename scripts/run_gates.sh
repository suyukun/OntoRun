#!/usr/bin/env bash
# OntoRun 轻 CI 门（本地增量门禁，AGENTS.md「P6 收口后建轻 CI」）。
#
# 职责（三件事，秒级~分钟级）：
#   1) ruff check src/ tests/          —— lint 门（增量开发必须全绿）
#   2) pytest tests/test_governance.py —— 制度自检测（AGENTS.md 软规则硬化，
#        阶段声明/技术债登记/测试制度/安全底线，违反直接红）
#   3) 提示全量门禁归属（见下）
#
# 全量 pytest / vitest 是【阶段末 Rose 门禁】，子代理与日常增量不跑：
#   - 后端全量：python -m pytest tests/ -q   （阶段末 Rose 跑一次，不进子代理循环）
#   - 前端全量：cd web && npm run test       （vitest）
# 本脚本不做全量，只做日常可安全重复的门。
#
# 用法：bash scripts/run_gates.sh
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> [gate 1/2] ruff check src/ tests/"
ruff check src/ tests/

echo "==> [gate 2/2] governance 制度自检（pytest tests/test_governance.py -q）"
python -m pytest tests/test_governance.py -q

echo "==> gate 通过（lint + governance 全绿）"
echo "    全量门禁（pytest tests/ 全量 + vitest）属阶段末 Rose 门禁，本脚本不触发，"
echo "    见 AGENTS.md「测试」与 docs/tech-debt.md。"
