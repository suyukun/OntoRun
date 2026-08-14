"""语义接口 API（B3，技术方案 §4）：FastAPI 薄壳 + 统一信封 + 错误码映射。"""
from src.api.main import create_app

__all__ = ["create_app"]
