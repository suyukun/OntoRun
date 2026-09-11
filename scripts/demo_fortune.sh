#!/usr/bin/env bash
# 财富广场演示一键启动/停止：前台 ChatBI(:8000) + 后台API(:8010) + 后台前端(:5174)
# 用法: ./scripts/demo_fortune.sh start|stop|status
set -u
cd "$(dirname "$0")/.."
VENV=.venv/bin
LOGDIR=/tmp/fortune-demo
mkdir -p "$LOGDIR"

start() {
  echo "== 1/3 前台语义服务 :8000 =="
  nohup /opt/anaconda3/bin/python -m uvicorn src.app.main:app --port 8000 >"$LOGDIR/app.log" 2>&1 &
  echo "  log=$LOGDIR/app.log"
  echo "== 2/3 后台管理台 API :8010 =="
  nohup /opt/anaconda3/bin/python -m uvicorn src.fortune_admin.main:app --port 8010 >"$LOGDIR/admin.log" 2>&1 &
  echo "  log=$LOGDIR/admin.log"
  echo "== 3/4 前台 ChatBI 壳 :5173 =="
  (cd chatbi && nohup npm run dev -- --port 5173 >"$LOGDIR/chatbi.log" 2>&1 &)
  echo "  log=$LOGDIR/chatbi.log"
  echo "== 4/4 后台管理台前端 :5174 =="
  (cd ontology-admin && nohup npm run dev -- --port 5174 >"$LOGDIR/admin-fe.log" 2>&1 &)
  echo "  log=$LOGDIR/admin-fe.log"
  sleep 5
  status
}

stop() {
  pkill -f "uvicorn src.app.main:app" 2>/dev/null && echo "前台已停" || echo "前台未在跑"
  pkill -f "uvicorn src.fortune_admin.main:app" 2>/dev/null && echo "后台API已停" || echo "后台API未在跑"
  pkill -f "vite" 2>/dev/null && echo "后台前端已停" || echo "后台前端未在跑"
}

status() {
  echo "== 服务状态 =="
  curl -s -o /dev/null -w "前台 API :8000 -> %{http_code}\n" http://localhost:8000/docs || echo "前台 down"
  curl -s -o /dev/null -w "前台 ChatBI :5173 -> %{http_code}\n" http://localhost:5173/ || echo "前台壳 down"
  curl -s -o /dev/null -w "后台 API :8010 -> %{http_code}\n" http://localhost:8010/api/ontology || echo "后台API down"
  curl -s -o /dev/null -w "后台前端 :5174 -> %{http_code}\n" http://localhost:5174/ || echo "后台前端 down"
  "$VENV/python" -c "import duckdb; con=duckdb.connect('data/fortune_mirror.duckdb', read_only=True); print('镜像库注册明细:', con.execute('SELECT count(*) FROM cdm.dwd_cu_rgst_fin_di').fetchone()[0], '行')" 2>/dev/null || echo "镜像库: 不可读"
}

case "${1:-}" in
  start) start ;;
  stop) stop ;;
  status) status ;;
  *) echo "用法: $0 start|stop|status" ;;
esac
