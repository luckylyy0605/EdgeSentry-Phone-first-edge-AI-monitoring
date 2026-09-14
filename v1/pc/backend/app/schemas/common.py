"""协议公共常量与错误模型。"""

from enum import IntEnum

from pydantic import BaseModel, Field

# 所有 JSON 消息携带的协议版本;不兼容变更时递增。
PROTOCOL_VERSION = 1


class ErrorCode(IntEnum):
    """结构化错误码,前端据此显示失败原因,禁止静默失败。"""

    PROTOCOL_MISMATCH = 1  # protocol_version 不支持
    SESSION_NOT_FOUND = 2
    SESSION_STATE_INVALID = 3
    RATE_LIMIT = 4  # 帧率/尺寸/速率超限
    PAYLOAD_TOO_LARGE = 5
    ADAPTER_ERROR = 6  # 推理 adapter 显性失败
    ADAPTER_UNAVAILABLE = 7
    INTERNAL = 8


class ErrorInfo(BaseModel):
    """统一错误体;error 消息与 HTTP 错误响应共用。"""

    code: ErrorCode
    message: str = Field(min_length=1)
    session_id: str | None = None
    detail: dict | None = None
