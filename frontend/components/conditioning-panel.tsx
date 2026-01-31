"use client";

import { useState, useCallback, useEffect } from "react";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Image as ImageIcon, Video, X, Upload } from "lucide-react";
import type { GenerationParams } from "@/lib/api";
import { uploadImage, uploadVideo } from "@/lib/api";

interface ConditioningPanelProps {
  params: GenerationParams;
  onParamsChange: (params: Partial<GenerationParams>) => void;
}

export function ConditioningPanel({
  params,
  onParamsChange,
}: ConditioningPanelProps) {
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [videoPreview, setVideoPreview] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [dragOverImage, setDragOverImage] = useState(false);
  const [dragOverVideo, setDragOverVideo] = useState(false);

  useEffect(() => {
    if (!params.conditioning_image) {
      setImagePreview(null);
    }
  }, [params.conditioning_image]);

  useEffect(() => {
    if (!params.video_conditioning) {
      setVideoPreview(null);
    }
  }, [params.video_conditioning]);

  const handleImageUpload = useCallback(
    async (file: File) => {
      try {
        setUploading(true);
        const path = await uploadImage(file);
        onParamsChange({ conditioning_image: path });

        // Create preview
        const reader = new FileReader();
        reader.onload = (e) => setImagePreview(e.target?.result as string);
        reader.readAsDataURL(file);
      } catch (error) {
        console.error("Failed to upload image:", error);
      } finally {
        setUploading(false);
      }
    },
    [onParamsChange]
  );

  const handleVideoUpload = useCallback(
    async (file: File) => {
      try {
        setUploading(true);
        const path = await uploadVideo(file);
        onParamsChange({ video_conditioning: path });

        // Create preview
        setVideoPreview(URL.createObjectURL(file));
      } catch (error) {
        console.error("Failed to upload video:", error);
      } finally {
        setUploading(false);
      }
    },
    [onParamsChange]
  );

  const handleImageDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOverImage(false);
      const file = e.dataTransfer.files[0];
      if (file && file.type.startsWith("image/")) {
        handleImageUpload(file);
      }
    },
    [handleImageUpload]
  );

  const handleVideoDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOverVideo(false);
      const file = e.dataTransfer.files[0];
      if (file && file.type.startsWith("video/")) {
        handleVideoUpload(file);
      }
    },
    [handleVideoUpload]
  );

  const clearImage = () => {
    setImagePreview(null);
    onParamsChange({
      conditioning_image: undefined,
      conditioning_frame_idx: undefined,
      conditioning_strength: undefined,
    });
  };

  const clearVideo = () => {
    setVideoPreview(null);
    onParamsChange({
      video_conditioning: undefined,
      conditioning_mode: undefined,
    });
  };

  return (
    <div className="space-y-6">
      {/* Image Conditioning */}
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <ImageIcon className="h-4 w-4 text-primary" />
          <Label className="text-sm font-medium">Image Conditioning</Label>
        </div>

        {imagePreview ? (
          <div className="relative rounded-xl overflow-hidden border border-border">
            <img
              src={imagePreview}
              alt="Conditioning"
              className="w-full h-48 object-cover"
            />
            <Button
              variant="destructive"
              size="icon"
              className="absolute top-2 right-2 h-8 w-8"
              onClick={clearImage}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        ) : (
          <div
            onDrop={handleImageDrop}
            onDragOver={(e) => {
              e.preventDefault();
              setDragOverImage(true);
            }}
            onDragLeave={() => setDragOverImage(false)}
            className={`drop-zone flex flex-col items-center justify-center h-32 rounded-xl cursor-pointer transition-all ${
              dragOverImage ? "drag-over" : ""
            }`}
            onClick={() => document.getElementById("image-upload")?.click()}
          >
            <Upload className="h-8 w-8 text-muted-foreground mb-2" />
            <p className="text-sm text-muted-foreground">
              {uploading ? "Uploading..." : "Drop image or click to upload"}
            </p>
            <input
              id="image-upload"
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) handleImageUpload(file);
              }}
            />
          </div>
        )}

        {params.conditioning_image && (
          <div className="space-y-4 p-4 rounded-xl bg-secondary/30">
            <div className="space-y-2">
              <Label className="text-xs text-muted-foreground">Conditioning Mode</Label>
              <Select
                value={params.conditioning_mode || "guide"}
                onValueChange={(v) =>
                  onParamsChange({ conditioning_mode: v as "replace" | "guide" })
                }
              >
                <SelectTrigger className="bg-card">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="guide">Guide</SelectItem>
                  <SelectItem value="replace">Replace</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label className="text-xs text-muted-foreground">Frame Index</Label>
                <span className="text-xs font-mono text-primary">
                  {params.conditioning_frame_idx || 0}
                </span>
              </div>
              <Slider
                value={[params.conditioning_frame_idx || 0]}
                onValueChange={([v]) =>
                  onParamsChange({ conditioning_frame_idx: v })
                }
                min={0}
                max={params.num_frames - 1}
                step={1}
                className="w-full"
              />
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label className="text-xs text-muted-foreground">Strength</Label>
                <span className="text-xs font-mono text-primary">
                  {(params.conditioning_strength || 1.0).toFixed(2)}
                </span>
              </div>
              <Slider
                value={[params.conditioning_strength || 1.0]}
                onValueChange={([v]) =>
                  onParamsChange({ conditioning_strength: v })
                }
                min={0}
                max={1}
                step={0.01}
                className="w-full"
              />
            </div>
          </div>
        )}
      </div>

      {/* Video Conditioning (IC-LoRA) */}
      {params.pipeline === "ic_lora" && (
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Video className="h-4 w-4 text-primary" />
            <Label className="text-sm font-medium">Video Conditioning</Label>
          </div>

          {videoPreview ? (
            <div className="relative rounded-xl overflow-hidden border border-border">
              <video
                src={videoPreview}
                className="w-full h-48 object-cover"
                controls
                muted
              />
              <Button
                variant="destructive"
                size="icon"
                className="absolute top-2 right-2 h-8 w-8"
                onClick={clearVideo}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ) : (
            <div
              onDrop={handleVideoDrop}
              onDragOver={(e) => {
                e.preventDefault();
                setDragOverVideo(true);
              }}
              onDragLeave={() => setDragOverVideo(false)}
              className={`drop-zone flex flex-col items-center justify-center h-32 rounded-xl cursor-pointer transition-all ${
                dragOverVideo ? "drag-over" : ""
              }`}
              onClick={() => document.getElementById("video-upload")?.click()}
            >
              <Upload className="h-8 w-8 text-muted-foreground mb-2" />
              <p className="text-sm text-muted-foreground">
                {uploading ? "Uploading..." : "Drop video or click to upload"}
              </p>
              <input
                id="video-upload"
                type="file"
                accept="video/*"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleVideoUpload(file);
                }}
              />
            </div>
          )}

          {params.video_conditioning && (
            <div className="space-y-4 p-4 rounded-xl bg-secondary/30">
              <div className="space-y-2">
                <Label className="text-xs text-muted-foreground">Conditioning Mode</Label>
                <Select
                  value={params.conditioning_mode || "guide"}
                  onValueChange={(v) =>
                    onParamsChange({ conditioning_mode: v as "replace" | "guide" })
                  }
                >
                  <SelectTrigger className="bg-card">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="guide">Guide</SelectItem>
                    <SelectItem value="replace">Replace</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label className="text-xs text-muted-foreground">Frame Index</Label>
                  <span className="text-xs font-mono text-primary">
                    {params.conditioning_frame_idx || 0}
                  </span>
                </div>
                <Slider
                  value={[params.conditioning_frame_idx || 0]}
                  onValueChange={([v]) =>
                    onParamsChange({ conditioning_frame_idx: v })
                  }
                  min={0}
                  max={params.num_frames - 1}
                  step={1}
                  className="w-full"
                />
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label className="text-xs text-muted-foreground">Strength</Label>
                  <span className="text-xs font-mono text-primary">
                    {(params.conditioning_strength || 1.0).toFixed(2)}
                  </span>
                </div>
                <Slider
                  value={[params.conditioning_strength || 1.0]}
                  onValueChange={([v]) =>
                    onParamsChange({ conditioning_strength: v })
                  }
                  min={0}
                  max={1}
                  step={0.01}
                  className="w-full"
                />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
