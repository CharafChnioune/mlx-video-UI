const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ||
  (typeof window !== "undefined" && window.location.port === "3000"
    ? `http://${window.location.hostname}:8001`
    : "");

// =====================
// GENERATION TYPES
// =====================

export interface GenerationParams {
  prompt: string;
  negative_prompt?: string;
  output_filename?: string;
  height: number;
  width: number;
  num_frames: number;
  seed: number;
  fps: number;
  pipeline: "distilled" | "dev" | "keyframe" | "ic_lora";
  steps?: number;
  cfg_scale?: number;
  model_repo?: string;
  text_encoder_repo?: string;
  checkpoint_path?: string;
  enhance_prompt?: boolean;
  auto_output_name?: boolean;
  tiling?: "auto" | "none" | "default" | "aggressive" | "conservative" | "spatial" | "temporal";
  cache_limit_gb?: number;
  memory_limit_gb?: number;
  eval_interval?: number;
  audio?: boolean;
  stream?: boolean;
  mem_log?: boolean;
  clear_cache?: boolean;
  conditioning_image?: string;
  conditioning_frame_idx?: number;
  conditioning_strength?: number;
  video_conditioning?: string;
  conditioning_mode?: "replace" | "guide";
  loras?: { path: string; strength: number }[];
  distilled_loras?: { path: string; strength: number }[];
  extra_args?: string[];
}

export interface GenerationJob {
  job_id: string;
  status: "pending" | "processing" | "completed" | "error";
  progress?: number;
  current_step?: string;
  download_progress?: number;
  download_step?: string;
  preview_path?: string;
  output_path?: string;
  error?: string;
}

export interface ProgressUpdate {
  type: "progress" | "status" | "complete" | "error";
  job_id: string;
  progress?: number;
  current_step?: string;
  download_progress?: number;
  download_step?: string;
  preview_path?: string;
  output_path?: string;
  error?: string;
}

export interface JobStatusResponse {
  job_id: string;
  status: "pending" | "processing" | "completed" | "error";
  progress?: number;
  current_step?: string;
  download_progress?: number;
  download_step?: string;
  preview_path?: string;
  output_path?: string;
  error?: string;
}

export interface EnhanceResponse {
  enhanced: string;
  negative_prompt?: string;
  filename?: string;
}

export type EnhanceProvider = "local" | "ollama" | "lmstudio";

export interface EnhanceRequest {
  prompt: string;
  negative_prompt?: string;
  provider: EnhanceProvider;
  model?: string;
  base_url?: string;
  max_tokens?: number;
  temperature?: number;
  seed?: number;
}

export interface EnhanceModelInfo {
  id: string;
  display_name: string;
  state: "loaded" | "not-loaded" | null;
  type: "llm" | "embedding";
  instance_id?: string;
}

export interface EnhanceModelsResponse {
  models: string[];
  model_details?: EnhanceModelInfo[];
}

// =====================
// TRAINING TYPES
// =====================

export interface LoraConfig {
  rank: number;
  alpha: number;
  dropout: number;
  target_modules: string[];
}

export interface TrainingParams {
  // Model config
  model_repo: string;
  pipeline: "dev" | "distilled";
  training_mode: "lora" | "full";

  // Training strategy
  strategy: "text_to_video" | "video_to_video" | "ic_lora";
  with_audio: boolean;
  first_frame_conditioning_p: number;

  // LoRA config (when training_mode is "lora")
  lora_rank: number;
  lora_alpha: number;
  lora_dropout: number;
  lora_target_modules: string[];

  // Optimization
  learning_rate: number;
  steps: number;
  batch_size: number;
  gradient_accumulation_steps: number;
  max_grad_norm: number;
  optimizer_type: "adamw" | "adamw8bit";
  scheduler_type: "constant" | "linear" | "cosine" | "cosine_with_restarts" | "polynomial";
  enable_gradient_checkpointing: boolean;

  // Data
  data_root: string;
  num_dataloader_workers: number;

  // Acceleration
  mixed_precision_mode: "no" | "fp16" | "bf16";
  quantization: string | null;
  load_text_encoder_in_8bit: boolean;

