"""schema 行为契约测试:校验规则与双端解析一致性。"""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.schemas import (
    DeviceStatus,
    Detection,
    ErrorCode,
    ErrorInfo,
    InferenceResult,
    ModelHealth,
    ModelStatus,
    PROTOCOL_VERSION,
    ResourceUsage,
    SessionConfig,
    SessionState,
)

EXAMPLES_DIR = Path(__file__).resolve().parents[2] / "configs" / "schema-examples"

BASE_RESULT = {
    "protocol_version": PROTOCOL_VERSION,
    "session_id": "01JTEST",
    "seq": 184,
    "capture_ts_ms": 1789372800123,
    "server_ts_ms": 1789372800218,
    "infer_ms": 63.4,
}


class TestSessionConfig:
    def test_defaults_match_contract(self) -> None:
        cfg = SessionConfig()
        assert cfg.video.width == 640
        assert cfg.video.height == 360
        assert cfg.video.fps == 3
        assert cfg.video.format == "jpeg"
        assert cfg.audio.sample_rate == 16000
        assert cfg.audio.channels == 1
        assert cfg.audio.format == "pcm_s16le"

    def test_rejects_out_of_range_video(self) -> None:
        with pytest.raises(ValidationError):
            SessionConfig(video={"width": 1920, "height": 1080, "fps": 30, "format": "jpeg"})

    def test_rejects_unsupported_format(self) -> None:
        with pytest.raises(ValidationError):
            SessionConfig(video={"format": "h264"})

    def test_json_roundtrip(self) -> None:
        cfg = SessionConfig()
        assert SessionConfig.model_validate_json(cfg.model_dump_json()) == cfg


class TestDetection:
    def test_accepts_normalized_bbox(self) -> None:
        det = Detection(class_id=0, class_name="person", bbox_norm=(0.15, 0.12, 0.48, 0.92), confidence=0.91)
        assert det.track_id is None

    def test_rejects_pixel_bbox(self) -> None:
        """像素坐标必须被拒绝,防止 v6 像素值漏进统一协议。"""
        with pytest.raises(ValidationError):
            Detection(class_id=0, class_name="person", bbox_norm=(30.0, 25.0, 150.0, 400.0), confidence=0.9)

    def test_rejects_inverted_bbox(self) -> None:
        with pytest.raises(ValidationError):
            Detection(class_id=0, class_name="person", bbox_norm=(0.5, 0.1, 0.4, 0.9), confidence=0.9)


class TestInferenceResult:
    def test_accepts_api_contract_example(self) -> None:
        """api-contract.md 第 3 节的示例必须可解析。"""
        result = InferenceResult(
            **BASE_RESULT,
            detections=[{
                "class_id": 0,
                "class_name": "person",
                "bbox_norm": [0.15, 0.12, 0.48, 0.92],
                "confidence": 0.91,
                "track_id": 2,
            }],
            fight={"prob": 0.18, "active": False},
            stats={"queue_depth": 0, "dropped_frames": 7},
        )
        assert result.detections[0].track_id == 2
        assert result.stats["dropped_frames"] == 7

    def test_rejects_negative_seq(self) -> None:
        with pytest.raises(ValidationError):
            InferenceResult(**{**BASE_RESULT, "seq": -1})

    def test_rejects_wrong_protocol_version(self) -> None:
        with pytest.raises(ValidationError):
            InferenceResult(**{**BASE_RESULT, "protocol_version": 99})


class TestErrorAndDevice:
    def test_error_info(self) -> None:
        err = ErrorInfo(code=ErrorCode.RATE_LIMIT, message="frame rate exceeded", session_id="01JTEST")
        assert err.code == ErrorCode.RATE_LIMIT

    def test_device_status(self) -> None:
        status = DeviceStatus(
            platform="pc",
            uptime_s=12.5,
            resources=ResourceUsage(cpu_percent=31.0, memory_percent=48.2, memory_used_mb=4096.0, disk_free_mb=10240.0),
            models={"detector": ModelHealth.READY},
            dropped_frames=3,
        )
        assert status.models["detector"] == ModelHealth.READY

    def test_resource_rejects_invalid_percent(self) -> None:
        with pytest.raises(ValidationError):
            ResourceUsage(cpu_percent=120.0, memory_percent=50.0, memory_used_mb=100.0, disk_free_mb=1.0)


class TestModelStatus:
    def test_failure_is_explicit(self) -> None:
        status = ModelStatus(name="detector", loaded=False, error="weights not found")
        assert status.loaded is False
        assert status.error is not None

    def test_success_without_error(self) -> None:
        status = ModelStatus(name="detector", loaded=True, load_ms=320.5)
        assert status.error is None


class TestSessionStateEnum:
    def test_values_match_architecture_doc(self) -> None:
        assert {s.value for s in SessionState} == {
            "disconnected", "pairing", "ready", "streaming", "stopping", "degraded", "failed",
        }


class TestSchemaExamples:
    """configs/schema-examples 的样例必须可被后端 schema 解析。"""

    def _load(self, name: str) -> dict:
        return json.loads((EXAMPLES_DIR / name).read_text(encoding="utf-8"))

    def test_stream_configure_example(self) -> None:
        msg = self._load("stream.configure.json")
        assert SessionConfig.model_validate(msg["video"] | {"audio": msg["audio"], "models": msg["models"]})

    def test_inference_result_example(self) -> None:
        msg = self._load("inference.result.json")
        result = InferenceResult.model_validate(msg)
        assert result.detections[0].bbox_norm == (0.15, 0.12, 0.48, 0.92)

    def test_error_example(self) -> None:
        msg = self._load("error.json")
        assert ErrorInfo.model_validate(msg["error"]).code == ErrorCode.RATE_LIMIT

    def test_device_status_example(self) -> None:
        msg = self._load("device.status.json")
        assert DeviceStatus.model_validate(msg["status"]).models["detector"] == ModelHealth.READY
