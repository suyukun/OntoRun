#!/usr/bin/env bash
# Six-state curl smoke for the T1 semantic service (reusable acceptance probe).
# Usage: scripts/semantic_smoke.sh
#   - starts its own uvicorn on :8901 unless one is already serving there
#   - one question per state: hot / cold_pushdown / cold_adhoc / rejected /
#     ask_param(missing_param) / reject_range(out_of_range)
#   - PASS = final frame path/state/block_reason match (+ REQ- id present)
set -u
cd "$(dirname "$0")/.."

PY="${PYTHON:-/opt/anaconda3/bin/python3}"
PORT="${SEMANTIC_SMOKE_PORT:-8901}"
BASE="http://127.0.0.1:$PORT"
SRV=""
started_here=0

if ! curl -sf "$BASE/api/profile" >/dev/null 2>&1; then
  $PY -m uvicorn src.semantic.app:app --port "$PORT" --log-level warning >/tmp/semantic_smoke_uvicorn.log 2>&1 &
  SRV=$!
  started_here=1
  for _ in $(seq 1 40); do
    curl -sf "$BASE/api/profile" >/dev/null 2>&1 && break
    sleep 0.5
  done
fi
trap '[ "$started_here" = 1 ] && kill "$SRV" 2>/dev/null' EXIT

if ! curl -sf "$BASE/api/profile" >/dev/null 2>&1; then
  echo "FAIL: service not reachable at $BASE (see /tmp/semantic_smoke_uvicorn.log)"
  exit 1
fi

extract_final() {  # stdin: SSE frames -> "path<TAB>state<TAB>block_reason<TAB>request_id"
  $PY -c '
import json, sys
final = None
for line in sys.stdin:
    line = line.strip()
    if not line.startswith("data: "):
        continue
    ev = json.loads(line[6:])
    if ev.get("kind") == "final":
        final = ev["result"]
    elif ev.get("kind") == "error":
        final = {"path": "error", "state": "error", "block_reason": None, "request_id": ev.get("code")}
if final is None:
    print("MISSING\tNO_FINAL\t\t-")
else:
    print("\t".join([str(final.get("path")), str(final.get("state")),
                     str(final.get("block_reason")), str(final.get("request_id"))]))
'
}

pass=0
fail=0

run_case() {  # name question expected_path expected_state expected_block_reason
  local name="$1" question="$2" epath="$3" estate="$4" eblock="$5"
  local crid body final gpath gstate gbr grid ok=1 note=""
  crid="SMOKE-$$-$name-$(date +%s)"
  body=$(printf '{"question":"%s","client_request_id":"%s"}' "$question" "$crid")
  final=$(curl -sN --max-time 90 -X POST "$BASE/api/chat" \
    -H 'Content-Type: application/json' -d "$body" | extract_final)
  gpath=$(printf '%s' "$final" | cut -f1)
  gstate=$(printf '%s' "$final" | cut -f2)
  gbr=$(printf '%s' "$final" | cut -f3)
  grid=$(printf '%s' "$final" | cut -f4)

  [ "$gpath" = "$epath" ] || ok=0
  [ "$gbr" = "$eblock" ] || ok=0
  case "$gstate" in
    "$estate") ;;
    success_warning) # LLM route fell back to keywords: degraded but still correct
      if [ "$estate" = "success" ]; then note=" (degraded: keyword route)"; else ok=0; fi ;;
    *) ok=0 ;;
  esac
  case "$grid" in REQ-*) ;; *) ok=0 ;; esac

  if [ "$ok" = 1 ]; then
    echo "PASS [$name]$note path=$gpath state=$gstate block=$gbr id=$grid"
    pass=$((pass + 1))
  else
    echo "FAIL [$name] got=[$gpath|$gstate|$gbr|$grid] want=[$epath|$estate|$eblock|REQ-*]"
    fail=$((fail + 1))
  fi
}

run_case hot           "2026年8月注册用户数是多少？"   hot           success       None
run_case cold_pushdown "2026年8月分渠道注册用户数"     cold_pushdown success       None
run_case cold_adhoc    "2026年8月注册用户男女比例"     cold_adhoc    success       None
run_case scope         "抽奖活动效果怎么样？"          rejected      reject_scope  None
run_case ask_param     "注册用户数是多少？"            blocked_param ask_param     missing_param
run_case range         "2026年10月注册用户数是多少？"  blocked_param reject_range  out_of_range

echo "----"
echo "smoke: $pass passed, $fail failed"
[ "$fail" = 0 ]
