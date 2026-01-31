"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Plus, Trash2, Layers } from "lucide-react";
import type { GenerationParams, LoraItem } from "@/lib/api";
import { listLoras } from "@/lib/api";
import { useEffect, useState } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface LoraPanelProps {
  params: GenerationParams;
  onParamsChange: (params: Partial<GenerationParams>) => void;
}

export function LoraPanel({ params, onParamsChange }: LoraPanelProps) {
  const loras = params.loras || [];
  const distilledLoras = params.distilled_loras || [];
  const [availableLoras, setAvailableLoras] = useState<LoraItem[]>([]);

  useEffect(() => {
    const load = async () => {
      const items = await listLoras();
      setAvailableLoras(items);
    };
    load();
  }, []);

  const updateLora = (
    index: number,
    key: "path" | "strength",
    value: string | number,
    isDistilled = false
  ) => {
    const list = isDistilled ? [...distilledLoras] : [...loras];
    const item = { ...list[index], [key]: value };
    list[index] = item;
    onParamsChange(isDistilled ? { distilled_loras: list } : { loras: list });
  };

  const addLora = (isDistilled = false) => {
    const list = isDistilled ? [...distilledLoras] : [...loras];
    list.push({ path: "", strength: 1.0 });
    onParamsChange(isDistilled ? { distilled_loras: list } : { loras: list });
  };

  const removeLora = (index: number, isDistilled = false) => {
    const list = isDistilled ? [...distilledLoras] : [...loras];
    list.splice(index, 1);
    onParamsChange(isDistilled ? { distilled_loras: list } : { loras: list });
  };

  const renderList = (list: { path: string; strength: number }[], isDistilled = false) => (
    <div className="space-y-4">
      {list.length === 0 && (
        <p className="text-xs text-muted-foreground">No LoRAs added.</p>
      )}
      {list.map((lora, idx) => (
        <div key={`${isDistilled ? "distilled" : "main"}-${idx}`} className="space-y-3 p-3 rounded-xl glass border border-border/50">
          <div className="flex items-center justify-between gap-2">
            <Label className="text-xs text-muted-foreground">LoRA Path</Label>
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              onClick={() => removeLora(idx, isDistilled)}
            >
              <Trash2 className="h-3.5 w-3.5" />
            </Button>
          </div>
          <div className="space-y-2">
            <Select
              value={lora.path}
              onValueChange={(v) => updateLora(idx, "path", v, isDistilled)}
            >
              <SelectTrigger className="glass border-border/50">
                <SelectValue placeholder="Select LoRA from /loras" />
              </SelectTrigger>
              <SelectContent className="glass-card border-border/50">
                {availableLoras.map((item) => (
                  <SelectItem key={item.path} value={item.path} className="focus:bg-primary/10">
                    {item.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Input
              value={lora.path}
              onChange={(e) => updateLora(idx, "path", e.target.value, isDistilled)}
              placeholder="/path/to/lora.safetensors"
              className="font-mono text-xs"
            />
            <p className="text-[11px] text-muted-foreground">Pick from the lora folder or paste a full path.</p>
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label className="text-xs text-muted-foreground">Strength</Label>
              <span className="text-xs font-mono text-primary px-2 py-0.5 rounded bg-primary/10">
                {lora.strength.toFixed(2)}
              </span>
            </div>
            <Slider
              value={[lora.strength]}
              onValueChange={([v]) => updateLora(idx, "strength", v, isDistilled)}
              min={0}
              max={2}
              step={0.05}
              className="w-full"
            />
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Layers className="h-4 w-4 text-primary" />
        <Label className="text-sm font-medium">LoRA (Runtime)</Label>
      </div>
      {renderList(loras)}
      <Button
        variant="outline"
        className="w-full"
        onClick={() => addLora(false)}
      >
        <Plus className="h-4 w-4 mr-2" />
        Add LoRA
      </Button>

      {params.pipeline === "distilled" && (
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Layers className="h-4 w-4 text-primary" />
            <Label className="text-sm font-medium">Distilled Stage‑2 LoRA</Label>
          </div>
          {renderList(distilledLoras, true)}
          <Button
            variant="outline"
            className="w-full"
            onClick={() => addLora(true)}
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Stage‑2 LoRA
          </Button>
        </div>
      )}
    </div>
  );
}
