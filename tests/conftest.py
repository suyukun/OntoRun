"""pytest 全局配置：将项目根目录加入 sys.path（src/data 均为顶层包）。"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)
