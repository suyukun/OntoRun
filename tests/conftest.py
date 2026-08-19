"""pytest 全局配置：将项目根目录加入 sys.path（src/data 均为顶层包）。"""

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)


def _parse_dotenv(path: Path) -> dict[str, str]:
    """手写 .env 解析（零依赖，仅支持 KEY=VALUE 行，忽略注释与空行）。"""
    env: dict[str, str] = {}
    if not path.is_file():
        return env
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            env[key] = value
    return env


@pytest.fixture(autouse=True)
def _load_dotenv_for_live_tests(request: pytest.FixtureRequest) -> None:
    """仅 live 标记的测试触发：从项目根 .env 补全缺失的环境变量。

    不覆盖已有环境变量（export 优先），mock 测试完全不受影响。
    """
    marker = request.node.get_closest_marker("live")
    if marker is None:
        return
    dotenv = _parse_dotenv(ROOT / ".env")
    for key, value in dotenv.items():
        if key not in os.environ:
            os.environ[key] = value


# ======================================================================
# TD-3 偿还（P4）：extraction MockProvider 响应 fixture 化
# ======================================================================

GOLDEN_DIR = ROOT / "tests" / "golden"


@pytest.fixture
def extraction_mock_responses() -> dict:
    """加载冻结的 MockProvider 响应场景（tests/golden/extraction_mock_responses.json）。

    LLM"说过什么"由 fixture 固定：E2E 断言对响应内容精确可控，不再内联拼 payload。
    """
    import json

    path = GOLDEN_DIR / "extraction_mock_responses.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["scenarios"]


@pytest.fixture
def make_mock_provider(extraction_mock_responses):
    """工厂 fixture：按场景名构造 MockProvider（响应内容来自 golden 文件）。"""

    import json as _json

    from src.agent.provider import ChatResponse, MockProvider

    def _make(scenario: str) -> MockProvider:
        spec = extraction_mock_responses[scenario]
        if "raw_content" in spec:
            content = spec["raw_content"]
        else:
            content = _json.dumps(spec["content_json"], ensure_ascii=False)
        return MockProvider(responses=[ChatResponse(content=content)])

    return _make
