"use client";

import { useState, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  ChevronDown,
  GraduationCap,
  Cpu,
  Layers,
  Zap,
  Database,
  Settings2,
  Save,
  Play,
  Square,
  Loader2,
  FolderOpen,
  Info,
  Sparkles,
  Video,
  RefreshCw,
  CheckCircle2,
  XCircle,
  TrendingDown,
} from "lucide-react";
import {
  type TrainingParams,
  type TrainingJob,
  type TrainingProgressUpdate,
  defaultTrainingParams,
  startTraining,
  stopTraining,
  connectTrainingWebSocket,
} from "@/lib/api";

const trainingModes = [
  {
    value: "lora",
    label: "LoRA",
    description: "Low-Rank Adaptation - efficient fine-tuning",
    icon: Layers,
  },
  {
    value: "full",
    label: "Full",
    description: "Full model fine-tuning - more VRAM required",
    icon: Cpu,
  },
];

const strategies = [
  {
    value: "text_to_video",
    label: "Text to Video",
    description: "Train on text-video pairs",
    icon: Video,
  },
  {
    value: "video_to_video",
    label: "Video to Video",
    description: "IC-LoRA style conditioning",
    icon: RefreshCw,
  },
];

const optimizers = [
  { value: "adamw", label: "AdamW", description: "Standard optimizer" },
  { value: "adamw8bit", label: "AdamW 8-bit", description: "Memory efficient" },
];

const schedulers = [
  { value: "constant", label: "Constant" },
  { value: "linear", label: "Linear" },
  { value: "cosine", label: "Cosine" },
  { value: "cosine_with_restarts", label: "Cosine with Restarts" },
  { value: "polynomial", label: "Polynomial" },
];

const precisionModes = [
  { value: "bf16", label: "BFloat16", description: "Recommended" },
  { value: "fp16", label: "Float16", description: "Legacy" },
  { value: "no", label: "Float32", description: "High precision" },
];

const loraTargetModules = [
  { value: "to_k", label: "to_k", description: "Key projections" },
  { value: "to_q", label: "to_q", description: "Query projections" },
  { value: "to_v", label: "to_v", description: "Value projections" },
  { value: "to_out.0", label: "to_out.0", description: "Output projections" },
  { value: "ff.net.0.proj", label: "ff.net.0.proj", description: "FFN input" },
  { value: "ff.net.2", label: "ff.net.2", description: "FFN output" },
];

