/**
 * Mobile Monitor 统一协议类型(v1)。
 *
 * 与后端 Pydantic schema 一一对应:
 *   backend/app/schemas/{common,session,inference,device}.py
 * 任何一侧变更必须同步另一侧,并由 configs/schema-examples 的
 * 双端解析样例验证。
 */

/** 所有 JSON 消息携带的协议版本;不兼容变更时递增。 */
export const PROTOCOL_VERSION = 1;

// ---------- session ----------

export type SessionState =
  | "disconnected"
  | "pairing"
  | "ready"
  | "streaming"
  | "stopping"
  | "degraded"
  | "failed";

export interface VideoConfig {
  width: number;
  height: number;
  fps: number;
  format: "jpeg" | "webp";
}

export interface AudioConfig {
  sample_rate: number;
  channels: 1;
  format: "pcm_s16le";
}

export interface SessionConfig {
  video: VideoConfig;
  audio: AudioConfig;
  models: string[];
}

// ---------- inference ----------

/** [x1, y1, x2, y2],0–1 归一化,后端拒绝像素坐标。 */
export type BboxNorm = [number, number, number, number];

export interface Detection {
  class_id: number;
  class_name: string;
  bbox_norm: BboxNorm;
  confidence: number;
  track_id?: number;
}

export interface InferenceResult {
  protocol_version: number;
  session_id: string;
  seq: number;
  capture_ts_ms: number;
  server_ts_ms: number;
  infer_ms: number;
  detections: Detection[];
  fight?: { prob: number; active: boolean };
  audio_events: Record<string, unknown>[];
  faces: Record<string, unknown>[];
  stats: { queue_depth: number; dropped_frames: number } & Record<string, unknown>;
}

export interface ModelStatus {
  name: string;
  loaded: boolean;
  load_ms?: number;
  error?: string;
}

// ---------- error ----------

export type ErrorCode =
  | 1 // PROTOCOL_MISMATCH
  | 2 // SESSION_NOT_FOUND
  | 3 // SESSION_STATE_INVALID
  | 4 // RATE_LIMIT
  | 5 // PAYLOAD_TOO_LARGE
  | 6 // ADAPTER_ERROR
  | 7 // ADAPTER_UNAVAILABLE
  | 8; // INTERNAL

export interface ErrorInfo {
  code: ErrorCode;
  message: string;
  session_id?: string;
  detail?: Record<string, unknown>;
}

// ---------- device ----------

export type ModelHealth = "not_loaded" | "loading" | "ready" | "error";

export interface ResourceUsage {
  cpu_percent: number;
  memory_percent: number;
  memory_used_mb: number;
  temperature_c?: number;
  disk_free_mb: number;
}

export interface DeviceStatus {
  platform: string;
  uptime_s: number;
  resources: ResourceUsage;
  models: Record<string, ModelHealth>;
  network_rtt_ms?: number;
  dropped_frames: number;
}

// ---------- healthz ----------

export interface Healthz {
  status: "ok";
  protocol_version: number;
}
