# 调研发现

本文件记录对 `v6demo` 的代码审计结果、约束与架构依据。外部资料如后续需要检索，也只记录在此文件中。

## 待确认

- `v6demo` 的实际 CLI 主入口。
- 输入源支持范围：文件、USB 摄像头、RTSP、逐帧图像。
- 输出结果格式：stdout、JSON、图片/视频、数据库或报告。
- 开发板上可用的硬件解码能力与当前失败点。
- 需要在手机显示的最小状态和控制项。

## `v6demo` 审计结果

- 项目定位：RK3568 端侧警务 AI 助手；实时链路为 C++，事后处理为 Python，推理栈包含 RKNN、sherpa-onnx、YAMNet 和 llama.cpp。
- 当前主入口：`v6demo/src/realtime/cpp/video_demo.cc`，参数形式仍是位置参数，输入是本地视频路径，输出目录包含 `result.mp4`、NDJSON `result.json`、`chain.log` 和 `timing.json`。
- 编排入口：`v6demo/scripts/run_pipeline.sh`，先运行 `video_demo`，再用 ffmpeg 将原始音轨合入 `result_audio.mp4`。
- 当前视频 I/O：`video_io.{h,cc}` 直接使用 FFmpeg/libav；板上 OpenCV 无 FFmpeg 支持，MPP 固件未就绪，因此视频软解、libx264 软编。
- 已测瓶颈：576p/720p 的软编码约 67–102 ms/帧；3414×1920 约 748 ms/帧。NPU 推理约 40 ms/帧，不是主要可变瓶颈。
- 当前链路是“离线文件处理并落盘”，不是持续流服务；要支持手机实时监视，不能只在外面套一个网页去执行 CLI，必须增加长期运行的服务与流式输入/输出适配层。
- `result.json` 已是可复用的结构化事件来源；`timing.json` 可用于性能面板；`chain.log`/root hash 可用于证据状态显示。

## 初步判断：手机能否解决解码问题

- **能减轻一部分，但不会自动解决全部问题。** 手机可以承担摄像头采集与 H.264 硬编码，避免 HEVC 文件在板端软解的高开销；浏览器也能直接显示板端返回的视频流。
- 若板端仍需对每帧运行模型，就仍必须在板端把压缩流解成像素帧。没有可用 MPP 硬解时，板端仍有解码成本。
- 更稳妥的 v1 是让手机端按可控帧率发送 JPEG/WebP 图像帧，板端省去 H.264/HEVC 解码集成难题，但带宽和图像压缩开销更高；适合先跑通协议和 GUI。
- v2 再升级为 WebRTC/H.264：手机硬编、板端用 GStreamer/FFmpeg 接流并在可用时切换 MPP；浏览器接收结果叠加层，不要求板端重新编码整幅标注视频。
- 最大的编码优化来自“传原始预览流 + 单独传 JSON 检测框，由手机 Canvas 叠加”，这样板端无需为 GUI 持续软编码 `result.mp4`。

## 协议与浏览器依据（2026-09-14 核验）

- `getUserMedia()` 只在安全上下文中可用，并且必须获得用户对摄像头/麦克风的授权。因此手机通过局域网 IP 访问时仍要提供可信 HTTPS，不能把明文 HTTP 当成正式方案。来源：[MDN getUserMedia](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia)。
- WebRTC 兼容实现的基线视频编解码包括 VP8 与 H.264 Constrained Baseline，音频包括 Opus 与 G.711。H.264 + Opus 适合作为 v2 首选协商组合，但必须保留协商/回退，不能假设任意 HEVC 流都可用。来源：[MDN WebRTC codecs](https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Formats/WebRTC_codecs)。
- MediaMTX 当前文档列出 WebRTC、RTSP、RTMP、HLS、SRT 等发布/读取能力，可作为浏览器 WebRTC 与板端 RTSP/GStreamer/FFmpeg 之间的候选协议桥；是否使用仍需在 RK3568 实测后决定。来源：[MediaMTX introduction](https://mediamtx.org/docs/kickoff/introduction)。

## 接口设计依据

- 现有 NDJSON 字段包含 `frame_idx`、`timestamp`、`detections`、可选 `fight`、`audio_event`、`faces`、`hash`，足够作为新协议的兼容输入。
- 现有 bbox 是源视频像素坐标；手机屏幕方向和 Canvas 尺寸会变化，新协议应使用 0–1 归一化 bbox，并保留源尺寸用于审计。
- 实时系统不能按离线视频方式保证“每帧必处理”；应保证结果与 `seq` 对齐，同时明确上报丢帧数和推理延迟。
- v6 哈希链覆盖每个视频帧；实时 latest-frame-wins 会主动丢帧，因此不能直接宣称继承同等证据链语义。v1 先记录会话和事件，后续需单独设计“采集帧链 + 推理事件链”。
