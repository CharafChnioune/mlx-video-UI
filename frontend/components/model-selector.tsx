"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Cpu, Zap, Sparkles, Video, Check } from "lucide-react";

interface ModelSelectorProps {
  pipeline: string;
  onPipelineChange: (value: string) => void;
  modelRepo: string;
  onModelRepoChange: (value: string) => void;
}

const pipelines = [
  {
    value: "distilled",
    label: "Distilled",
    description: "Fast generation, fewer steps",
    longDescription: "Optimized for speed with 8-step generation. Best for quick iterations.",
    icon: Zap,
    color: "from-yellow-500 to-orange-500",
  },
  {
    value: "dev",
    label: "Developer",
    description: "Full control with CFG",
    longDescription: "Full quality with negative prompts and CFG scale control.",
    icon: Cpu,
    color: "from-blue-500 to-cyan-500",
  },
  {
    value: "keyframe",
    label: "Keyframe",
    description: "Image-to-video generation",
    longDescription: "Generate videos starting from your own images.",
    icon: Sparkles,
    color: "from-purple-500 to-pink-500",
  },
  {
    value: "ic_lora",
    label: "IC-LoRA",
    description: "Video conditioning",
    longDescription: "Advanced video-to-video with instruction conditioning.",
    icon: Video,
    color: "from-green-500 to-emerald-500",
  },
];

const models = [
  {
    value: "AITRADER/ltx2-distilled-4bit-mlx",
    label: "LTX-2 Distilled 4-bit",
    size: "~10GB",
    speed: "Fastest",
    badge: "Recommended",
  },
  {
    value: "AITRADER/ltx2-distilled-8bit-mlx",
    label: "LTX-2 Distilled 8-bit",
    size: "~19GB",
    speed: "Fast",
    badge: null,
  },
  {
    value: "AITRADER/ltx2-dev-4bit-mlx",
    label: "LTX-2 Dev 4-bit",
    size: "~10GB",
    speed: "Medium",
    badge: null,
  },
  {
    value: "AITRADER/ltx2-dev-8bit-mlx",
    label: "LTX-2 Dev 8-bit",
    size: "~19GB",
    speed: "Slower",
    badge: "Highest Quality",
  },
];

export function ModelSelector({
  pipeline,
  onPipelineChange,
  modelRepo,
  onModelRepoChange,
}: ModelSelectorProps) {
  return (
    <div className="space-y-6">
      {/* Pipeline Selection */}
      <div className="space-y-3">
        <Label className="text-sm font-medium text-foreground/80 flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-primary" />
          Pipeline
        </Label>
        <div className="grid grid-cols-2 gap-3">
          {pipelines.map((p) => {
            const Icon = p.icon;
            const isSelected = pipeline === p.value;
            return (
              <Tooltip key={p.value}>
                <TooltipTrigger asChild>
                  <button
                    onClick={() => onPipelineChange(p.value)}
                    className={`
                      relative flex flex-col items-start p-4 rounded-xl border transition-all duration-300
                      selection-dot ${isSelected ? 'selected' : ''}
                      ${isSelected
                        ? "border-primary/50 glass-intense glow-primary"
                        : "border-border/50 glass hover:border-primary/30 hover:scale-[1.02]"
                      }
                    `}
                  >
                    {/* Background gradient on hover/selection */}
                    <div className={`
                      absolute inset-0 rounded-xl bg-gradient-to-br ${p.color} opacity-0 transition-opacity duration-300
                      ${isSelected ? 'opacity-10' : 'group-hover:opacity-5'}
                    `} />

                    <div className="relative flex items-center gap-2 mb-1.5">
                      <div className={`
                        p-1.5 rounded-lg transition-all duration-300
                        ${isSelected
                          ? `bg-gradient-to-br ${p.color} text-white`
                          : 'bg-secondary/50 text-muted-foreground'
                        }
                      `}>
                        <Icon className={`h-4 w-4 ${isSelected ? 'animate-icon-pulse' : ''}`} />
                      </div>
                      <span className={`
                        font-medium text-sm transition-colors duration-300
                        ${isSelected ? "text-primary" : "text-foreground"}
                      `}>
                        {p.label}
                      </span>
                    </div>
                    <span className="relative text-xs text-muted-foreground line-clamp-1">
                      {p.description}
                    </span>

                    {/* Selected indicator */}
                    {isSelected && (
                      <div className="absolute top-2 right-2 w-5 h-5 rounded-full bg-primary flex items-center justify-center animate-celebration">
                        <Check className="h-3 w-3 text-white" />
                      </div>
                    )}
                  </button>
                </TooltipTrigger>
                <TooltipContent side="bottom" className="max-w-[200px]">
                  <p className="font-medium">{p.label}</p>
                  <p className="text-xs text-muted-foreground mt-1">{p.longDescription}</p>
                </TooltipContent>
              </Tooltip>
            );
          })}
        </div>
      </div>

      {/* Model Selection */}
      <div className="space-y-3">
        <Label className="text-sm font-medium text-foreground/80 flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-primary" />
          Model
        </Label>
        <Select value={modelRepo} onValueChange={onModelRepoChange}>
          <SelectTrigger className="h-14 glass border-border/50 hover:border-primary/30 transition-all">
            <SelectValue placeholder="Select a model">
              {modelRepo && (
                <div className="flex flex-col items-start">
                  <span className="font-medium text-sm">
                    {models.find(m => m.value === modelRepo)?.label}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {models.find(m => m.value === modelRepo)?.size} &middot;{" "}
                    {models.find(m => m.value === modelRepo)?.speed}
                  </span>
                </div>
              )}
            </SelectValue>
          </SelectTrigger>
          <SelectContent className="glass-card border-border/50">
            {models.map((model) => (
              <SelectItem
                key={model.value}
                value={model.value}
                className="py-3 focus:bg-primary/10 cursor-pointer"
              >
                <div className="flex flex-col">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{model.label}</span>
                    {model.badge && (
                      <span className={`
                        px-1.5 py-0.5 rounded text-[10px] font-medium
                        ${model.badge === 'Recommended'
                          ? 'bg-primary/20 text-primary'
                          : 'bg-purple-500/20 text-purple-400'
                        }
                      `}>
                        {model.badge}
                      </span>
                    )}
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {model.size} &middot; {model.speed}
                  </span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
