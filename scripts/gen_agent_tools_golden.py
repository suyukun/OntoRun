"""一次性生成 A2 golden 快照（tests/golden/agent_tools_golden.json）。"""

import json
import sys
from pathlib import Path

sys.path.insert(0, ".")

from src.agent.tools_generator import build_tools
from src.ontology import build_registry

tools = build_tools(build_registry())
out = json.dumps(tools, ensure_ascii=False, indent=2, sort_keys=True)
path = Path("tests/golden/agent_tools_golden.json")
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(out, encoding="utf-8")
print(f"golden written: {path} ({len(out)} bytes)")
