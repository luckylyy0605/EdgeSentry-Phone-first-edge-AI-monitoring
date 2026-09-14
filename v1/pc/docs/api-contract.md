# v1 API 与推理协议

## 1. 版本原则

- HTTP 前缀：`/api/v1`
- WebSocket 子协议：`mobile-monitor.v1`
- 所有 JSON 消息包含 `protocol_version: 1`。
- 手机只接触 Mobile Monitor API；不能直接调用 `v6demo` CLI。

## 2. REST API

| 方法 | 路径 | 用途 |
|---|---|---|
| GET | `/healthz` | 进程健康，不暴露敏感信息 |
| POST | `/api/v1/pair` | 用一次性 pairing code 换短期 token |
| POST | `/api/v1/sessions` | 创建采集/推理会话 |
| GET | `/api/v1/sessions/{id}` | 会话状态与统计 |
| POST | `/api/v1/sessions/{id}/stop` | 幂等停止会话 |
| GET | `/api/v1/sessions/{id}/events` | 分页读取事件时间线 |
| GET | `/api/v1/device/status` | 设备、模型、存储和温度状态 |

## 3. WebSocket

路径：`/ws/v1/sessions/{session_id}`。鉴权使用短期 token；token 不写入日志。

### 文本消息

客户端控制示例：

```json
{
  "protocol_version": 1,
  "type": "stream.configure",
  "session_id": "01J...",
  "video": {"width": 640, "height": 360, "fps": 3, "format": "jpeg"},
  "audio": {"sample_rate": 16000, "channels": 1, "format": "pcm_s16le"}
}
```

服务端推理结果示例：

```json
{
  "protocol_version": 1,
  "type": "inference.result",
  "session_id": "01J...",
  "seq": 184,
  "capture_ts_ms": 1789372800123,
  "server_ts_ms": 1789372800218,
  "infer_ms": 63.4,
  "detections": [
    {
      "class_id": 0,
      "class_name": "person",
      "bbox_norm": [0.15, 0.12, 0.48, 0.92],
      "confidence": 0.91,
      "track_id": 2
    }
  ],
  "fight": {"prob": 0.18, "active": false},
  "audio_events": [],
  "faces": [],
  "stats": {"queue_depth": 0, "dropped_frames": 7}
}
```

服务端必须显式发送 `session.state`、`device.status`、`event.created` 和 `error` 消息；前端不得从缺失消息推断成功。

### 二进制媒体包

为避免 Base64 开销，二进制包使用固定头：

| 字节 | 字段 | 类型 |
|---:|---|---|
| 0 | kind：`0x01` JPEG/WebP frame，`0x02` PCM16LE audio | uint8 |
| 1–8 | seq | uint64 big-endian |
| 9–16 | capture_ts_ms | uint64 big-endian |
| 17–末尾 | payload | bytes |

服务端限制单帧尺寸、帧率和音频速率；超限返回结构化错误并可关闭连接。

## 4. InferenceAdapter

后端只依赖下列语义接口：

```python
class InferenceAdapter(Protocol):
    async def start(self, config: SessionConfig) -> ModelStatus: ...
    async def infer_frame(self, frame: VideoFrame) -> InferenceResult: ...
    async def push_audio(self, chunk: AudioChunk) -> list[AudioEvent]: ...
    async def stop(self) -> None: ...
    async def health(self) -> AdapterHealth: ...
```

约束：

- `start()` 只在会话启动或 worker 恢复时加载模型，不能每帧加载。
- `infer_frame()` 不负责网络、鉴权、持久化或重试策略。
- adapter 输出必须转换为统一 schema；`v6demo` 的像素 bbox 在 adapter 内按输入宽高归一化。
- 相同 `session_id + seq` 的结果应幂等；实时帧超时后不重试。

## 5. `v6demo` 兼容层

### 离线兼容

`V6CliJobAdapter` 仅用于用户上传完整视频后的异步分析：受控参数调用 `run_pipeline.sh`，读取 NDJSON/timing/chain 产物。它不承担实时视频。

### 实时推荐

在 `v6demo` 一侧增加常驻 `v6_worker`，模型加载一次，通过 Unix domain socket 接收帧并返回一行一个 JSON 的结果。`Mobile_Monitor` 中的 `V6WorkerAdapter` 只负责：

1. worker 生命周期与健康检查；
2. 有界队列和超时；
3. v6 像素坐标到统一 schema 的转换；
4. 将 worker 错误原样显性化。

这是一条版本化依赖边界。若完全不改 `v6demo`，只能用短视频分段反复调用 CLI，延迟和资源开销不适合实时监控。

## 6. 会话产物

```text
output/<YYYYMMDD_HHMMSS>_<platform>_<session_id>/
├── session.json
├── events.ndjson
├── device.ndjson
├── snapshots/
├── audio/                 # 启用录音时
└── evidence/              # 后续接入 v6 哈希链
```

原始连续视频默认不保存；开启保存必须由 UI 明示并受保留策略控制。

