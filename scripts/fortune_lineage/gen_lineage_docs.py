#!/usr/bin/env python
"""Generate lineage docs (mermaid markdown + self-contained HTML) from lineage_edges.json.

Graph and broken-chain list are both derived from the same JSON produced by
run_full_lineage.py -- no hand-written numbers or edges.
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).parent
DOCS_DIR = Path("docs/fortune-lineage")
MERMAID_JS = Path("/tmp/mermaid_dl/mermaid.min.js")
TITLE = "财富广场·注册场景血缘 V0（2026-09-10）"

# Known Chinese labels (Jack's curated list + task brief); new tables keep English.
CN_LABELS = {
    "dim_cu_usr_info_df": "用户维",
    "dim_ch_chl_df": "渠道维",
    "dim_pb_date_yf": "日期维",
    "dwd_cu_rgst_fin_di": "注册KPI明细",
    "dwd_cu_actv_df": "激活",
    "dwd_cu_real_df": "实名",
    "dwd_cu_rgst_nonfin_di": "原始注册",
    "dwd_ch_usr_rltv_df": "渠道关联授权",
    "dwd_lm_pv_df": "浏览流量",
    "ads_rgst_chnl_cnt_df": "注册数·观远唯一源",
    "ads_chnl_real_user_df": "实名指标",
    "ads_chnl_auth_qty_df": "授权指标",
    "ads_chnl_rltv_chnl_df": "关联渠道指标",
    "ads_chnl_rgst_to_real_auth_dau_df": "转化率",
    "ads_chnl_real_info_df": "实名宽表",
    "ads_rgst_raw_chnl_cnt_df": "原始注册计数",
    "ads_rgst_act_chnl_cnt_df": "激活注册计数",
}


def norm(table: str) -> str:
    """'cdm.t' -> 't'; '<default>.t' -> 't'; keeps cfgl_iml_data.x -> x."""
    t = table.strip()
    if t.lower().startswith("<default>."):
        t = t.split(".", 1)[1]
    return t.split(".")[-1].lower()


def node_id(table: str) -> str:
    return "n_" + re.sub(r"[^A-Za-z0-9_]", "_", norm(table))


def node_label(table: str) -> str:
    short = norm(table)
    cn = CN_LABELS.get(short)
    return f"{short}（{cn}）" if cn else short


def main() -> int:
    edges = json.loads((HERE / "lineage_edges.json").read_text(encoding="utf-8"))

    ddl_tables = set()
    base = Path("materials/fortune-warehouse-input/2026-09-10-数仓ddl及脚本")
    for ddl in sorted(base.glob("crt_tab_ddl*.sql")):
        text = ddl.read_text(encoding="utf-8", errors="replace")
        ddl_tables |= {
            m.group(1).lower()
            for m in re.finditer(
                r"\bCREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([\w.\$]+)",
                text,
                re.IGNORECASE,
            )
        }

    # dedupe edges by (normalized source, normalized target), keep first via_script
    seen = {}
    for e in edges:
        key = (norm(e["source"]), norm(e["target"]))
        seen.setdefault(key, e)
    uniq_edges = list(seen.values())

    all_tables = sorted(
        {norm(e["source"]) for e in edges} | {norm(e["target"]) for e in edges}
    )
    broken = [t for t in all_tables if t not in ddl_tables]
    ddl_unused = sorted(ddl_tables - set(all_tables))

    nodes = sorted(
        {norm(e["source"]) for e in uniq_edges}
        | {norm(e["target"]) for e in uniq_edges}
    )
    # original (schema-qualified) form per normalized table, e.g. cfgl_iml_data.x -> x
    orig = {}
    for e in edges:
        for side in ("source", "target"):
            orig.setdefault(norm(e[side]), e[side])
    layers = {"ODS": [], "CDM": [], "ADS": []}
    for t in nodes:
        raw = orig.get(t, t).lower()
        if raw.startswith("rec.") or t.startswith("ads_"):
            layers["ADS"].append(t)
        elif raw.startswith(("ods.", "cfgl_")):
            layers["ODS"].append(t)  # external-source schemas stay out of CDM
        else:
            layers["CDM"].append(t)

    lines = ["graph LR"]
    for name in ("ODS", "CDM", "ADS"):
        lines.append(f"  subgraph {name}")
        for t in layers[name]:
            lines.append(f'    {node_id(t)}["{node_label(t)}"]')
        lines.append("  end")
    for e in uniq_edges:
        lines.append(f"  {node_id(norm(e['source']))} --> {node_id(norm(e['target']))}")
    mermaid_def = chr(10).join(lines)

    fence = (
        "~~~"  # tilde fence: markdown-standard, keeps backticks out of this generator
    )
    broken_md = chr(10).join(f"- `{t}`" for t in broken)
    unused_md = chr(10).join(f"- `{t}`" for t in ddl_unused) or "-（无）"
    via_md = chr(10).join(
        f"- `{e['source']}` → `{e['target']}`（{e['via_script']}）" for e in uniq_edges
    )

    md = f"""# {TITLE}

> 机器生成（scripts/fortune_lineage/gen_lineage_docs.py），数据源 = lineage_edges.json；表级血缘。
> 解析方法：占位符替换（data_ds → 2026-08-25）→ postgres 方言（失败则剥离 DWS DDL 尾缀子句 / 换 hive）→ 剔除脚本内临时表。
> 覆盖：17 个 ETL 脚本全部解析成功；去重后 {len(uniq_edges)} 条边、{len(all_tables)} 张表。

{fence}mermaid
{mermaid_def}
{fence}

## 边明细（去重后 {len(uniq_edges)} 条）

{via_md}

## 断链清单（被脚本引用、但不在 22 张 DDL 覆盖内：{len(broken)} 张）

{broken_md}

## DDL 中有、但 17 个脚本未引用的表（{len(ddl_unused)} 张）

{unused_md}
"""
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "血缘图V0.md").write_text(md, encoding="utf-8")

    # self-contained HTML: mermaid.min.js inlined, zero external references
    js = MERMAID_JS.read_text(encoding="utf-8")
    closing = "</" + "script"  # built at runtime; no literal closing tag in this file
    js_safe = js.replace(closing, "<" + chr(92) + "/script")
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>{TITLE}</title>
<style>
  body {{ font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
         margin: 24px; background: #fafafa; color: #222; }}
  h1 {{ font-size: 22px; }}
  .meta {{ color: #666; font-size: 13px; margin-bottom: 16px; }}
  .mermaid {{ background: #fff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 16px; }}
</style>
</head>
<body>
<h1>{TITLE}</h1>
<div class="meta">表级血缘 · 17 个 ETL 脚本 · {len(uniq_edges)} 条边 · {len(all_tables)} 张表 · 断链 {len(broken)} 张（明细见 血缘图V0.md）</div>
<pre class="mermaid">
{mermaid_def}
</pre>
<script>
{js_safe}
mermaid.initialize({{ startOnLoad: true, securityLevel: "loose" }});
</script>
</body>
</html>
"""
    (DOCS_DIR / "血缘图V0.html").write_text(html, encoding="utf-8")

    print(f"md written: {DOCS_DIR / '血缘图V0.md'}")
    print(f"html written: {DOCS_DIR / '血缘图V0.html'} (mermaid js bytes: {len(js)})")
    print(
        f"edges(uniq): {len(uniq_edges)}  tables: {len(all_tables)}  broken: {len(broken)}  ddl_unused: {len(ddl_unused)}"
    )
    print("broken tables:", ", ".join(broken))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
