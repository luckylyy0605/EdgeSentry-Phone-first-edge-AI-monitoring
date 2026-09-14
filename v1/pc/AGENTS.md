# Mobile Monitor v1 PC

## 项目身份

在 PC 上验证“手机浏览器采集摄像头/麦克风 → 后端接收 → 可替换推理 adapter → 手机实时叠加结果与告警”的最小闭环。

技术栈：TypeScript + React/Vite PWA；Python 3.11 + FastAPI/Uvicorn；WebSocket；pytest；Playwright（端到端测试）

运行环境：Windows PC 开发；手机与 PC 位于同一局域网，通过 HTTPS 访问。

## 开始任何任务前，必须先读

- `../../task_plan.md`
- `../../findings.md`
- `../../progress.md`
- `progress.md`
- `docs/architecture.md`
- `docs/api-contract.md`
- `docs/roadmap.md`
- `configs/`（创建后）

## 目录结构

```text
v1/pc/
├── AGENTS.md
├── progress.md
├── docs/
│   ├── architecture.md
│   ├── api-contract.md
│   └── roadmap.md
├── frontend/              # PWA（实施 1.1 时创建）
├── backend/               # FastAPI（实施 1.1 时创建）
├── adapters/              # mock / replay / ONNX adapter
├── configs/               # 非敏感配置与 schema
├── tests/
└── scripts/
```

## 开发节奏

- 每次只完成一个编号单元（1.1、1.2……）。
- 完成后必须运行该单元列出的验证命令并写入 `progress.md`。
- 验证通过后只建议 Git commit，并询问用户是否执行；未经用户明确同意不得 add/commit/push。
- 用户同意后，commit message 格式：`feat(1.1): 描述`。
- 不得跨单元一次性执行。

## 编码规范

- Python：类型注解完整；路径使用 `pathlib.Path`；Pydantic 定义外部消息 schema。
- TypeScript：开启 strict；禁止 `any`；协议类型由 schema 生成或集中定义。
- 每个 WebSocket 消息必须带 `protocol_version`、`session_id`、`seq` 或 `event_id`。
- 坐标跨端传输统一使用 0–1 归一化值；adapter 内部负责与 `v6demo` 像素坐标转换。
- 队列必须有上限；实时帧采用 latest-frame-wins。

## 禁止行为

- 禁止前端执行任意命令或传入任意服务器文件路径。
- 禁止把 `v6demo` 源码、模型和输出目录复制进本项目。
- 禁止为 v1 引入公网账号体系、云数据库、Kubernetes 或多租户设计。
- 禁止用 Base64 JSON 传连续媒体数据。
- 禁止在 HTTP 明文页面请求手机摄像头/麦克风。
- 禁止在完成单元 1.8 前批量复制 `v6demo`；1.9 仅复制迁移清单批准的内容。

## 当前阶段

见 `progress.md`。当前为设计冻结前，尚未开始 1.1 实施。
