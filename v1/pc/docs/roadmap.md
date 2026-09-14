# 开发路线与验收

## 版本策略

只创建正在开发的版本/平台目录：当前为 `v1/pc`。完成 PC 闭环后再创建 `v1/rk3568`；架构发生不兼容变化时才创建 `v2`，不要把每个小功能都升级为新版本。

## v1 PC：完整闭环验证

### 1.1 工程骨架与协议 schema

- 创建 frontend/backend/tests/configs。
- 定义 Pydantic + TypeScript 的会话、结果、错误和设备状态类型。
- 实现 `/healthz` 与契约测试。

验收：后端测试通过；前端类型检查和构建通过；无 `any`；schema 示例可双端解析。

### 1.2 手机 PWA 摄像头预览

- HTTPS 开发环境、权限提示、前后摄像头切换。
- 本地 `<video>` + Canvas overlay，不接真实模型。
- 显示权限拒绝、无摄像头、页面后台化等状态。

验收：Android Chrome 与 iOS Safari 至少各记录一次实机结果；若暂缺设备，必须标记未覆盖，不得写“通过”。

### 1.3 WSS 会话与有界帧队列

- 创建/停止会话；二进制 JPEG/WebP 帧上传。
- latest-frame-wins 队列、帧率/尺寸限制、重连与丢帧统计。
- MockAdapter 返回可预测检测框。

验收：连续 10 分钟无队列增长；人为降低 adapter 速度后延迟保持有界且 dropped_frames 增长。

### 1.4 v6 结果回放兼容

- 读取现有 `result.json` NDJSON 与 `timing.json`。
- 转为统一 schema，在手机按时间轴回放检测框、打架、人脸、音频事件和性能指标。

验收：至少用一个现有 v6 输出目录回放；bbox 与原视频尺寸对应；坏 JSON 行显式报错。

### 1.5 PC 推理 adapter

- 接一个轻量 ONNX 模型或已存在的 PC 推理入口，保持与 v6 schema 一致。
- 模型只加载一次；运行指标进入设备/性能面板。

验收：手机实时画面产生真实结果；模型加载次数为 1；统计推理 P50/P95 和端到端 P50/P95。

### 1.6 手机麦克风与扬声器闭环

- 麦克风采集、16 kHz 单声道 PCM 包、静音控制。
- 接 mock/PC 音频事件 adapter；手机播放告警音。
- 明示录音状态和权限，停止会话后释放设备。

验收：音频 seq 连续、时钟漂移有记录；权限拒绝时视频功能仍可用；停止后系统录音指示消失。

### 1.7 事件时间线、设备面板与会话落盘

- 告警卡片、抓拍、筛选、设备指标。
- 原子写入 session/events/device；异常退出后可读取已完成记录。

验收：断网、磁盘不足、adapter 崩溃三种故障均在 UI 和日志中显式出现。

### 1.8 PC 端到端验收与设计冻结

- 自动化 API/协议测试 + 浏览器 E2E。
- 手机实机走完整开始、监控、告警、停止、回放流程。
- 记录带宽、CPU、内存、推理时延、端到端时延和丢帧率。

验收：所有必测项有数据；未测平台明确列出；冻结 v1 protocol schema。

### 1.9 `v6demo` 有用资产整理

本单元必须在交互页面和 PC 闭环完成后执行。先建立 `docs/v6-migration-manifest.md`，逐项记录源路径、目标路径、用途、是否修改、依赖和验证方式，再按清单选择性复制。

分类原则：

- **复制并维护**：与新协议直接相关、体积小、边界清楚的 schema、解析器、测试样例或通用模块。
- **外部引用**：模型权重、llama 运行时、测试视频、法条库、大型第三方代码；通过配置路径引用，不重复纳入 Git。
- **适配/重写**：`video_demo.cc` 这类单体 CLI 的实时部分，抽成 `v6_worker` 协议，不直接整文件复制后继续堆功能。
- **不迁移**：PPT、历史输出、临时调试脚本、重复模型和与手机闭环无关的实验资产。

验收：清单中每个复制项都有来源和测试；新项目在不依赖 `v6demo/output`、临时目录和绝对路径时仍能运行；大型资产仍在 `.gitignore` 外部管理。

## v1 RK3568：完成 PC 后再创建目录

建议单元：

- R1：板上 API/证书/设备指标运行。
- R2：实现 `v6_worker` + Unix socket，模型只加载一次。
- R3：JPEG 帧 → RKNN → JSON 结果闭环，先关闭结果视频编码。
- R4：接 PCM 音频事件/ASR。
- R5：验证 MPP；若可用，再接 WebRTC/H.264，否则保留 JPEG 降级路径。
- R6：压力、温度、掉线恢复、证据产物验收。

## 后续版本候选

- `v2`：WebRTC/MediaMTX、H.264/Opus、低延迟动态码率；只有协议/架构不兼容时创建。
- `v3`：公网安全接入、多个手机/设备管理；只有确有需求时创建。

## Claude Code 单元提示词模板

```text
请先完整读取 Mobile_Monitor/CLAUDE.md、Mobile_Monitor/task_plan.md、
Mobile_Monitor/findings.md、Mobile_Monitor/v1/pc/AGENTS.md、
Mobile_Monitor/v1/pc/progress.md 和 docs/roadmap.md。

本次只完成单元 1.X：<名称>，不得提前实现后续单元。
编码前先列出假设、涉及文件、成功标准和验证命令。
实现后运行验证，更新根 progress.md 与 v1/pc/progress.md；
任何跳过项或失败必须显式记录。不要提交模型、视频、证书或密钥。
验证完成后显示 git status/diff 摘要并询问我是否需要 commit；
未经我明确同意，不得执行 add、commit、push、建分支、merge、rebase 或 tag。
```
