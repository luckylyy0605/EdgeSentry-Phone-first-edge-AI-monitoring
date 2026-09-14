import type { Healthz } from "./protocol/types";

/**
 * 1.1 骨架页:仅验证 PWA 壳与协议类型可用。
 * 摄像头预览、WebSocket、会话控制属 1.2/1.3,不在此实现。
 */

export default function App() {
  const healthz: Healthz = { status: "ok", protocol_version: 1 };

  return (
    <main className="app">
      <h1>Mobile Monitor</h1>
      <p className="status-line">
        backend healthz: {healthz.status} · protocol v{healthz.protocol_version}
      </p>
    </main>
  );
}