  // Checkpoints
  checkpoint_interval: number;
  keep_last_n_checkpoints: number;
  checkpoint_precision: "float32" | "bfloat16";

  // Validation
  validation_prompts: string[];
  validation_interval: number | null;
  validation_video_dims: [number, number, number]; // [width, height, frames]
  validation_seed: number;
  validation_inference_steps: number;
  validation_guidance_scale: number;
  validation_fps: number;
  skip_initial_validation: boolean;

  // Output
  output_dir: string;
  seed: number;

  // Logging
  log_every: number;
  wandb_enabled: boolean;
  wandb_project: string;
}

export interface TrainingJob {
  job_id: string;
  status: "pending" | "training" | "completed" | "error" | "stopped";
  progress?: number;
  current_step?: number;
  total_steps?: number;
  current_loss?: number;
  learning_rate?: number;
  eta?: string;
  checkpoint_path?: string;
  error?: string;
}

export interface TrainingProgressUpdate {
  type: "progress" | "validation" | "checkpoint" | "complete" | "error";
  job_id: string;
  step?: number;
  total_steps?: number;
  loss?: number;
  learning_rate?: number;
  eta?: string;
  validation_video?: string;
  checkpoint_path?: string;
  error?: string;
}

// Default training parameters
export const defaultTrainingParams: TrainingParams = {
  model_repo: "Lightricks/LTX-2",
  pipeline: "dev",
  training_mode: "lora",

  strategy: "text_to_video",
  with_audio: false,
  first_frame_conditioning_p: 0.1,

  lora_rank: 64,
  lora_alpha: 64,
  lora_dropout: 0.0,
  lora_target_modules: ["to_k", "to_q", "to_v", "to_out.0"],

  learning_rate: 5e-4,
  steps: 3000,
  batch_size: 1,
  gradient_accumulation_steps: 1,
  max_grad_norm: 1.0,
  optimizer_type: "adamw",
  scheduler_type: "linear",
  enable_gradient_checkpointing: false,

  data_root: "",
  num_dataloader_workers: 2,

  mixed_precision_mode: "bf16",
  quantization: null,
  load_text_encoder_in_8bit: false,

  checkpoint_interval: 250,
  keep_last_n_checkpoints: 3,
  checkpoint_precision: "bfloat16",

  validation_prompts: [],
  validation_interval: 100,
  validation_video_dims: [512, 512, 33],
  validation_seed: 42,
  validation_inference_steps: 50,
  validation_guidance_scale: 4.0,
  validation_fps: 24.0,
  skip_initial_validation: false,

  output_dir: "./training_output",
  seed: 42,

  log_every: 1,
  wandb_enabled: false,
  wandb_project: "ltx-trainer",
};

// =====================
// SYSTEM API
// =====================

export interface HardwareInfo {
  platform: string;
  cpu: string;
  cores: number;
  memory_gb: number;
  is_apple_silicon: boolean;
  mlx_version?: string | null;
  python_version: string;
}

export interface DefaultSettings {
  generation: Partial<GenerationParams>;
  training: Partial<TrainingParams>;
}

export async function getHardwareInfo(): Promise<HardwareInfo> {
  const response = await fetch(`${API_BASE}/api/system/hardware`);
  if (!response.ok) {
    throw new Error("Failed to fetch hardware info");
  }
  return response.json();
}

export async function getDefaultSettings(): Promise<DefaultSettings> {
  const response = await fetch(`${API_BASE}/api/system/defaults`);
  if (!response.ok) {
    throw new Error("Failed to fetch defaults");
  }
  return response.json();
}

// =====================
// GALLERY TYPES
// =====================

export interface GalleryVideo {
  id: string;
  filename: string;
  path: string;
  thumbnail?: string;
  prompt?: string;
  params?: Partial<GenerationParams>;
  created_at: string;
  duration?: number;
  width?: number;
  height?: number;
  size?: number;
}

// =====================
// GENERATION API
// =====================

export async function startGeneration(
  params: GenerationParams
): Promise<GenerationJob> {
  const response = await fetch(`${API_BASE}/api/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to start generation");
  }

  return response.json();
}

export async function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  const response = await fetch(`${API_BASE}/api/status/${jobId}`);
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to fetch job status");
  }
  return response.json();
}

export async function uploadImage(file: File): Promise<string> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/api/upload/image`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to upload image");
  }

  const data = await response.json();
  return data.path;
}

