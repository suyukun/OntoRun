"""本体管理台独立入口：uvicorn src.fortune_admin.main:app --port 8010"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.fortune_admin.router import router

app = FastAPI(title="OntoRun 本体管理台 API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本地开发台，前后端分离 dev 用
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8010)
