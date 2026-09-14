# v1 PC 总体架构

## 1. 结论

首版采用 **手机 PWA + PC FastAPI 网关 + 可替换推理 adapter**。手机本地直接显示摄像头预览；只把降采样后的帧送去推理，服务端返回结构化结果，手机用 Canvas 叠加检测框。这样可以先验证完整交互，同时绕开板端持续生成标注视频造成的软编码瓶颈。

## 2. 系统边界

```text
手机 PWA
  ├─ getUserMedia：摄像头、麦克风
  ├─ 本地 <video>：零等待预览
  ├─ Canvas：检测框/人脸/打架/音频告警叠加
  └─ WebSocket：帧、PCM、控制、结果
             │ HTTPS/WSS（局域网）
             ▼
Mobile Monitor API（PC，后续迁移开发板）
  ├─ 配对鉴权 / 会话状态机 / 限流
  ├─ 最新帧队列（有界，过期即丢）
  ├─ 事件时间线与设备指标
  └─ InferenceAdapter 接口
       ├─ MockAdapter（1.2）
       ├─ ReplayAdapter：读取 v6 NDJSON（1.4）
       ├─ OnnxAdapter（PC 全链路验证）
       └─ V6WorkerAdapter（RK3568，后续版本）
```

## 3. 为什么不直接给 CLI 套网页

现有 `video_demo` 面向本地视频文件：启动时加载模型，处理到文件结束，再产出 MP4/NDJSON/计时/哈希链。若每帧或每小段都启动一次 CLI，会重复加载模型、产生大量临时文件并增加数秒延迟。

实时版本需要常驻 worker：模型只加载一次，持续接收帧并持续输出 JSON 事件。GUI 与 worker 之间只能通过固定协议交互，不能让浏览器传入 shell 命令或任意路径。

## 4. 媒体链路

### v1：低风险验证链路

- 摄像头：手机 `<video>` 本地预览；按 640×360、初始 3 FPS 抽帧为 JPEG/WebP，经 WSS 发送。
- 推理：服务端只保留最新待处理帧；当推理速度落后时丢弃旧帧，不积累延迟。
- 结果：返回与输入 `seq` 对齐的归一化 bbox、事件和耗时；手机 Canvas 叠加。
- 麦克风：采样为单声道 PCM16LE/16 kHz 小块，供 ASR/YAMNet adapter；v1 可先实现采集和回环，再接模型。
- 扬声器：手机播放服务端返回的告警音或 TTS 文件；首版不做全双工对讲。

### v2：低延迟媒体链路

- 将手机上行改为 WebRTC，优先协商 H.264 Constrained Baseline + Opus，保留 VP8/PCM 兼容路径。
- 媒体服务可采用 MediaMTX 作为协议桥；是否纳入正式部署必须先在目标板验证二进制体积、架构和性能。
- 开发板收到 H.264 后仍需解码才能推理；优先接 MPP，失败时回退 FFmpeg 软解并降低分辨率/帧率。
- 手机继续用本地预览 + JSON 叠加，不要求开发板把画过框的整幅视频重新编码回传。

## 5. “手机能否解决解码问题”

只能部分解决：

- 手机可承担摄像头采集与硬件编码，避免输入 HEVC 文件的某些兼容问题。
- v1 发送 JPEG/WebP 帧时，板端不再做 H.264/HEVC 视频流解码，但仍需解图片。
- v2 发送 H.264 时，板端为了模型推理仍要解码成 RGB/NV12；MPP 不可用则解码成本仍存在。
- 真正确定能省掉的是 **板端标注视频软编码**：只回传 JSON，由手机端叠加即可。

## 6. 页面范围

首版只做四个页面/区域：

1. **实时监控**：本地视频、检测框、连接状态、推理 FPS、开始/停止、前后摄像头切换、麦克风开关。
2. **告警时间线**：危险物、打架、人脸、音频事件，含时间、置信度与抓拍。
3. **设备状态**：CPU/NPU 占用、内存、温度、磁盘、模型加载状态、网络延迟和丢帧数。
4. **设置**：采集分辨率、发送 FPS、阈值、启用的模型；所有值由服务器校验。

## 7. 状态机与失败行为

```text
DISCONNECTED → PAIRING → READY → STREAMING → STOPPING → READY
                                └─ 错误 → DEGRADED / FAILED
```

- 网络断开：手机提示并指数退避重连；服务端在超时后关闭会话。
- 推理过慢：丢旧帧、显示 dropped_frames，不把实时画面拖成历史回放。
- 摄像头/麦克风拒绝：保留监视与设备状态功能，明确显示权限错误。
- adapter 崩溃：会话进入 DEGRADED，禁止伪造“正常”结果；可重启 worker，但不自动重放实时帧。

## 8. 安全基线

- 手机媒体 API 只在可信 HTTPS 页面使用；开发期也不能用手机直接访问明文 `http://<PC-IP>`。
- 首次连接显示一次性二维码，包含设备地址、短期 pairing code 和证书指纹；完成后换取短期 token。
- API 默认只监听配置的局域网接口；不开放公网，不启用默认密码。
- 事件日志、抓拍和录音按会话目录保存；配置保留天数，提供显式清理，不上传云端。
- 所有控制操作都进入审计日志；不得允许前端指定服务器任意文件路径。

## 9. 不在 v1 范围

- 公网穿透、多用户并发、多板集群、云端账号体系。
- iOS/Android 原生 App、后台锁屏持续采集、全双工对讲。
- 在 GUI 中训练/转换模型。
- 修改 `v6demo` 的识别算法或精度调优。

## 10. 外部技术依据

- 浏览器摄像头/麦克风访问要求安全上下文和用户授权：[MDN getUserMedia](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia)
- WebRTC 兼容实现需支持 VP8/H.264 基线视频和 Opus/G.711 音频：[MDN WebRTC codecs](https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Formats/WebRTC_codecs)
- MediaMTX 支持 WebRTC、RTSP、RTMP、HLS 等多种发布/读取协议，可作为后续协议桥候选：[MediaMTX introduction](https://mediamtx.org/docs/kickoff/introduction)

