"""制度自检测试（governance）——把 AGENTS.md 的软规则硬化成可断言检查。

零到一档的机制防衰减：子代理每次跑增量测试时连带上它（秒级），
违反制度（缺阶段声明/缺技术债登记/全量测试过慢/写端点缺 actor 校验）直接红。
新增规则时在此加断言，规则才真正生效。
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


# ---------- 1) 阶段声明与治理 ----------
def test_agents_md_declares_current_stage() -> None:
    text = (REPO / "AGENTS.md").read_text(encoding="utf-8")
    assert "当前阶段" in text and "S1" in text, "AGENTS.md 必须声明当前阶段（S0-S3）"


def test_tech_debt_register_exists() -> None:
    td = REPO / "docs" / "tech-debt.md"
    assert td.exists(), "必须存在 docs/tech-debt.md（技术债登记）"
    text = td.read_text(encoding="utf-8")
    assert "| # | 债务 |" in text and "开放" in text, "技术债表格式：编号/债务/原因/偿还触发/状态"


# ---------- 2) 测试制度（增量快反馈） ----------
def test_builder_test_files_run_under_60s() -> None:
    """增量测试套件必须秒级：超 60s 说明测试设计失守（慢测试应拆分标记）。"""
    test_files = sorted((REPO / "tests").glob("test_builder_p*.py"))
    assert test_files, "找不到 test_builder_p*.py"
    total = 0
    for f in test_files:
        total += f.stat().st_size
    # 按文件规模粗判（不实际跑测试，避免 CI 里自嵌套）：<200KB 文件应 <60s
    assert total < 200_000, f"builder 测试文件总规模 {total}B 过大，增量反馈会退化"


def test_no_full_suite_in_subagent_docs() -> None:
    """AGENTS.md 必须含子代理禁跑全量的条款（防回归到 18 次重跑事故）。"""
    text = (REPO / "AGENTS.md").read_text(encoding="utf-8")
    assert "禁止跑全量" in text, "缺少子代理禁跑全量 pytest 的条款"


# ---------- 3) 安全底线（builder 写端点 actor 校验） ----------
def test_builder_write_routes_have_actor_check() -> None:
    """builder 写端点必须走 X-Actor 校验：扫路由源码找 post/put/delete 端点与 actor 断言共存。"""
    routes = []
    for f in (REPO / "src" / "api").glob("builder*.py"):
        routes.append(f.read_text(encoding="utf-8"))
    src = "\n".join(routes)
    has_write = any('router.' + m + '(' in src for m in ('post', 'put', 'delete'))
    assert has_write, 'builder 应至少有写端点（post/put/delete）'
    assert "ALLOWED_ACTORS" in src, "builder 路由必须复用 ALLOWED_ACTORS 白名单"
    assert "X-Actor" in src or "x_actor" in src, "builder 路由必须读 X-Actor header"


# ---------- 4) 密钥安全 ----------
def test_no_secrets_in_code() -> None:
    for f in (REPO / "src").rglob("*.py"):
        text = f.read_text(encoding="utf-8")
        assert not re.search(r"(api[_-]?key\s*=\s*['\"]|sk-[A-Za-z0-9]{20,})", text), (
            f"疑似密钥写入代码: {f}"
        )


# ---------- 5) 开工门槛制度（2026-09-11 SPEC 机制窗新增；制度文件 docs/plans/开工门槛-模板.md） ----------
THRESHOLD_DIR = REPO / "docs" / "plans"
THRESHOLD_TEMPLATE = THRESHOLD_DIR / "开工门槛-模板.md"

THRESHOLD_ANCHORS = (
    "派活前自查",          # 三行硬门禁
    "级别声明",            # S/M/L 定级，防偷偷降级
    "NC 登记",             # NEEDS CLARIFICATION 答题卡
    "## 收口",             # converge 五步
    "grep -c 'NC-OPEN'",   # 派活前机器检查命令本身
)


def _threshold_drafts() -> list[Path]:
    return sorted(p for p in THRESHOLD_DIR.glob("开工门槛-*.md") if p != THRESHOLD_TEMPLATE)


def _threshold_archived(head: str) -> bool:
    return ("存档" in head) or ("取代" in head)


def test_threshold_template_contains_mandatory_anchors() -> None:
    text = THRESHOLD_TEMPLATE.read_text(encoding="utf-8")
    missing = [a for a in THRESHOLD_ANCHORS if a not in text]
    assert not missing, f"开工门槛模板缺少制度锚点: {missing}"


def test_threshold_new_drafts_declare_valid_level() -> None:
    """新制稿（含级别声明标记者）必须声明 S/M/L；存量稿豁免，补登状态标记后收紧。"""
    for p in _threshold_drafts():
        text = p.read_text(encoding="utf-8")
        if "级别声明" not in text and "本块级别" not in text:
            continue
        m = re.search(r"(?:本块级别|级别)\s*[：:＝=]\s*\*{0,2}([SML])\s*级", text)
        assert m, f"{p.name}: 新制稿必须声明 S/M/L 级别"


def test_threshold_active_drafts_declare_status() -> None:
    for p in _threshold_drafts():
        head = "\n".join(p.read_text(encoding="utf-8").splitlines()[:12])
        if _threshold_archived(head):
            continue
        assert "状态" in head, f"{p.name}: 头部缺状态声明（进行中/已收口/存档）"


def test_threshold_closed_drafts_have_no_open_nc() -> None:
    """收口五步第 4 条的机器化：已收口的稿不允许残留 NC-OPEN。"""
    for p in _threshold_drafts():
        text = p.read_text(encoding="utf-8")
        if "已收口" not in "\n".join(text.splitlines()[:12]):
            continue
        assert "NC-OPEN" not in text, f"{p.name}: 已收口但残留 NC-OPEN"