export async function uploadVideo(file: File): Promise<string> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/api/upload/video`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to upload video");
  }

  const data = await response.json();
  return data.path;
}

export function connectWebSocket(
  jobId: string,
  onMessage: (update: ProgressUpdate) => void,
  onError?: (error: Event) => void,
  onClose?: () => void
): WebSocket {
  const wsBase = API_BASE
    ? API_BASE.replace(/^http/, "ws")
    : `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.host}`;
  const ws = new WebSocket(`${wsBase}/api/ws/progress/${jobId}`);

  ws.onmessage = (event) => {
    try {
      const update = JSON.parse(event.data);
      onMessage(update);
    } catch (e) {
      console.error("Failed to parse WebSocket message:", e);
    }
  };

  ws.onerror = (error) => {
    console.error("WebSocket error:", error);
    onError?.(error);
  };

  ws.onclose = () => {
    onClose?.();
  };

  return ws;
}

export function getVideoUrl(filename: string): string {
  return `${API_BASE}/api/videos/${filename}`;
}

// =====================
// TRAINING API
// =====================

export async function startTraining(
  params: TrainingParams
): Promise<TrainingJob> {
  const response = await fetch(`${API_BASE}/api/train`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to start training");
  }

  return response.json();
}

export async function stopTraining(jobId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/train/${jobId}/stop`, {
    method: "POST",
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to stop training");
  }
}

export async function getTrainingStatus(jobId: string): Promise<TrainingJob> {
  const response = await fetch(`${API_BASE}/api/train/${jobId}/status`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to get training status");
  }

  return response.json();
}

export function connectTrainingWebSocket(
  jobId: string,
  onMessage: (update: TrainingProgressUpdate) => void,
  onError?: (error: Event) => void,
  onClose?: () => void
): WebSocket {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const ws = new WebSocket(`${protocol}//${window.location.host}/api/ws/training/${jobId}`);

  ws.onmessage = (event) => {
    try {
      const update = JSON.parse(event.data);
      onMessage(update);
    } catch (e) {
      console.error("Failed to parse WebSocket message:", e);
    }
  };

  ws.onerror = (error) => {
    console.error("WebSocket error:", error);
    onError?.(error);
  };

  ws.onclose = () => {
    onClose?.();
  };

  return ws;
}

export async function listCheckpoints(): Promise<string[]> {
  const response = await fetch(`${API_BASE}/api/checkpoints`);

  if (!response.ok) {
    return [];
  }

  const data = await response.json();
  return data.checkpoints || [];
}

// =====================
// LoRA API
// =====================

export interface LoraItem {
  name: string;
  path: string;
}

export async function listLoras(): Promise<LoraItem[]> {
  const response = await fetch(`${API_BASE}/api/loras`);
  if (!response.ok) {
    return [];
  }
  const data = await response.json();
  return data.loras || [];
}

// =====================
// GALLERY API
// =====================

export async function listVideos(): Promise<GalleryVideo[]> {
  const response = await fetch(`${API_BASE}/api/gallery`);

  if (!response.ok) {
    return [];
  }

  const data = await response.json();
  return data.videos || [];
}

export async function enhancePrompt(request: EnhanceRequest): Promise<EnhanceResponse> {
  const response = await fetch(`${API_BASE}/api/enhance`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Prompt enhancement failed");
  }

  return response.json();
}

export async function getEnhanceModels(
  provider: EnhanceProvider,
  baseUrl?: string
): Promise<EnhanceModelsResponse> {
  const params = new URLSearchParams({ provider });
  if (baseUrl) params.set("base_url", baseUrl);
  const response = await fetch(`${API_BASE}/api/enhance/models?${params.toString()}`);
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `Failed to load ${provider} models. Make sure ${provider === "ollama" ? "Ollama" : "LM Studio"} is running.`);
  }
  return response.json();
}

export async function deleteVideo(videoId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/gallery/${videoId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to delete video");
  }
}

export function getVideoThumbnailUrl(filename: string): string {
  return `${API_BASE}/api/thumbnails/${filename}`;
}
