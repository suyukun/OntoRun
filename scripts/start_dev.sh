#!/usr/bin/env bash
# OntoRun 一键起（C 档 #7，S2 P5 收口）：后端 :8000 + 前端 :5173。
#
# - 读 DEEPSEEK_API_KEY：优先环境变量，其次 .env，最后 ~/.dsh/.credentials.yaml；
# - 后端 uvicorn src.app.main:app --reload（:8000）；前端 web vite（:5173）；
# - 日志落 .dev-backend.log / .dev-frontend.log；Ctrl-C 或 kill 脚本即停。
#
# 用法：bash scripts/start_dev.sh
set -euo pipefail
cd "$(dirname "$0")/.."

# ---- DEEPSEEK_API_KEY 解析（环境 > .env > credentials）----
if [[ -z "${DEEPSEEK_API_KEY:-}" ]]; then
  if [[ -f .env ]]; then
    set -a; source .env; set +a
  fi
fi
if [[ -z "${DEEPSEEK_API_KEY:-}" && -f ~/.dsh/.credentials.yaml ]]; then
  DEEPSEEK_API_KEY="$(awk '/DEEPSEEK_API_KEY:/{print $2}' ~/.dsh/.credentials.yaml | tr -d '\r')"
  export DEEPSEEK_API_KEY
fi
if [[ -z "${DEEPSEEK_API_KEY:-}" ]]; then
  echo "缺少 DEEPSEEK_API_KEY（检查 .env 或 ~/.dsh/.credentials.yaml）" >&2
  exit 1
fi
echo "==> DEEPSEEK_API_KEY 已就绪"

# ---- 后端 ----
echo "==> 启动后端 uvicorn :8000"
nohup uvicorn src.app.main:app --reload --port 8000 > .dev-backend.log 2>&1 &
BACKEND_PID=$!
echo "    后端 PID=$BACKEND_PID 日志=.dev-backend.log"

# ---- 前端 ----
echo "==> 启动前端 vite :5173"
(cd web && nohup npm run dev > ../.dev-frontend.log 2>&1 & echo $! > /tmp/ontorun_frontend.pid)
FRONTEND_PID="$(cat /tmp/ontorun_frontend.pid)"
echo "    前端 PID=$FRONTEND_PID 日志=.dev-frontend.log"

echo
echo "OntoRun 已启动："
echo "  后端  http://localhost:8000  （语义接口 + 本体元数据）"
echo "  前端  http://localhost:5173  （本体驱动 UI）"
echo "停止：kill $BACKEND_PID $FRONTEND_PID（或 Ctrl-C 中断本脚本——后台进程需手动 kill）"
echo
trap 'echo "停止 OntoRun 后台进程..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true' EXIT
echo "按 Ctrl-C 停止并退出..."
wait $BACKEND_PID
