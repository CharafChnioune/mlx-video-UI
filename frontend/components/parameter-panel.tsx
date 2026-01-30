"use client";

import { useState } from "react";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
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
  Shuffle,
  Info,
  Maximize,
  Film,
  Settings2,
  Sparkles,
  Volume2,
} from "lucide-react";
import type { GenerationParams } from "@/lib/api";

interface ParameterPanelProps {
  params: GenerationParams;
  onParamsChange: (params: Partial<GenerationParams>) => void;
}

const resolutionPresets = [
  { label: "Square (512x512)", width: 512, height: 512, icon: "1:1" },
  { label: "Portrait (512x768)", width: 512, height: 768, icon: "2:3" },
  { label: "Landscape (768x512)", width: 768, height: 512, icon: "3:2" },
  { label: "HD (704x480)", width: 704, height: 480, icon: "16:9" },
  { label: "Wide (832x480)", width: 832, height: 480, icon: "16:9" },
];

const framePresets = [
  { label: "Short", value: 17, duration: "0.7s" },
  { label: "Medium", value: 33, duration: "1.3s" },
  { label: "Long", value: 49, duration: "2.0s" },
  { label: "Extra Long", value: 65, duration: "2.7s" },
  { label: "Maximum", value: 81, duration: "3.3s" },
];

