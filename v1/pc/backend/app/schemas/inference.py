"""推理结果与模型状态模型。

bbox 一律使用 0–1 归一化坐标;源像素坐标只允许存在于 adapter 内部,
见 docs/api-contract.md 第 4 节。
"""

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import PROTOCOL_VERSION


class Detection(BaseModel):
    """单个检测目标;bbox_norm 为 [x1, y1, x2, y2],0–1 归一化。"""

    class_id: int = Field(ge=0)
    class_name: str = Field(min_length=1)
    bbox_norm: tuple[float, float, float, float]
    confidence: float = Field(ge=0.0, le=1.0)
    track_id: int | None = None

    @field_validator("bbox_norm")
    @classmethod
    def bbox_in_unit_square(cls, v: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
        x1, y1, x2, y2 = v
        if not (0.0 <= x1 <= 1.0 and 0.0 <= y1 <= 1.0 and 0.0 <= x2 <= 1.0 and 0.0 <= y2 <= 1.0):
            raise ValueError("bbox_norm values must be within [0, 1]")
        if x2 <= x1 or y2 <= y1:
            raise ValueError("bbox_norm requires x2 > x1 and y2 > y1")
        return v


class InferenceResult(BaseModel):
    """与输入 seq 对齐的单帧推理结果(inference.result 消息体)。"""

    protocol_version: int = Field(ge=1, le=PROTOCOL_VERSION)
    session_id: str
    seq: int = Field(ge=0)
    capture_ts_ms: int = Field(ge=0)
    server_ts_ms: int = Field(ge=0)
    infer_ms: float = Field(ge=0.0)
    detections: list[Detection] = Field(default_factory=list)
    fight: dict | None = None  # {"prob": float, "active": bool}
    audio_events: list[dict] = Field(default_factory=list)
    faces: list[dict] = Field(default_factory=list)
    stats: dict = Field(default_factory=dict)  # queue_depth / dropped_frames


class ModelStatus(BaseModel):
    """adapter 启动时上报的模型加载状态;加载失败必须显性化。"""

    name: str = Field(min_length=1)
    loaded: bool
    load_ms: float | None = Field(default=None, ge=0.0)
    error: str | None = None
