# 开发进度

## 2026-09-14：单元 1.1 工程骨架与协议 schema

- 本轮只处理单元 1.1,未提前实现后续单元。
- 建立 Mobile_Monitor 独立 git 仓库(main 分支),远程指向 `EdgeSentry-Phone-first-edge-AI-monitoring`。
- 环境适配:Node.js 因 MSI 安装失败(注册表已登记但文件未落盘,Error 1730 需管理员),改用便携版 v24.19.0 于 `D:\software\node-v24.19.0-win-x64`,未改系统 PATH。
- 新增后端 `v1/pc/backend/`:FastAPI + `GET /healthz`;Pydantic schema 覆盖 session/inference/error/device;bbox 强制 0–1 归一化,协议版本与帧率范围显式校验。
- 新增前端 `v1/pc/frontend/`:Vite + React + TypeScript strict 骨架,PWA manifest,`src/protocol/types.ts` 与后端 schema 逐字段对应。
- 新增 `v1/pc/configs/schema-examples/`:4 个双端契约样例,由后端测试保证可解析。
- Git 记录:按用户要求,commit message 不加 Co-Authored-By;已两次按用户指示执行 commit(项目文档、后端、历史改写去署名)。

## 验证记录

- `python -m pytest tests/ -v`(backend):22 passed。
- `npm run build`(frontend,含 tsc --noEmit):31 modules transformed,built in 372ms,类型检查 0 错误。
- 未验证项:手机实机访问、uvicorn 实际启动、WSL 内 git push(用户自行完成,成功)。
- 环境遗留:Windows 侧 git push 需复制 WSL 的 `id_ed25519_github_v2` 公钥到 GitHub 账号或本地 ssh config;系统注册表残留 Node.js 假安装记录,不影响本项目。

## 2026-09-14：方案设计启动

- 已创建独立项目目录 `Mobile_Monitor/`。
- 已明确本轮只做架构和版本规划，不改动 `v6demo`。
- 当前正在审计 `v6demo` 的入口、数据流和已知问题。
- 已完成入口与 I/O 审计：现有实现是本地视频文件 CLI，输出 MP4/NDJSON/计时/哈希链。
- 已确认主要实时化障碍是“文件型 CLI + 板端软编”，不是简单增加网页按钮即可解决。
- 已形成两阶段媒体策略：v1 图片帧闭环，v2 WebRTC/H.264；手机端用 JSON 叠加检测框，避免板端重新编码预览视频。
- 已创建 `README.md`、`CLAUDE.md`、`.gitignore` 和 `v1/pc` 平台骨架。
- 已完成总体架构、API/二进制媒体包、adapter 接口、页面范围、安全基线与 1.1–1.8 路线设计。
- 已明确实时上板需要 `v6_worker` 常驻协议；完全不改旧项目时只能支持离线视频任务。
- 用户确认 v6 有用资产需要在新项目中保留，但应在交互页面完成后整理；已增加 1.9 迁移清单单元。
- 已强化 Claude Code 规则：工作日志强制落盘；Git 写操作逐次询问，未经同意不执行。
- 客户端方案确定为 v1 响应式 HTML/PWA，暂不开发原生 App。

## 验证记录

- 已递归检查项目文件：共 11 个文档/配置骨架文件，路径符合 `项目/v1/pc` 规范。
- 已检索确认 `CLAUDE.md`、平台 `AGENTS.md` 与 roadmap 同时包含：PWA 选择、工作日志、Git 逐次授权和 1.9 v6 资产整理规则。
- `git status --short -- Mobile_Monitor` 显示整个新目录为未跟踪；未执行 add、commit、push 或其他 Git 写操作。
- Git 输出一条用户级全局 ignore 文件无权限警告，不影响本次状态判断。
- 尚未运行代码验证；当前只有方案与文档脚手架，1.1 尚未开始。
