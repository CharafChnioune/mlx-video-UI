"use client";

import { useState, useCallback, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { ModelSelector } from "./model-selector";
import { ParameterPanel } from "./parameter-panel";
import { ConditioningPanel } from "./conditioning-panel";
import { LoraPanel } from "./lora-panel";
import { ProgressIndicator } from "./progress-indicator";
import { VideoPreview } from "./video-preview";
import {
  Sparkles,
  Wand2,
  Info,
  Settings,
  ImageIcon,
  History,
  Loader2,
} from "lucide-react";
import {
  startGeneration,
  connectWebSocket,
  type GenerationParams,
  type ProgressUpdate,
  getDefaultSettings,
  getHardwareInfo,
  type HardwareInfo,
  enhancePrompt,
  getJobStatus,
  getEnhanceModels,
  type EnhanceProvider,
} from "@/lib/api";

const defaultParams: GenerationParams = {
  prompt: "",
  negative_prompt: "",
  height: 512,
  width: 512,
  num_frames: 33,
  seed: 42,
  fps: 24,
  pipeline: "distilled",
  steps: 40,
  cfg_scale: 4.0,
  model_repo: "AITRADER/ltx2-distilled-4bit-mlx",
  auto_output_name: false,
  tiling: "auto",
  cache_limit_gb: 32,
  memory_limit_gb: undefined,
  audio: true,
  stream: true,
  mem_log: false,
  clear_cache: false,
  loras: [],
  distilled_loras: [],
};

const sanitizeParams = (raw: Partial<GenerationParams>): GenerationParams => {
  const allowed = Object.keys(defaultParams) as (keyof GenerationParams)[];
  const cleaned: Partial<GenerationParams> = {};
  for (const key of allowed) {
    if (key in raw) {
      cleaned[key] = raw[key];
    }
  }
  return { ...defaultParams, ...cleaned };
};

const STORAGE_KEY = "mlx-video-ui:params:v1";
const HISTORY_KEY = "mlx-video-ui:history:v1";
const TAB_KEY = "mlx-video-ui:tab:v1";
const LAST_JOB_KEY = "mlx-video-ui:last-job:v1";
const ENHANCE_KEY = "mlx-video-ui:enhance:v1";

interface GenerationHistory {
  id: string;
  params: GenerationParams;
  videoPath?: string;
  timestamp: Date;
}

export function VideoGenerator() {
  const [params, setParams] = useState<GenerationParams>(defaultParams);
  const [status, setStatus] = useState<
    "idle" | "pending" | "processing" | "completed" | "error"
  >("idle");
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState("");
  const [error, setError] = useState<string | undefined>();
  const [videoPath, setVideoPath] = useState<string | undefined>();
  const [history, setHistory] = useState<GenerationHistory[]>([]);
  const [activeTab, setActiveTab] = useState("parameters");
  const [hardware, setHardware] = useState<HardwareInfo | null>(null);
  const [defaultsApplied, setDefaultsApplied] = useState(false);
  const [isEnhancing, setIsEnhancing] = useState(false);
  const [enhanceError, setEnhanceError] = useState<string | null>(null);
  const [enhanceProvider, setEnhanceProvider] = useState<EnhanceProvider>("local");
  const [enhanceBaseUrl, setEnhanceBaseUrl] = useState<string>("http://127.0.0.1:11434");
  const [enhanceModels, setEnhanceModels] = useState<string[]>([]);
  const [enhanceModel, setEnhanceModel] = useState<string>("");

  const enhanceDefaults: Record<EnhanceProvider, string> = {
    local: "",
    ollama: "http://127.0.0.1:11434",
    lmstudio: "http://127.0.0.1:1234",
  };
  const [storageLoaded, setStorageLoaded] = useState(false);

  const updateParams = useCallback((updates: Partial<GenerationParams>) => {
    setParams((prev) => ({ ...prev, ...updates }));
  }, []);

  useEffect(() => {
    if (storageLoaded) return;
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved) as GenerationParams;
        setParams(sanitizeParams(parsed));
      }
      const savedHistory = localStorage.getItem(HISTORY_KEY);
      if (savedHistory) {
        const parsedHistory = JSON.parse(savedHistory) as GenerationHistory[];
        setHistory(parsedHistory.map((item) => ({ ...item, timestamp: new Date(item.timestamp) })));
      }
      const savedTab = localStorage.getItem(TAB_KEY);
      if (savedTab) {
        setActiveTab(savedTab);
      }
      const savedEnhance = localStorage.getItem(ENHANCE_KEY);
      if (savedEnhance) {
        const parsed = JSON.parse(savedEnhance) as {
          provider?: EnhanceProvider;
          baseUrl?: string;
          model?: string;
        };
        if (parsed.provider) setEnhanceProvider(parsed.provider);
        if (parsed.baseUrl) setEnhanceBaseUrl(parsed.baseUrl);
        if (parsed.model) setEnhanceModel(parsed.model);
      }
    } catch {
      // ignore storage errors
    } finally {
      setStorageLoaded(true);
    }
  }, [storageLoaded]);

  useEffect(() => {
    const loadDefaults = async () => {
      try {
        const defaults = await getDefaultSettings();
        const hw = await getHardwareInfo();
        setHardware(hw);
        if (!defaultsApplied && !storageLoaded) {
          setParams((prev) => ({ ...prev, ...defaults.generation }));
          setDefaultsApplied(true);
        }
      } catch {
        // ignore
      }
    };
    loadDefaults();
  }, [defaultsApplied, storageLoaded]);

  useEffect(() => {
    if (!storageLoaded) return;
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(params));
    } catch {
      // ignore
    }
  }, [params, storageLoaded]);

  useEffect(() => {
    if (!storageLoaded) return;
    try {
      localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
    } catch {
      // ignore
    }
  }, [history, storageLoaded]);

  useEffect(() => {
    if (!storageLoaded) return;
    try {
      localStorage.setItem(TAB_KEY, activeTab);
    } catch {
      // ignore
    }
  }, [activeTab, storageLoaded]);

  useEffect(() => {
    if (!storageLoaded) return;
    try {
      localStorage.setItem(
        ENHANCE_KEY,
        JSON.stringify({
          provider: enhanceProvider,
          baseUrl: enhanceBaseUrl,
          model: enhanceModel,
        })
      );
    } catch {
      // ignore
    }
  }, [enhanceProvider, enhanceBaseUrl, enhanceModel, storageLoaded]);

  useEffect(() => {
    if (params.pipeline !== "distilled" && params.distilled_loras?.length) {
      updateParams({ distilled_loras: [] });
    }
    if (params.pipeline !== "ic_lora" && params.video_conditioning) {
      updateParams({ video_conditioning: undefined });
    }
  }, [params.pipeline, params.distilled_loras, params.video_conditioning, updateParams]);

  useEffect(() => {
    // Reset base URL when switching providers
    if (enhanceProvider === "local") return;
    setEnhanceBaseUrl(enhanceDefaults[enhanceProvider]);
  }, [enhanceProvider]);

  useEffect(() => {
    let cancelled = false;
    const loadModels = async () => {
      setEnhanceError(null);
      if (enhanceProvider === "local") {
        if (!cancelled) {
          setEnhanceModels(["bundled"]);
          setEnhanceModel("bundled");
        }
        return;
      }
      const baseUrl = enhanceBaseUrl.trim() || enhanceDefaults[enhanceProvider];
      try {
        const result = await getEnhanceModels(enhanceProvider, baseUrl);
        if (cancelled) return;
        setEnhanceModels(result.models || []);
        if (!result.models?.includes(enhanceModel)) {
          setEnhanceModel(result.models?.[0] || "");
        }
      } catch (e) {
        if (!cancelled) {
          setEnhanceModels([]);
          setEnhanceModel("");
          setEnhanceError(e instanceof Error ? e.message : "Failed to load models");
        }
      }
    };
    loadModels();
    return () => {
      cancelled = true;
    };
  }, [enhanceProvider, enhanceBaseUrl]);

  useEffect(() => {
    if (!storageLoaded) return;
    const resumeLastJob = async () => {
      const lastJob = localStorage.getItem(LAST_JOB_KEY);
      if (!lastJob) return;
      try {
        const status = await getJobStatus(lastJob);
        setStatus(status.status);
        setProgress(status.progress || 0);
        setCurrentStep(status.current_step || "");
        setError(status.error);
        if (status.output_path) {
          setVideoPath(status.output_path);
        }

        if (status.status === "processing" || status.status === "pending") {
          connectWebSocket(
            lastJob,
            (update: ProgressUpdate) => {
              if (update.type === "progress") {
                setStatus("processing");
                setProgress(update.progress || 0);
                setCurrentStep(update.current_step || "Processing...");
                if (update.output_path) {
                  setVideoPath(update.output_path);
                }
              } else if (update.type === "complete") {
                setStatus("completed");
                setProgress(100);
                setVideoPath(update.output_path);
                localStorage.removeItem(LAST_JOB_KEY);
              } else if (update.type === "error") {
                setStatus("error");
                setError(update.error);
                localStorage.removeItem(LAST_JOB_KEY);
              }
            },
            () => setError("Connection lost"),
            () => {}
          );
        }
      } catch {
        localStorage.removeItem(LAST_JOB_KEY);
      }
    };
    resumeLastJob();
  }, [storageLoaded]);

  const handleGenerate = async () => {
    if (!params.prompt.trim()) return;

    setStatus("pending");
    setProgress(0);
    setCurrentStep("Starting generation...");
    setError(undefined);
    setVideoPath(undefined);

    try {
      const job = await startGeneration(params);
      try {
        localStorage.setItem(LAST_JOB_KEY, job.job_id);
      } catch {
        // ignore
      }

      const ws = connectWebSocket(
        job.job_id,
        (update: ProgressUpdate) => {
          if (update.type === "progress") {
            setStatus("processing");
            setProgress(update.progress || 0);
            setCurrentStep(update.current_step || "Processing...");
            if (update.output_path) {
              setVideoPath(update.output_path);
            }
          } else if (update.type === "complete") {
            setStatus("completed");
            setProgress(100);
            setVideoPath(update.output_path);
            try {
              localStorage.removeItem(LAST_JOB_KEY);
            } catch {
              // ignore
            }

            // Add to history
            setHistory((prev) => [
              {
                id: job.job_id,
                params: { ...params },
                videoPath: update.output_path,
                timestamp: new Date(),
              },
              ...prev.slice(0, 9),
            ]);
          } else if (update.type === "error") {
            setStatus("error");
            setError(update.error);
            try {
              localStorage.removeItem(LAST_JOB_KEY);
            } catch {
              // ignore
            }
          }
        },
        () => setError("Connection lost"),
        () => {}
      );

      return () => ws.close();
    } catch (e) {
      setStatus("error");
      setError(e instanceof Error ? e.message : "Failed to start generation");
    }
  };

  const runEnhance = async () => {
    if (!params.prompt.trim() || isEnhancing) return;
    if (enhanceProvider !== "local" && !enhanceModel) {
      setEnhanceError("Select an enhancer model first.");
      return;
    }
    setIsEnhancing(true);
    setEnhanceError(null);
    try {
      const baseUrl =
        enhanceProvider === "local"
          ? undefined
          : enhanceBaseUrl.trim() || enhanceDefaults[enhanceProvider];
      const result = await enhancePrompt({
        prompt: params.prompt,
        provider: enhanceProvider,
        model: enhanceProvider === "local" ? undefined : enhanceModel || undefined,
        base_url: baseUrl,
      });
      updateParams({
        prompt: result.enhanced,
      });
    } catch (e) {
      setEnhanceError(e instanceof Error ? e.message : "Prompt enhancement failed");
    } finally {
      setIsEnhancing(false);
    }
  };

  const loadFromHistory = (item: GenerationHistory) => {
    setParams(item.params);
    if (item.videoPath) {
      setVideoPath(item.videoPath);
      setStatus("completed");
    }
  };

  const isGenerating = status === "processing" || status === "pending";
  const missingVideo = params.pipeline === "ic_lora" && !params.video_conditioning;
  const missingImage = params.pipeline === "keyframe" && !params.conditioning_image;
  const canGenerate =
    params.prompt.trim() &&
    !isGenerating &&
    !isEnhancing &&
    !missingVideo &&
    !missingImage;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8">
      {/* Left Panel - Controls */}
      <div className="space-y-6">
        {/* Step 1: Prompt */}
        <Card className="glass-card border-border/50 overflow-hidden card-hover">
          {/* Gradient top bar */}
          <div className="h-1 bg-gradient-to-r from-primary via-purple-500 to-blue-500 animate-gradient" />
          <CardContent className="p-6 space-y-5">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label className="text-base font-semibold flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-primary" />
                  Step 1: Prompt
                </Label>
                <div className="flex flex-wrap items-center gap-2">
                  <Select
                    value={enhanceProvider}
                    onValueChange={(val) => setEnhanceProvider(val as EnhanceProvider)}
                  >
                    <SelectTrigger className="h-8 glass border-border/50">
                      <SelectValue placeholder="Enhancer" />
                    </SelectTrigger>
                    <SelectContent className="glass-card border-border/50">
                      <SelectItem value="local">Local Gemma (bundled)</SelectItem>
                      <SelectItem value="ollama">Ollama (local)</SelectItem>
                      <SelectItem value="lmstudio">LM Studio (local)</SelectItem>
                    </SelectContent>
                  </Select>

                  {enhanceProvider !== "local" && (
                    <Input
                      value={enhanceBaseUrl}
                      onChange={(e) => setEnhanceBaseUrl(e.target.value)}
                      placeholder="Base URL"
                      className="h-8 w-[200px] text-xs font-mono"
                    />
                  )}

                  <Select
                    value={enhanceModel}
                    onValueChange={(val) => setEnhanceModel(val)}
                    disabled={enhanceProvider !== "local" && enhanceModels.length === 0}
                  >
                    <SelectTrigger className="h-8 glass border-border/50 min-w-[200px]">
                      <SelectValue
                        placeholder={
                          enhanceProvider === "local"
                            ? "Bundled"
                            : enhanceModels.length
                            ? "Select model"
                            : "No models found"
                        }
                      />
                    </SelectTrigger>
                    <SelectContent className="glass-card border-border/50">
                      {(enhanceModels.length ? enhanceModels : ["bundled"]).map((model) => (
                        <SelectItem key={model} value={model} className="focus:bg-primary/10">
                          {model}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>

                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        size="sm"
                        className="h-8"
                        onClick={runEnhance}
                        disabled={isEnhancing || !params.prompt.trim()}
                      >
                        {isEnhancing ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <Wand2 className="h-4 w-4" />
                        )}
                        Enhance
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                      Enhance the prompt and insert the result for review
                    </TooltipContent>
                  </Tooltip>
                </div>
              </div>
              <div className="relative">
                <Textarea
                  placeholder="Describe the video you want to generate..."
                  value={params.prompt}
                  onChange={(e) => updateParams({ prompt: e.target.value })}
                  className="min-h-[120px] bg-background/50 border-border/50 resize-none text-base focus:border-primary/50 focus:ring-primary/20 transition-all"
                />
                {/* Character count */}
                <div className="absolute bottom-2 right-2 text-xs text-muted-foreground/50">
                  {params.prompt.length} chars
                </div>
              </div>
              {isEnhancing && (
                <p className="text-xs text-muted-foreground flex items-center gap-2">
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  Enhancing prompt...
                </p>
              )}
              {enhanceError && (
                <p className="text-xs text-red-400">{enhanceError}</p>
              )}
            </div>

            {params.pipeline === "dev" && (
              <div className="space-y-2">
                <Label className="text-sm text-muted-foreground">
                  Negative Prompt
                </Label>
                <Textarea
                  placeholder="What to avoid in the video..."
                  value={params.negative_prompt || ""}
                  onChange={(e) =>
                    updateParams({ negative_prompt: e.target.value })
                  }
                  className="min-h-[60px] bg-background/50 border-border/50 resize-none text-sm focus:border-primary/50 transition-all"
                />
              </div>
            )}

          </CardContent>
        </Card>

        {hardware && (
          <Card className="glass-card border-border/50">
            <CardContent className="p-4 text-xs text-muted-foreground space-y-1">
              <div className="flex items-center justify-between">
                <span>Hardware</span>
                <span className="font-medium text-foreground">{hardware.cpu}</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Memory</span>
                <span className="font-medium text-foreground">{hardware.memory_gb} GB</span>
              </div>
              <div className="flex items-center justify-between">
                <span>MLX</span>
                <span className="font-medium text-foreground">{hardware.mlx_version || "unknown"}</span>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 2: Model & Settings */}
        <Card className="glass-card border-border/50 overflow-hidden">
          <div className="px-6 pt-6 pb-2">
            <Label className="text-sm font-semibold">Step 2–4: Configure</Label>
            <p className="text-xs text-muted-foreground mt-1">
              Select pipeline/model, add conditioning, and LoRAs.
            </p>
          </div>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="w-full p-1 bg-background/50 rounded-t-lg rounded-b-none border-b border-border/50 h-auto">
              <TabsTrigger
                value="parameters"
                className="flex-1 gap-2 py-2.5 data-[state=active]:bg-primary/10 data-[state=active]:text-primary transition-all"
              >
                <Settings className="h-4 w-4" />
                Step 2: Parameters
              </TabsTrigger>
              <TabsTrigger
                value="conditioning"
                className="flex-1 gap-2 py-2.5 data-[state=active]:bg-primary/10 data-[state=active]:text-primary transition-all"
              >
                <ImageIcon className="h-4 w-4" />
                Step 3: Conditioning
              </TabsTrigger>
              <TabsTrigger
                value="lora"
                className="flex-1 gap-2 py-2.5 data-[state=active]:bg-primary/10 data-[state=active]:text-primary transition-all"
              >
                <Sparkles className="h-4 w-4" />
                Step 4: LoRA
              </TabsTrigger>
              <TabsTrigger
                value="history"
                className="flex-1 gap-2 py-2.5 data-[state=active]:bg-primary/10 data-[state=active]:text-primary transition-all"
              >
                <History className="h-4 w-4" />
                History
              </TabsTrigger>
            </TabsList>

            <CardContent className="p-6">
              <TabsContent value="parameters" className="mt-0 space-y-6">
                <ModelSelector
                  pipeline={params.pipeline}
                  onPipelineChange={(v) =>
                    updateParams({
                      pipeline: v as GenerationParams["pipeline"],
                    })
                  }
                  modelRepo={params.model_repo || ""}
                  onModelRepoChange={(v) => updateParams({ model_repo: v })}
                />
                <div className="h-px bg-gradient-to-r from-transparent via-border to-transparent" />
                <ParameterPanel params={params} onParamsChange={updateParams} />
              </TabsContent>

              <TabsContent value="conditioning" className="mt-0">
                <ConditioningPanel
                  params={params}
                  onParamsChange={updateParams}
                />
              </TabsContent>

              <TabsContent value="lora" className="mt-0">
                <LoraPanel params={params} onParamsChange={updateParams} />
              </TabsContent>

              <TabsContent value="history" className="mt-0">
                {history.length > 0 ? (
                  <div className="space-y-3">
                    {history.map((item, index) => (
                      <button
                        key={item.id}
                        onClick={() => loadFromHistory(item)}
                        className="w-full p-4 rounded-xl glass border border-border/50 hover:border-primary/30 hover:bg-primary/5 transition-all duration-300 text-left group"
                        style={{ animationDelay: `${index * 50}ms` }}
                      >
                        <p className="text-sm font-medium line-clamp-2 group-hover:text-primary transition-colors">
                          {item.params.prompt}
                        </p>
                        <p className="text-xs text-muted-foreground mt-2 flex items-center gap-2">
                          <span className="px-1.5 py-0.5 rounded bg-secondary/50">
                            {item.params.width}x{item.params.height}
                          </span>
                          <span>&middot;</span>
                          <span>{item.params.num_frames} frames</span>
                          <span>&middot;</span>
                          <span>{new Date(item.timestamp).toLocaleTimeString()}</span>
                        </p>
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
                    <div className="w-16 h-16 rounded-2xl glass-card border border-border/50 flex items-center justify-center mb-4">
                      <History className="h-8 w-8 opacity-30" />
                    </div>
                    <p className="text-sm font-medium">No generation history yet</p>
                    <p className="text-xs text-muted-foreground/70 mt-1">Your generated videos will appear here</p>
                  </div>
                )}
              </TabsContent>
            </CardContent>
          </Tabs>
        </Card>
      </div>

      {/* Right Panel - Preview & Progress */}
      <div className="space-y-6">
        <Card className="glass-card border-border/50 overflow-hidden card-hover">
          <div className="h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-primary animate-gradient" />
          <CardContent className="p-6">
            <Label className="text-base font-semibold mb-4 flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
              Preview
            </Label>
            <VideoPreview
              videoPath={videoPath}
              isGenerating={isGenerating}
            />
          </CardContent>
        </Card>

        {status !== "idle" && (
          <ProgressIndicator
            status={status}
            progress={progress}
            currentStep={currentStep}
            error={error}
          />
        )}

        {/* Quick Info */}
        <Card className="glass-card border-border/50 overflow-hidden">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-xl glass border border-primary/20 flex items-center justify-center shrink-0">
                <Info className="h-5 w-5 text-primary" />
              </div>
              <div className="space-y-1 flex-1">
                <p className="text-sm font-medium">Generation Info</p>
                <div className="flex flex-wrap gap-2">
                  <span className="px-2 py-0.5 rounded-md bg-secondary/50 text-xs text-muted-foreground">
                    {params.width}x{params.height}
                  </span>
                  <span className="px-2 py-0.5 rounded-md bg-secondary/50 text-xs text-muted-foreground">
                    {params.num_frames} frames
                  </span>
                  <span className="px-2 py-0.5 rounded-md bg-secondary/50 text-xs text-muted-foreground">
                    {((params.num_frames - 1) / params.fps).toFixed(1)}s
                  </span>
                  <span className="px-2 py-0.5 rounded-md bg-primary/10 text-xs text-primary">
                    {params.pipeline}
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
        {/* Step 5: Generate */}
        <Card className="glass-card border-border/50">
          <CardContent className="p-6 space-y-4">
            <Label className="text-sm font-medium">Step 5: Generate</Label>
            {missingVideo && (
              <p className="text-xs text-amber-400">
                IC-LoRA requires a conditioning video. Upload one in the Conditioning tab.
              </p>
            )}
            {missingImage && (
              <p className="text-xs text-amber-400">
                Keyframe requires a conditioning image. Upload one in the Conditioning tab.
              </p>
            )}
            <Button
              onClick={handleGenerate}
              disabled={!canGenerate}
              className={`
                w-full h-14 text-base font-semibold relative overflow-hidden
                bg-gradient-to-r from-primary via-purple-600 to-primary
                hover:from-primary/90 hover:via-purple-600/90 hover:to-primary/90
                disabled:from-muted disabled:via-muted disabled:to-muted
                transition-all duration-300
                ${canGenerate ? 'glow-primary-intense btn-shine btn-shine-active animate-glow-pulse' : ''}
              `}
            >
              {isGenerating ? (
                <>
                  <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="h-5 w-5 mr-2" />
                  Generate Video
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
