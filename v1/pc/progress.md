# Mobile Monitor v1 PC 进度

## 当前状态

- 阶段:单元 1.1 完成,待实机验证
- 当前单元:1.1(工程骨架与协议 schema)
- 代码:backend + frontend 骨架已创建并通过验证

## 已完成(单元 1.1)

- 后端 `backend/app/`:FastAPI 入口 + `GET /healthz`(仅 status/protocol_version,无敏感字段)。
- 协议 schema `backend/app/schemas/`:
  - `common.py`:PROTOCOL_VERSION=1、ErrorCode(8 类)、ErrorInfo;
  - `session.py`:SessionState 七态、Video/Audio/SessionConfig(范围校验,拒绝 h264);
  - `inference.py`:Detection(bbox 0–1 强制,拒像素坐标与倒序框)、InferenceResult、ModelStatus(失败必须带 error);
  - `device.py`:ResourceUsage、DeviceStatus、ModelHealth。
- 前端 `frontend/`:Vite+React18+TS strict、PWA manifest、HTTPS dev 配置、`src/protocol/types.ts` 与后端 schema 对应。
- 契约样例 `configs/schema-examples/`:stream.configure / inference.result / error / device.status,后端测试逐个解析。
- 测试 `backend/tests/`:22 项,含契约示例解析、像素 bbox 拒绝、错误协议版本拒绝。

## 已知问题

- 前端协议类型与后端 schema 目前人工保持同步;1.3 引入 WebSocket 消息封包时评估是否用 datamodel-codegen 自动生成。
- Node.js 为便携版(`D:\software\node-v24.19.0-win-x64`),不在系统 PATH;跑前端命令需临时前缀。
- vite dev 代理目标写死 `https://localhost:8443`;1.2 做 HTTPS 证书与后端启动脚本时必须改为配置驱动(项目规则:地址/端口来自配置)。

## 验证记录

- `python -m pytest tests/ -v`(backend):22 passed in 0.34s。
- `npm run build`(frontend):tsc --noEmit 0 错误,vite build 成功(142.81 kB JS / gzip 45.92 kB)。
- 未验证:uvicorn 启动 healthz 的手工 curl(留给 1.2 的 HTTPS 环境一起验)、手机实机访问、双端样例的前端侧自动解析(前端为纯类型,无可执行检查)。
- 用户已在 WSL 内完成首次 `git push -u origin main`(Windows 侧 SSH 未配 GitHub key)。

## 单元外说明

- 本轮环境适配耗时长:Node MSI 安装故障(WinGet 报成功但文件未落盘),最终用便携版解决;细节记于根 progress.md。
- 用户要求 commit message 一律不加 Co-Authored-By,历史已改写去署名(远程需 force push 覆盖)。

