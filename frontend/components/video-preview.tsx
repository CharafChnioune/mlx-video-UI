"use client";

import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import {
  Download,
  Play,
  Pause,
  RotateCcw,
  Maximize2,
  Volume2,
  VolumeX,
  Film,
  Sparkles,
} from "lucide-react";
import { getVideoUrl } from "@/lib/api";

interface VideoPreviewProps {
  videoPath?: string;
  isGenerating?: boolean;
}

export function VideoPreview({ videoPath, isGenerating }: VideoPreviewProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(true);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const restart = () => {
    if (videoRef.current) {
      videoRef.current.currentTime = 0;
      videoRef.current.play();
      setIsPlaying(true);
    }
  };

  const handleDownload = () => {
    if (videoPath) {
      const filename = videoPath.split("/").pop() || "video.mp4";
      const a = document.createElement("a");
      a.href = getVideoUrl(filename);
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, "0")}`;
  };

  const handleFullscreen = () => {
    if (videoRef.current) {
      if (document.fullscreenElement) {
        document.exitFullscreen();
      } else {
        videoRef.current.requestFullscreen();
      }
    }
  };

  return (
    <div className="space-y-4">
      {/* Video container with glow effect */}
      <div className={`video-preview-glow rounded-xl ${videoPath ? 'animate-glow-pulse' : ''}`}>
        <div className="video-preview glass-card border border-border/50 gradient-border">
          {videoPath ? (
            <video
              ref={videoRef}
              src={getVideoUrl(videoPath.split("/").pop() || "")}
              className="w-full h-full rounded-lg"
              loop
              muted={isMuted}
              playsInline
              onPlay={() => setIsPlaying(true)}
              onPause={() => setIsPlaying(false)}
              onTimeUpdate={(e) => setCurrentTime(e.currentTarget.currentTime)}
              onLoadedMetadata={(e) => setDuration(e.currentTarget.duration)}
              autoPlay
            />
          ) : (
            <div className="w-full h-full flex flex-col items-center justify-center text-muted-foreground relative overflow-hidden">
              {/* Background decoration */}
              <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-purple-600/5" />

              {/* Animated video frames in background */}
              <div className="absolute inset-4 border-2 border-dashed border-border/30 rounded-lg animate-video-frame" />
              <div className="absolute inset-8 border border-dashed border-border/20 rounded-lg animate-video-frame" style={{ animationDelay: '0.5s' }} />

              {isGenerating ? (
                <div className="flex flex-col items-center gap-6 relative z-10">
                  {/* Animated generation indicator */}
                  <div className="relative">
                    {/* Outer ring */}
                    <div className="w-24 h-24 rounded-full border-4 border-primary/20 animate-spin-slow" />
                    {/* Middle ring */}
                    <div className="absolute inset-2 rounded-full border-4 border-t-primary border-r-purple-500 border-b-blue-500 border-l-transparent animate-spin" />
                    {/* Inner content */}
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary/30 to-purple-600/30 animate-pulse flex items-center justify-center">
                        <Sparkles className="h-5 w-5 text-primary animate-icon-pulse" />
                      </div>
                    </div>
                    {/* Floating particles */}
                    <div className="absolute -top-2 -right-2 w-3 h-3 rounded-full bg-primary/50 animate-particle" />
                    <div className="absolute -bottom-1 -left-1 w-2 h-2 rounded-full bg-purple-500/50 animate-particle" style={{ animationDelay: '1s' }} />
                    <div className="absolute top-1/2 -right-4 w-2 h-2 rounded-full bg-blue-500/50 animate-particle" style={{ animationDelay: '2s' }} />
                  </div>
                  <div className="text-center">
                    <p className="text-sm font-medium text-foreground mb-1">Creating your video</p>
                    <p className="text-xs text-muted-foreground">This may take a moment...</p>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-4 relative z-10">
                  {/* Animated placeholder icon */}
                  <div className="relative group">
                    <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-purple-600/20 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                    <div className="relative w-24 h-24 rounded-2xl glass-card border border-border/50 flex items-center justify-center group-hover:scale-105 transition-transform duration-300">
                      <Film className="h-10 w-10 text-muted-foreground/50 group-hover:text-primary/70 transition-colors" />
                    </div>
                  </div>
                  <div className="text-center">
                    <p className="text-sm font-medium text-foreground/80 mb-1">Ready to create</p>
                    <p className="text-xs text-muted-foreground">Your video will appear here</p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Enhanced video controls */}
      {videoPath && (
        <div className="flex items-center gap-2 p-3 rounded-xl glass-card border border-border/50">
          <Button
            variant="ghost"
            size="icon"
            className="h-9 w-9 hover:bg-primary/10 hover:text-primary transition-colors"
            onClick={togglePlay}
          >
            {isPlaying ? (
              <Pause className="h-4 w-4" />
            ) : (
              <Play className="h-4 w-4" />
            )}
          </Button>

          <Button
            variant="ghost"
            size="icon"
            className="h-9 w-9 hover:bg-primary/10 hover:text-primary transition-colors"
            onClick={restart}
          >
            <RotateCcw className="h-4 w-4" />
          </Button>

          <div className="flex-1 flex items-center gap-3 px-3">
            <span className="text-xs font-mono text-muted-foreground w-10 tabular-nums">
              {formatTime(currentTime)}
            </span>
            <div className="flex-1 h-1.5 bg-secondary rounded-full overflow-hidden relative">
              {/* Glow effect on progress */}
              <div
                className="absolute inset-y-0 left-0 bg-gradient-to-r from-primary to-purple-500 rounded-full transition-all"
                style={{ width: `${(currentTime / duration) * 100 || 0}%` }}
              />
              <div
                className="absolute inset-y-0 left-0 bg-gradient-to-r from-primary to-purple-500 rounded-full blur-sm opacity-50 transition-all"
                style={{ width: `${(currentTime / duration) * 100 || 0}%` }}
              />
            </div>
            <span className="text-xs font-mono text-muted-foreground w-10 tabular-nums">
              {formatTime(duration)}
            </span>
          </div>

          <Button
            variant="ghost"
            size="icon"
            className="h-9 w-9 hover:bg-primary/10 hover:text-primary transition-colors"
            onClick={toggleMute}
          >
            {isMuted ? (
              <VolumeX className="h-4 w-4" />
            ) : (
              <Volume2 className="h-4 w-4" />
            )}
          </Button>

          <Button
            variant="ghost"
            size="icon"
            className="h-9 w-9 hover:bg-primary/10 hover:text-primary transition-colors"
            onClick={handleFullscreen}
          >
            <Maximize2 className="h-4 w-4" />
          </Button>

          <Button
            variant="outline"
            size="sm"
            className="ml-2 bg-gradient-to-r from-primary/10 to-purple-600/10 border-primary/30 hover:border-primary/50 hover:from-primary/20 hover:to-purple-600/20 transition-all"
            onClick={handleDownload}
          >
            <Download className="h-4 w-4 mr-2" />
            Download
          </Button>
        </div>
      )}
    </div>
  );
}
