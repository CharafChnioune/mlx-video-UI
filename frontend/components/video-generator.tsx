"use client";

import { useState, useCallback } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { ModelSelector } from "./model-selector";
import { ParameterPanel } from "./parameter-panel";
import { ConditioningPanel } from "./conditioning-panel";
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
  enhance_prompt: false,
  tiling: "auto",
  cache_limit_gb: 32,
  audio: false,
};

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

  const updateParams = useCallback((updates: Partial<GenerationParams>) => {
    setParams((prev) => ({ ...prev, ...updates }));
  }, []);

  const handleGenerate = async () => {
    if (!params.prompt.trim()) return;

    setStatus("pending");
    setProgress(0);
    setCurrentStep("Starting generation...");
    setError(undefined);
    setVideoPath(undefined);

    try {
      const job = await startGeneration(params);

      const ws = connectWebSocket(
        job.job_id,
        (update: ProgressUpdate) => {
          if (update.type === "progress") {
            setStatus("processing");
            setProgress(update.progress || 0);
            setCurrentStep(update.current_step || "Processing...");
          } else if (update.type === "complete") {
            setStatus("completed");
            setProgress(100);
            setVideoPath(update.output_path);

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

  const loadFromHistory = (item: GenerationHistory) => {
    setParams(item.params);
    if (item.videoPath) {
      setVideoPath(item.videoPath);
      setStatus("completed");
    }
  };

  const isGenerating = status === "processing" || status === "pending";
  const canGenerate = params.prompt.trim() && !isGenerating;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8">
      {/* Left Panel - Controls */}
      <div className="space-y-6">
        {/* Prompt Section */}
        <Card className="glass-card border-border/50 overflow-hidden card-hover">
          {/* Gradient top bar */}
          <div className="h-1 bg-gradient-to-r from-primary via-purple-500 to-blue-500 animate-gradient" />
          <CardContent className="p-6 space-y-5">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label className="text-base font-semibold flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-primary" />
                  Prompt
                </Label>
                <div className="flex items-center gap-2">
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <div className="flex items-center gap-1.5 px-2 py-1 rounded-lg glass border border-border/50">
                        <Switch
                          id="enhance"
                          checked={params.enhance_prompt || false}
                          onCheckedChange={(checked) =>
                            updateParams({ enhance_prompt: checked })
                          }
                          className="data-[state=checked]:bg-primary"
                        />
                        <Label
                          htmlFor="enhance"
                          className="text-xs cursor-pointer flex items-center gap-1"
                        >
                          <Wand2 className="h-3.5 w-3.5" />
                          Enhance
                        </Label>
                      </div>
                    </TooltipTrigger>
                    <TooltipContent>
                      Use AI to enhance your prompt for better results
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

            {/* Enhanced Generate Button */}
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

        {/* Model & Settings Tabs */}
        <Card className="glass-card border-border/50 overflow-hidden">
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="w-full p-1 bg-background/50 rounded-t-lg rounded-b-none border-b border-border/50 h-auto">
              <TabsTrigger
                value="parameters"
                className="flex-1 gap-2 py-2.5 data-[state=active]:bg-primary/10 data-[state=active]:text-primary transition-all"
              >
                <Settings className="h-4 w-4" />
                Parameters
              </TabsTrigger>
              <TabsTrigger
                value="conditioning"
                className="flex-1 gap-2 py-2.5 data-[state=active]:bg-primary/10 data-[state=active]:text-primary transition-all"
              >
                <ImageIcon className="h-4 w-4" />
                Conditioning
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
      </div>
    </div>
  );
}