export function ParameterPanel({ params, onParamsChange }: ParameterPanelProps) {
  const [advancedOpen, setAdvancedOpen] = useState(false);

  const generateRandomSeed = () => {
    onParamsChange({ seed: Math.floor(Math.random() * 2147483647) });
  };

  const handleResolutionPreset = (preset: (typeof resolutionPresets)[0]) => {
    onParamsChange({ width: preset.width, height: preset.height });
  };

  return (
    <div className="space-y-6">
      {/* Resolution */}
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-primary/10">
            <Maximize className="h-4 w-4 text-primary" />
          </div>
          <Label className="text-sm font-medium">Resolution</Label>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
          {resolutionPresets.map((preset) => {
            const isSelected =
              params.width === preset.width && params.height === preset.height;
            return (
              <button
                key={preset.label}
                onClick={() => handleResolutionPreset(preset)}
                className={`
                  group relative px-3 py-2.5 text-xs rounded-xl border transition-all duration-300
                  ${isSelected
                    ? "border-primary/50 bg-primary/10 text-primary glow-primary"
                    : "border-border/50 glass text-muted-foreground hover:border-primary/30 hover:bg-primary/5 hover:text-foreground"
                  }
                `}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-medium">{preset.width}x{preset.height}</span>
                  <span className={`
                    px-1.5 py-0.5 rounded text-[10px] transition-colors
                    ${isSelected ? 'bg-primary/20' : 'bg-secondary/50 group-hover:bg-primary/10'}
                  `}>
                    {preset.icon}
                  </span>
                </div>
              </button>
            );
          })}
        </div>

        <div className="grid grid-cols-2 gap-4 p-4 rounded-xl glass border border-border/50">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label className="text-xs text-muted-foreground">Width</Label>
              <span className="text-xs font-mono text-primary px-2 py-0.5 rounded bg-primary/10">{params.width}px</span>
            </div>
            <div className="slider-glow">
              <Slider
                value={[params.width]}
                onValueChange={([v]) => onParamsChange({ width: Math.round(v / 32) * 32 })}
                min={256}
                max={1024}
                step={32}
                className="w-full"
              />
            </div>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label className="text-xs text-muted-foreground">Height</Label>
              <span className="text-xs font-mono text-primary px-2 py-0.5 rounded bg-primary/10">{params.height}px</span>
            </div>
            <div className="slider-glow">
              <Slider
                value={[params.height]}
                onValueChange={([v]) => onParamsChange({ height: Math.round(v / 32) * 32 })}
                min={256}
                max={1024}
                step={32}
                className="w-full"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Frames */}
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-primary/10">
            <Film className="h-4 w-4 text-primary" />
          </div>
          <Label className="text-sm font-medium">Frames</Label>
        </div>

        <div className="flex flex-wrap gap-2">
          {framePresets.map((preset) => {
            const isSelected = params.num_frames === preset.value;
            return (
              <button
                key={preset.value}
                onClick={() => onParamsChange({ num_frames: preset.value })}
                className={`
                  group px-3 py-2 text-xs rounded-xl border transition-all duration-300
                  ${isSelected
                    ? "border-primary/50 bg-primary/10 text-primary glow-primary"
                    : "border-border/50 glass text-muted-foreground hover:border-primary/30 hover:bg-primary/5 hover:text-foreground"
                  }
                `}
              >
                <div className="flex flex-col items-start gap-0.5">
                  <span className="font-medium">{preset.label}</span>
                  <span className={`text-[10px] ${isSelected ? 'text-primary/70' : 'text-muted-foreground/70'}`}>
                    {preset.value}f &middot; {preset.duration}
                  </span>
                </div>
              </button>
            );
          })}
        </div>

        <div className="p-4 rounded-xl glass border border-border/50 space-y-3">
          <div className="flex items-center justify-between">
            <Label className="text-xs text-muted-foreground">Custom Frames</Label>
            <span className="text-xs font-mono text-primary px-2 py-0.5 rounded bg-primary/10">{params.num_frames} frames</span>
          </div>
          <div className="slider-glow">
            <Slider
              value={[params.num_frames]}
              onValueChange={([v]) => onParamsChange({ num_frames: 1 + Math.round((v - 1) / 8) * 8 })}
              min={9}
              max={97}
              step={8}
              className="w-full"
            />
          </div>
          <p className="text-xs text-muted-foreground flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-primary/50 animate-pulse" />
            Duration: ~{((params.num_frames - 1) / params.fps).toFixed(1)}s at {params.fps} FPS
          </p>
        </div>
      </div>

      {/* Seed */}
      <div className="space-y-3">
        <Label className="text-sm font-medium flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-primary/10">
            <Sparkles className="h-4 w-4 text-primary" />
          </div>
          Seed
        </Label>
        <div className="flex gap-2">
          <Input
            type="number"
            value={params.seed}
            onChange={(e) => onParamsChange({ seed: parseInt(e.target.value) || 0 })}
            className="font-mono glass border-border/50 focus:border-primary/50"
          />
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="outline"
                size="icon"
                onClick={generateRandomSeed}
                className="shrink-0 glass border-border/50 hover:border-primary/50 hover:bg-primary/10 hover:text-primary transition-all"
              >
                <Shuffle className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Randomize seed</TooltipContent>
          </Tooltip>
        </div>
      </div>

      {/* Dev Pipeline Options */}
      {params.pipeline === "dev" && (
        <div className="space-y-4 p-4 rounded-xl glass-intense border border-primary/20">
          <Label className="text-sm font-medium text-primary flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
            Dev Pipeline Settings
          </Label>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label className="text-xs text-muted-foreground">Steps</Label>
              <span className="text-xs font-mono text-primary px-2 py-0.5 rounded bg-primary/10">{params.steps || 40}</span>
            </div>
            <div className="slider-glow">
              <Slider
                value={[params.steps || 40]}
                onValueChange={([v]) => onParamsChange({ steps: v })}
                min={10}
                max={100}
                step={1}
                className="w-full"
              />
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label className="text-xs text-muted-foreground">CFG Scale</Label>
              <span className="text-xs font-mono text-primary px-2 py-0.5 rounded bg-primary/10">{params.cfg_scale || 4.0}</span>
            </div>
            <div className="slider-glow">
              <Slider
                value={[params.cfg_scale || 4.0]}
                onValueChange={([v]) => onParamsChange({ cfg_scale: v })}
                min={1}
                max={15}
                step={0.1}
                className="w-full"
              />
            </div>
          </div>
        </div>
      )}

      {/* Advanced Settings */}
      <Collapsible open={advancedOpen} onOpenChange={setAdvancedOpen}>
        <CollapsibleTrigger asChild>
          <button className="flex items-center gap-2 w-full p-4 rounded-xl glass border border-border/50 hover:border-primary/30 hover:bg-primary/5 transition-all duration-300 group">
            <div className="p-1.5 rounded-lg bg-secondary/50 group-hover:bg-primary/10 transition-colors">
              <Settings2 className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
            </div>
            <span className="text-sm font-medium flex-1 text-left group-hover:text-primary transition-colors">Advanced Settings</span>
            <ChevronDown
              className={`h-4 w-4 text-muted-foreground transition-all duration-300 ${
                advancedOpen ? "rotate-180 text-primary" : ""
              }`}
            />
          </button>
        </CollapsibleTrigger>
        <CollapsibleContent className="pt-4 space-y-4 animate-in slide-in-from-top-2 duration-200">
          <div className="space-y-3 p-4 rounded-xl glass border border-border/50">
            <div className="flex items-center justify-between">
              <Label className="text-xs text-muted-foreground">FPS</Label>
              <span className="text-xs font-mono text-primary px-2 py-0.5 rounded bg-primary/10">{params.fps}</span>
            </div>
            <div className="slider-glow">
              <Slider
                value={[params.fps]}
                onValueChange={([v]) => onParamsChange({ fps: v })}
                min={12}
                max={60}
                step={1}
                className="w-full"
              />
            </div>
          </div>

          <div className="flex items-center justify-between p-4 rounded-xl glass border border-border/50 hover:border-primary/20 transition-colors group">
            <div className="flex items-center gap-3">
              <div className="p-1.5 rounded-lg bg-secondary/50 group-hover:bg-primary/10 transition-colors">
                <Sparkles className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
              </div>
              <div className="flex flex-col">
                <Label className="text-sm cursor-pointer">Enhance Prompt</Label>
                <span className="text-xs text-muted-foreground">AI-powered prompt enhancement</span>
              </div>
            </div>
            <Switch
              checked={params.enhance_prompt || false}
              onCheckedChange={(checked) => onParamsChange({ enhance_prompt: checked })}
              className="data-[state=checked]:bg-primary"
            />
          </div>

          <div className="flex items-center justify-between p-4 rounded-xl glass border border-border/50 hover:border-primary/20 transition-colors group">
            <div className="flex items-center gap-3">
              <div className="p-1.5 rounded-lg bg-secondary/50 group-hover:bg-primary/10 transition-colors">
                <Volume2 className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
              </div>
              <div className="flex flex-col">
                <Label className="text-sm cursor-pointer">Audio Generation</Label>
                <span className="text-xs text-muted-foreground">Generate audio for the video</span>
              </div>
            </div>
            <Switch
              checked={params.audio || false}
              onCheckedChange={(checked) => onParamsChange({ audio: checked })}
              className="data-[state=checked]:bg-primary"
            />
          </div>

          <div className="space-y-3 p-4 rounded-xl glass border border-border/50">
            <Label className="text-xs text-muted-foreground">Tiling Mode</Label>
            <Select
              value={params.tiling || "auto"}
              onValueChange={(v) => onParamsChange({ tiling: v as "auto" | "on" | "off" })}
            >
              <SelectTrigger className="glass border-border/50 hover:border-primary/30">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="glass-card border-border/50">
                <SelectItem value="auto" className="focus:bg-primary/10">Auto</SelectItem>
                <SelectItem value="on" className="focus:bg-primary/10">On</SelectItem>
                <SelectItem value="off" className="focus:bg-primary/10">Off</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-3 p-4 rounded-xl glass border border-border/50">
            <div className="flex items-center justify-between">
              <Label className="text-xs text-muted-foreground">Memory Limit (GB)</Label>
              <span className="text-xs font-mono text-primary px-2 py-0.5 rounded bg-primary/10">{params.cache_limit_gb || 32}GB</span>
            </div>
            <div className="slider-glow">
              <Slider
                value={[params.cache_limit_gb || 32]}
                onValueChange={([v]) => onParamsChange({ cache_limit_gb: v })}
                min={8}
                max={128}
                step={4}
                className="w-full"
              />
            </div>
          </div>
        </CollapsibleContent>
      </Collapsible>
    </div>
  );
}