export function TrainingForm() {
  const [params, setParams] = useState<TrainingParams>(defaultTrainingParams);
  const [status, setStatus] = useState<TrainingJob["status"]>("pending");
  const [currentStep, setCurrentStep] = useState(0);
  const [totalSteps, setTotalSteps] = useState(0);
  const [currentLoss, setCurrentLoss] = useState<number | null>(null);
  const [eta, setEta] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [validationOpen, setValidationOpen] = useState(false);
  const [loraOpen, setLoraOpen] = useState(true);

  const updateParams = useCallback((updates: Partial<TrainingParams>) => {
    setParams((prev) => ({ ...prev, ...updates }));
  }, []);

  const handleStartTraining = async () => {
    if (!params.data_root) {
      setError("Please specify a data root directory");
      return;
    }

    setStatus("pending");
    setError(null);
    setCurrentStep(0);
    setCurrentLoss(null);

    try {
      const job = await startTraining(params);
      setJobId(job.job_id);
      setTotalSteps(params.steps);

      const ws = connectTrainingWebSocket(
        job.job_id,
        (update: TrainingProgressUpdate) => {
          if (update.type === "progress") {
            setStatus("training");
            setCurrentStep(update.step || 0);
            setCurrentLoss(update.loss || null);
            setEta(update.eta || null);
          } else if (update.type === "complete") {
            setStatus("completed");
          } else if (update.type === "error") {
            setStatus("error");
            setError(update.error || "Training failed");
          }
        },
        () => setError("Connection lost"),
        () => {}
      );

      return () => ws.close();
    } catch (e) {
      setStatus("error");
      setError(e instanceof Error ? e.message : "Failed to start training");
    }
  };

  const handleStopTraining = async () => {
    if (jobId) {
      try {
        await stopTraining(jobId);
        setStatus("stopped");
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to stop training");
      }
    }
  };

  const toggleLoraModule = (module: string) => {
    const current = params.lora_target_modules;
    if (current.includes(module)) {
      updateParams({ lora_target_modules: current.filter((m) => m !== module) });
    } else {
      updateParams({ lora_target_modules: [...current, module] });
    }
  };

  const isTraining = status === "training" || status === "pending";
  const progress = totalSteps > 0 ? (currentStep / totalSteps) * 100 : 0;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Left Panel - Main Settings */}
      <div className="lg:col-span-2 space-y-6">
        {/* Training Mode & Strategy */}
        <Card className="glass-card border-border/50 overflow-hidden">
          <div className="h-1 bg-gradient-to-r from-green-500 via-emerald-500 to-teal-500 animate-gradient" />
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 text-lg">
              <GraduationCap className="h-5 w-5 text-primary" />
              Training Configuration
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Training Mode */}
            <div className="space-y-3">
              <Label className="text-sm font-medium flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                Training Mode
              </Label>
              <div className="grid grid-cols-2 gap-3">
                {trainingModes.map((mode) => {
                  const Icon = mode.icon;
                  const isSelected = params.training_mode === mode.value;
                  return (
                    <button
                      key={mode.value}
                      onClick={() => updateParams({ training_mode: mode.value as "lora" | "full" })}
                      disabled={isTraining}
                      className={`
                        relative flex flex-col items-start p-4 rounded-xl border transition-all duration-300
                        ${isSelected
                          ? "border-primary/50 glass-intense glow-primary"
                          : "border-border/50 glass hover:border-primary/30"
                        }
                        ${isTraining ? "opacity-50 cursor-not-allowed" : ""}
                      `}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <Icon className={`h-4 w-4 ${isSelected ? "text-primary" : "text-muted-foreground"}`} />
                        <span className={`font-medium ${isSelected ? "text-primary" : ""}`}>{mode.label}</span>
                      </div>
                      <span className="text-xs text-muted-foreground">{mode.description}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Strategy */}
            <div className="space-y-3">
              <Label className="text-sm font-medium flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-primary" />
                Training Strategy
              </Label>
              <div className="grid grid-cols-2 gap-3">
                {strategies.map((strategy) => {
                  const Icon = strategy.icon;
                  const isSelected = params.strategy === strategy.value;
                  const isDisabled = strategy.value === "video_to_video" && params.training_mode === "full";
                  return (
                    <Tooltip key={strategy.value}>
                      <TooltipTrigger asChild>
                        <button
                          onClick={() => updateParams({ strategy: strategy.value as "text_to_video" | "video_to_video" })}
                          disabled={isTraining || isDisabled}
                          className={`
                            relative flex flex-col items-start p-4 rounded-xl border transition-all duration-300
                            ${isSelected
                              ? "border-primary/50 glass-intense glow-primary"
                              : "border-border/50 glass hover:border-primary/30"
                            }
                            ${isTraining || isDisabled ? "opacity-50 cursor-not-allowed" : ""}
                          `}
                        >
                          <div className="flex items-center gap-2 mb-1">
                            <Icon className={`h-4 w-4 ${isSelected ? "text-primary" : "text-muted-foreground"}`} />
                            <span className={`font-medium ${isSelected ? "text-primary" : ""}`}>{strategy.label}</span>
                          </div>
                          <span className="text-xs text-muted-foreground">{strategy.description}</span>
                        </button>
                      </TooltipTrigger>
                      {isDisabled && (
                        <TooltipContent>Video-to-video requires LoRA training mode</TooltipContent>
                      )}
                    </Tooltip>
                  );
                })}
              </div>
            </div>

            {/* Audio Toggle */}
            <div className="flex items-center justify-between p-4 rounded-xl glass border border-border/50">
              <div className="flex items-center gap-3">
                <div className="p-1.5 rounded-lg bg-primary/10">
                  <Sparkles className="h-4 w-4 text-primary" />
                </div>
                <div>
                  <Label className="text-sm">Audio Training</Label>
                  <p className="text-xs text-muted-foreground">Joint audio-video training</p>
                </div>
              </div>
              <Switch
                checked={params.with_audio}
                onCheckedChange={(checked) => updateParams({ with_audio: checked })}
                disabled={isTraining || params.strategy === "video_to_video"}
              />
            </div>
          </CardContent>
        </Card>

        {/* LoRA Configuration */}
        {params.training_mode === "lora" && (
          <Collapsible open={loraOpen} onOpenChange={setLoraOpen}>
            <Card className="glass-card border-border/50 overflow-hidden">
              <CollapsibleTrigger asChild>
                <CardHeader className="cursor-pointer hover:bg-primary/5 transition-colors">
                  <CardTitle className="flex items-center justify-between text-lg">
                    <span className="flex items-center gap-2">
                      <Layers className="h-5 w-5 text-primary" />
                      LoRA Configuration
                    </span>
                    <ChevronDown className={`h-4 w-4 transition-transform ${loraOpen ? "rotate-180" : ""}`} />
                  </CardTitle>
                </CardHeader>
              </CollapsibleTrigger>
              <CollapsibleContent>
                <CardContent className="space-y-6 pt-0">
                  {/* Rank and Alpha */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <Label className="text-xs text-muted-foreground">Rank</Label>
                        <span className="text-xs font-mono text-primary px-2 py-0.5 rounded bg-primary/10">{params.lora_rank}</span>
                      </div>
                      <Slider
                        value={[params.lora_rank]}
                        onValueChange={([v]) => updateParams({ lora_rank: v })}
                        min={4}
                        max={128}
                        step={4}
                        disabled={isTraining}
                      />
                    </div>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <Label className="text-xs text-muted-foreground">Alpha</Label>
                        <span className="text-xs font-mono text-primary px-2 py-0.5 rounded bg-primary/10">{params.lora_alpha}</span>
                      </div>
                      <Slider
                        value={[params.lora_alpha]}
                        onValueChange={([v]) => updateParams({ lora_alpha: v })}
                        min={4}
                        max={128}
                        step={4}
                        disabled={isTraining}
                      />
                    </div>
                  </div>

                  {/* Dropout */}
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <Label className="text-xs text-muted-foreground">Dropout</Label>
                      <span className="text-xs font-mono text-primary px-2 py-0.5 rounded bg-primary/10">{params.lora_dropout}</span>
                    </div>
                    <Slider
                      value={[params.lora_dropout]}
                      onValueChange={([v]) => updateParams({ lora_dropout: v })}
                      min={0}
                      max={0.5}
                      step={0.05}
                      disabled={isTraining}
                    />
                  </div>

                  {/* Target Modules */}
                  <div className="space-y-3">
                    <Label className="text-sm font-medium">Target Modules</Label>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                      {loraTargetModules.map((module) => {
                        const isSelected = params.lora_target_modules.includes(module.value);
                        return (
                          <button
                            key={module.value}
                            onClick={() => toggleLoraModule(module.value)}
                            disabled={isTraining}
                            className={`
                              px-3 py-2 text-xs rounded-lg border transition-all
                              ${isSelected
                                ? "border-primary/50 bg-primary/10 text-primary"
                                : "border-border/50 glass text-muted-foreground hover:border-primary/30"
                              }
                              ${isTraining ? "opacity-50 cursor-not-allowed" : ""}
                            `}
                          >
                            {module.label}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                </CardContent>
              </CollapsibleContent>
            </Card>
          </Collapsible>
        )}

        {/* Optimization Settings */}
        <Card className="glass-card border-border/50 overflow-hidden">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Zap className="h-5 w-5 text-primary" />
              Optimization
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Steps and Learning Rate */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-xs text-muted-foreground">Training Steps</Label>
                <Input
                  type="number"
                  value={params.steps}
                  onChange={(e) => updateParams({ steps: parseInt(e.target.value) || 1000 })}
                  disabled={isTraining}
                  className="glass border-border/50"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-xs text-muted-foreground">Learning Rate</Label>
                <Input
                  type="text"
                  value={params.learning_rate}
                  onChange={(e) => updateParams({ learning_rate: parseFloat(e.target.value) || 5e-4 })}
                  disabled={isTraining}
                  className="glass border-border/50 font-mono"
                />
              </div>
            </div>

            {/* Batch Size and Gradient Accumulation */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Label className="text-xs text-muted-foreground">Batch Size</Label>
                  <span className="text-xs font-mono text-primary px-2 py-0.5 rounded bg-primary/10">{params.batch_size}</span>
                </div>
                <Slider
                  value={[params.batch_size]}
                  onValueChange={([v]) => updateParams({ batch_size: v })}
                  min={1}
                  max={8}
                  step={1}
                  disabled={isTraining}
                />
              </div>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Label className="text-xs text-muted-foreground">Gradient Accumulation</Label>
                  <span className="text-xs font-mono text-primary px-2 py-0.5 rounded bg-primary/10">{params.gradient_accumulation_steps}</span>
                </div>
                <Slider
                  value={[params.gradient_accumulation_steps]}
                  onValueChange={([v]) => updateParams({ gradient_accumulation_steps: v })}
                  min={1}
                  max={16}
                  step={1}
                  disabled={isTraining}
                />
              </div>
            </div>

            {/* Optimizer and Scheduler */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-xs text-muted-foreground">Optimizer</Label>
                <Select
                  value={params.optimizer_type}
                  onValueChange={(v) => updateParams({ optimizer_type: v as "adamw" | "adamw8bit" })}
                  disabled={isTraining}
                >
                  <SelectTrigger className="glass border-border/50">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="glass-card">
                    {optimizers.map((opt) => (
                      <SelectItem key={opt.value} value={opt.value}>
                        <span className="font-medium">{opt.label}</span>
                        <span className="text-xs text-muted-foreground ml-2">{opt.description}</span>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label className="text-xs text-muted-foreground">Scheduler</Label>
                <Select
                  value={params.scheduler_type}
                  onValueChange={(v) => updateParams({ scheduler_type: v as TrainingParams["scheduler_type"] })}
                  disabled={isTraining}
                >
                  <SelectTrigger className="glass border-border/50">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="glass-card">
                    {schedulers.map((sched) => (
                      <SelectItem key={sched.value} value={sched.value}>
                        {sched.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Gradient Checkpointing */}
            <div className="flex items-center justify-between p-4 rounded-xl glass border border-border/50">
              <div className="flex items-center gap-3">
                <div className="p-1.5 rounded-lg bg-primary/10">
                  <Save className="h-4 w-4 text-primary" />
                </div>
                <div>
                  <Label className="text-sm">Gradient Checkpointing</Label>
                  <p className="text-xs text-muted-foreground">Trade speed for memory</p>
                </div>
              </div>
              <Switch
                checked={params.enable_gradient_checkpointing}
                onCheckedChange={(checked) => updateParams({ enable_gradient_checkpointing: checked })}
                disabled={isTraining}
              />
            </div>
          </CardContent>
        </Card>

        {/* Data Configuration */}
        <Card className="glass-card border-border/50 overflow-hidden">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Database className="h-5 w-5 text-primary" />
              Data Configuration
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label className="text-sm font-medium flex items-center gap-2">
                Data Root Directory
                <Tooltip>
                  <TooltipTrigger>
                    <Info className="h-3.5 w-3.5 text-muted-foreground" />
                  </TooltipTrigger>
                  <TooltipContent className="max-w-[300px]">
                    <p>Path to preprocessed dataset containing:</p>
                    <ul className="text-xs mt-1 list-disc list-inside">
                      <li>latents/ - VAE-encoded video latents</li>
                      <li>conditions/ - Text embeddings</li>
                      <li>audio_latents/ - (optional) Audio latents</li>
                    </ul>
                  </TooltipContent>
                </Tooltip>
              </Label>
              <div className="flex gap-2">
                <Input
                  value={params.data_root}
                  onChange={(e) => updateParams({ data_root: e.target.value })}
                  placeholder="/path/to/preprocessed/data"
                  disabled={isTraining}
                  className="glass border-border/50 font-mono text-sm"
                />
                <Button variant="outline" size="icon" disabled={isTraining} className="shrink-0 glass">
                  <FolderOpen className="h-4 w-4" />
                </Button>
              </div>
            </div>

            <div className="space-y-2">
              <Label className="text-sm font-medium">Output Directory</Label>
              <Input
                value={params.output_dir}
                onChange={(e) => updateParams({ output_dir: e.target.value })}
                placeholder="./training_output"
                disabled={isTraining}
                className="glass border-border/50 font-mono text-sm"
              />
            </div>
          </CardContent>
        </Card>

        {/* Advanced Settings */}
        <Collapsible open={advancedOpen} onOpenChange={setAdvancedOpen}>
          <CollapsibleTrigger asChild>
            <button className="flex items-center gap-2 w-full p-4 rounded-xl glass border border-border/50 hover:border-primary/30 transition-all group">
              <Settings2 className="h-4 w-4 text-muted-foreground group-hover:text-primary" />
              <span className="text-sm font-medium flex-1 text-left group-hover:text-primary">Advanced Settings</span>
              <ChevronDown className={`h-4 w-4 transition-transform ${advancedOpen ? "rotate-180" : ""}`} />
            </button>
          </CollapsibleTrigger>
          <CollapsibleContent className="pt-4 space-y-4">
            {/* Precision */}
            <Card className="glass border-border/50">
              <CardContent className="p-4 space-y-4">
                <Label className="text-sm font-medium">Precision Mode</Label>
                <div className="grid grid-cols-3 gap-2">
                  {precisionModes.map((mode) => {
                    const isSelected = params.mixed_precision_mode === mode.value;
                    return (
                      <button
                        key={mode.value}
                        onClick={() => updateParams({ mixed_precision_mode: mode.value as TrainingParams["mixed_precision_mode"] })}
                        disabled={isTraining}
                        className={`
                          px-3 py-2 text-xs rounded-lg border transition-all
                          ${isSelected
                            ? "border-primary/50 bg-primary/10 text-primary"
                            : "border-border/50 glass hover:border-primary/30"
                          }
                        `}
                      >
                        <div className="font-medium">{mode.label}</div>
                        <div className="text-[10px] text-muted-foreground">{mode.description}</div>
                      </button>
                    );
                  })}
                </div>

                <div className="flex items-center justify-between p-3 rounded-lg bg-secondary/30">
                  <div>
                    <Label className="text-sm">8-bit Text Encoder</Label>
                    <p className="text-xs text-muted-foreground">Reduce memory usage</p>
                  </div>
                  <Switch
                    checked={params.load_text_encoder_in_8bit}
                    onCheckedChange={(checked) => updateParams({ load_text_encoder_in_8bit: checked })}
                    disabled={isTraining}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Checkpoints */}
            <Card className="glass border-border/50">
              <CardContent className="p-4 space-y-4">
                <Label className="text-sm font-medium">Checkpoint Settings</Label>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label className="text-xs text-muted-foreground">Save Every N Steps</Label>
                    <Input
                      type="number"
                      value={params.checkpoint_interval}
                      onChange={(e) => updateParams({ checkpoint_interval: parseInt(e.target.value) || 250 })}
                      disabled={isTraining}
                      className="glass border-border/50"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs text-muted-foreground">Keep Last N</Label>
                    <Input
                      type="number"
                      value={params.keep_last_n_checkpoints}
                      onChange={(e) => updateParams({ keep_last_n_checkpoints: parseInt(e.target.value) || 3 })}
                      disabled={isTraining}
                      className="glass border-border/50"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Seed */}
            <Card className="glass border-border/50">
              <CardContent className="p-4 space-y-2">
                <Label className="text-sm font-medium">Random Seed</Label>
                <Input
                  type="number"
                  value={params.seed}
                  onChange={(e) => updateParams({ seed: parseInt(e.target.value) || 42 })}
                  disabled={isTraining}
                  className="glass border-border/50 font-mono"
                />
              </CardContent>
            </Card>
          </CollapsibleContent>
        </Collapsible>

        {/* Validation Settings */}
        <Collapsible open={validationOpen} onOpenChange={setValidationOpen}>
          <CollapsibleTrigger asChild>
            <button className="flex items-center gap-2 w-full p-4 rounded-xl glass border border-border/50 hover:border-primary/30 transition-all group">
              <Video className="h-4 w-4 text-muted-foreground group-hover:text-primary" />
              <span className="text-sm font-medium flex-1 text-left group-hover:text-primary">Validation Settings</span>
              <ChevronDown className={`h-4 w-4 transition-transform ${validationOpen ? "rotate-180" : ""}`} />
            </button>
          </CollapsibleTrigger>
          <CollapsibleContent className="pt-4">
            <Card className="glass border-border/50">
              <CardContent className="p-4 space-y-4">
                <div className="space-y-2">
                  <Label className="text-sm font-medium">Validation Prompts</Label>
                  <Textarea
                    value={params.validation_prompts.join("\n")}
                    onChange={(e) => updateParams({ validation_prompts: e.target.value.split("\n").filter((p) => p.trim()) })}
                    placeholder="One prompt per line..."
                    disabled={isTraining}
                    className="glass border-border/50 min-h-[100px]"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label className="text-xs text-muted-foreground">Validation Interval</Label>
                    <Input
                      type="number"
                      value={params.validation_interval || ""}
                      onChange={(e) => updateParams({ validation_interval: e.target.value ? parseInt(e.target.value) : null })}
                      placeholder="100"
                      disabled={isTraining}
                      className="glass border-border/50"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs text-muted-foreground">Inference Steps</Label>
                    <Input
                      type="number"
                      value={params.validation_inference_steps}
                      onChange={(e) => updateParams({ validation_inference_steps: parseInt(e.target.value) || 50 })}
                      disabled={isTraining}
                      className="glass border-border/50"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </CollapsibleContent>
        </Collapsible>
      </div>

      {/* Right Panel - Status & Controls */}
      <div className="space-y-6">
        {/* Training Controls */}
        <Card className="glass-card border-border/50 overflow-hidden sticky top-24">
          <div className="h-1 bg-gradient-to-r from-primary via-purple-500 to-blue-500 animate-gradient" />
          <CardContent className="p-6 space-y-6">
            {/* Status Badge */}
            <div className="flex items-center justify-between">
              <Label className="text-sm font-medium">Status</Label>
              <div className={`
                flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium
                ${status === "training" ? "bg-blue-500/20 text-blue-400" : ""}
                ${status === "completed" ? "bg-green-500/20 text-green-400" : ""}
                ${status === "error" ? "bg-red-500/20 text-red-400" : ""}
                ${status === "stopped" ? "bg-yellow-500/20 text-yellow-400" : ""}
                ${status === "pending" ? "bg-muted text-muted-foreground" : ""}
              `}>
                {status === "training" && <Loader2 className="h-3 w-3 animate-spin" />}
                {status === "completed" && <CheckCircle2 className="h-3 w-3" />}
                {status === "error" && <XCircle className="h-3 w-3" />}
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </div>
            </div>

            {/* Progress */}
            {isTraining && (
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Progress</span>
                  <span className="font-mono">{currentStep} / {totalSteps}</span>
                </div>
                <div className="relative h-2 rounded-full bg-secondary overflow-hidden">
                  <div
                    className="absolute inset-y-0 left-0 bg-gradient-to-r from-primary to-purple-500 rounded-full transition-all"
                    style={{ width: `${progress}%` }}
                  />
                  <div
                    className="absolute inset-y-0 left-0 bg-gradient-to-r from-primary to-purple-500 rounded-full blur-sm opacity-50 transition-all"
                    style={{ width: `${progress}%` }}
                  />
                </div>
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>{progress.toFixed(1)}%</span>
                  {eta && <span>ETA: {eta}</span>}
                </div>
              </div>
            )}

            {/* Loss */}
            {currentLoss !== null && (
              <div className="flex items-center justify-between p-3 rounded-lg glass border border-border/50">
                <div className="flex items-center gap-2">
                  <TrendingDown className="h-4 w-4 text-primary" />
                  <span className="text-sm">Loss</span>
                </div>
                <span className="font-mono text-sm text-primary">{currentLoss.toFixed(6)}</span>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/20">
                <p className="text-sm text-destructive">{error}</p>
              </div>
            )}

            {/* Control Buttons */}
            <div className="flex gap-3">
              {!isTraining ? (
                <Button
                  onClick={handleStartTraining}
                  className="flex-1 h-12 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 glow-primary btn-shine"
                >
                  <Play className="h-5 w-5 mr-2" />
                  Start Training
                </Button>
              ) : (
                <Button
                  onClick={handleStopTraining}
                  variant="destructive"
                  className="flex-1 h-12"
                >
                  <Square className="h-5 w-5 mr-2" />
                  Stop Training
                </Button>
              )}
            </div>

            {/* Quick Info */}
            <div className="space-y-2 p-4 rounded-xl bg-secondary/30">
              <p className="text-xs text-muted-foreground">
                <span className="font-medium text-foreground">Mode:</span> {params.training_mode.toUpperCase()}
                {params.training_mode === "lora" && ` (rank ${params.lora_rank})`}
              </p>
              <p className="text-xs text-muted-foreground">
                <span className="font-medium text-foreground">Steps:</span> {params.steps} @ {params.learning_rate}
              </p>
              <p className="text-xs text-muted-foreground">
                <span className="font-medium text-foreground">Batch:</span> {params.batch_size} x {params.gradient_accumulation_steps}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
