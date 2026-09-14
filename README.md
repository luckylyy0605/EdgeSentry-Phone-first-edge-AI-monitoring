# Mobile Monitor

`Mobile_Monitor` 是一个独立于 `v6demo` 的手机端监控与外设接入项目。手机负责 GUI、摄像头、麦克风和扬声器；PC/开发板负责会话管理、模型推理、事件记录和设备状态采集。

当前只创建 `v1/pc`，先在 PC 跑通完整闭环。RK3568 与 Ascend 平台目录在真正开始迁移时再创建。

## 文档入口

- `task_plan.md`：本轮设计工作的阶段与决策
- `findings.md`：对 `v6demo` 的审计结果
- `v1/pc/docs/architecture.md`：总体架构与媒体链路
- `v1/pc/docs/api-contract.md`：手机、服务端、推理适配器的协议
- `v1/pc/docs/roadmap.md`：编号开发单元与验收标准

## 与 `v6demo` 的关系

新项目不复制模型、权重或 `v6demo` 业务代码。它只依赖一个版本化的推理协议。PC 阶段使用 mock/ONNX adapter；RK3568 阶段通过本地 IPC 对接 `v6demo` 的常驻推理 worker。

现有 `v6demo` CLI 仍可作为“上传视频后离线分析”的兼容入口，但不作为实时监控主链路。

