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
