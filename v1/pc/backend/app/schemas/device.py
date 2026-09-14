"""设备状态模型(device.status 消息体与 GET /api/v1/device/status 响应)。"""

from enum import StrEnum

from pydantic import BaseModel, Field


class ModelHealth(StrEnum):
    """单模型健康度;前端不得从缺失消息推断状态。"""

    NOT_LOADED = "not_loaded"
    LOADING = "loading"
    READY = "ready"
    ERROR = "error"


class ResourceUsage(BaseModel):
    """瞬时资源占用;百分比为 0–100。"""

    cpu_percent: float = Field(ge=0.0, le=100.0)
    memory_percent: float = Field(ge=0.0, le=100.0)
    memory_used_mb: float = Field(ge=0.0)
    temperature_c: float | None = None
    disk_free_mb: float = Field(ge=0.0)


class DeviceStatus(BaseModel):
    """设备、模型与网络指标快照。"""

    platform: str = Field(min_length=1)  # 如 "pc" / "rk3568"
    uptime_s: float = Field(ge=0.0)
    resources: ResourceUsage
    models: dict[str, ModelHealth] = Field(default_factory=dict)
    network_rtt_ms: float | None = Field(default=None, ge=0.0)
    dropped_frames: int = Field(default=0, ge=0)
