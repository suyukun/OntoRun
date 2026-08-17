"""波 4a 任务 1：应用装配层——挂载 API 路由 + Agent 会话端点。

- main.py：FastAPI 应用工厂（create_app），组装 runtime + agent 端点；
- session.py：MVP 内存会话管理器。
"""

from src.app.main import create_app

__all__ = ["create_app"]
