"""Mobile Monitor API v1 入口。

单元 1.1 只提供 /healthz;会话、鉴权与 WebSocket 属后续单元,
不得提前实现。
"""

from fastapi import FastAPI

from app.schemas import PROTOCOL_VERSION

app = FastAPI(
    title="Mobile Monitor API",
    version="0.1.0",
    docs_url="/docs",
)


@app.get("/healthz")
def healthz() -> dict:
    """进程健康检查;不暴露敏感信息(路径、模型、密钥等)。"""
    return {
        "status": "ok",
        "protocol_version": PROTOCOL_VERSION,
    }
