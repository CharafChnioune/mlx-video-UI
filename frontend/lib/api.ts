const API_BASE = "";

// =====================
// GENERATION TYPES
// =====================

export interface GenerationParams {
  prompt: string;
  negative_prompt?: string;
  height: number;
  width: number;
  num_frames: number;
  seed: number;
  fps: number;
  pipeline: "distilled" | "dev" | "keyframe" | "ic_lora";
  steps?: number;
  cfg_scale?: number;
  model_repo?: string;
  checkpoint_path?: string;
  enhance_prompt?: boolean;
  tiling?: "auto" | "on" | "off";
  cache_limit_gb?: number;
  audio?: boolean;
  stream?: boolean;
  conditioning_image?: string;
  conditioning_frame_idx?: number;
  conditioning_strength?: number;
  video_conditioning?: string;
  conditioning_mode?: "replace" | "guide";
}

export interface GenerationJob {
  job_id: string;
  status: "pending" | "processing" | "completed" | "error";
  progress?: number;
  current_step?: string;
  output_path?: string;
  error?: string;
}

export interface ProgressUpdate {
  type: "progress" | "status" | "complete" | "error";
  job_id: string;
  progress?: number;
  current_step?: string;
  output_path?: string;
  error?: string;
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
  strategy: "text_to_video" | "video_to_video";
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
  skip_initial_validation: false,

  output_dir: "./training_output",
  seed: 42,

  log_every: 1,
  wandb_enabled: false,
  wandb_project: "ltx-trainer",
};

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

export async function getJobStatus(jobId: string): Promise<GenerationJob> {
  const response = await fetch(`${API_BASE}/api/status/${jobId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to get job status");
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
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const ws = new WebSocket(`${protocol}//${window.location.host}/ws/progress/${jobId}`);

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
  const ws = new WebSocket(`${protocol}//${window.location.host}/ws/training/${jobId}`);

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
