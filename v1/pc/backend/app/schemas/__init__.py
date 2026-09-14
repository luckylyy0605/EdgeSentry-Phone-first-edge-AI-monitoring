"""Mobile Monitor 统一协议 schema 包。

所有跨端 JSON 消息的 Pydantic 模型集中在此;
前端 TypeScript 类型见 frontend/src/protocol/types.ts,两者必须保持一致。
"""

from app.schemas.common import ErrorCode, ErrorInfo, PROTOCOL_VERSION
from app.schemas.session import SessionConfig, SessionState
from app.schemas.inference import Detection, InferenceResult, ModelStatus
from app.schemas.device import DeviceStatus, ModelHealth, ResourceUsage

__all__ = [
    "PROTOCOL_VERSION",
    "ErrorCode",
    "ErrorInfo",
    "SessionConfig",
    "SessionState",
    "Detection",
    "InferenceResult",
    "ModelStatus",
    "DeviceStatus",
    "ModelHealth",
    "ResourceUsage",
]
