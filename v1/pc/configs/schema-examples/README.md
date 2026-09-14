# schema-examples — 双端契约样例

本目录存放统一协议 v1 的样例 JSON。每个文件必须同时满足:

1. 后端 Pydantic 校验通过(`backend/tests`);
2. 前端 TypeScript 类型(`frontend/src/protocol/types.ts`)可赋值。

任何一侧 schema 变更导致样例不再合法,即视为协议破坏,必须同步修改双端。

| 文件 | 对应消息/模型 | 后端模型 | 前端类型 |
|---|---|---|---|
| `stream.configure.json` | WS 文本控制消息 | `SessionConfig` | `SessionConfig` |
| `inference.result.json` | WS 推理结果消息 | `InferenceResult` | `InferenceResult` |
| `error.json` | WS 错误消息 | `ErrorInfo` | `ErrorInfo` |
| `device.status.json` | WS 设备状态消息 | `DeviceStatus` | `DeviceStatus` |

注:`stream.configure` / `inference.result` / `error` / `device.status` 的完整
消息体还包含 `type` 等包装字段;WebSocket 消息封包在单元 1.3 实现,当前样例
按 api-contract.md 第 3 节的最终形态维护。
