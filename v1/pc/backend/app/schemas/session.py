"""会话配置与状态模型。"""

from enum import StrEnum

from pydantic import BaseModel, Field


class SessionState(StrEnum):
    """会话状态机,见 docs/architecture.md 第 7 节。"""

    DISCONNECTED = "disconnected"
    PAIRING = "pairing"
    READY = "ready"
    STREAMING = "streaming"
    STOPPING = "stopping"
    DEGRADED = "degraded"
    FAILED = "failed"


class VideoConfig(BaseModel):
    """采集端视频参数;全部值由服务器校验,前端不得自定上限。"""

    width: int = Field(default=640, ge=160, le=1280)
    height: int = Field(default=360, ge=120, le=720)
    fps: int = Field(default=3, ge=1, le=15)
    format: str = Field(default="jpeg", pattern="^(jpeg|webp)$")


class AudioConfig(BaseModel):
    """采集端音频参数;v1 只支持 16 kHz 单声道 PCM16LE。"""

    sample_rate: int = Field(default=16000, ge=8000, le=48000)
    channels: int = Field(default=1, ge=1, le=1)
    format: str = Field(default="pcm_s16le", pattern="^pcm_s16le$")


class SessionConfig(BaseModel):
    """POST /api/v1/sessions 请求体与 stream.configure 消息的公共部分。"""

    video: VideoConfig = Field(default_factory=VideoConfig)
    audio: AudioConfig = Field(default_factory=AudioConfig)
    models: list[str] = Field(default_factory=list)
