"use client";
import { Loader2, CheckCircle2, XCircle, Sparkles, Zap, Film, Download } from "lucide-react";

interface ProgressIndicatorProps {
  status: "idle" | "pending" | "processing" | "completed" | "error";
  progress: number;
  currentStep?: string;
  eta?: string;
  downloadProgress?: number;
  downloadStep?: string;
  error?: string;
}

const steps = [
  { icon: Zap, label: "Initializing", threshold: 0 },
  { icon: Sparkles, label: "Denoising", threshold: 10 },
  { icon: Film, label: "Decoding", threshold: 85 },
  { icon: Download, label: "Finalizing", threshold: 95 },
];

export function ProgressIndicator({
  status,
  progress,
  currentStep,
  eta,
  downloadProgress,
  downloadStep,
  error,
}: ProgressIndicatorProps) {
  if (status === "idle") return null;

  const getCurrentStepIndex = () => {
    const stepText = (currentStep || "").toLowerCase();
    // Prefer semantic stage detection from backend labels (progress ranges are dynamic).
    if (stepText.includes("saving") || stepText.includes("finaliz") || stepText.includes("mux")) return 3;
    if (stepText.includes("decod") || stepText.includes("streaming frames")) return 2;
    if (stepText.includes("denois") || stepText.includes("stage 1") || stepText.includes("stage 2")) return 1;
    if (stepText.includes("load") || stepText.includes("encod")) return 0;

    for (let i = steps.length - 1; i >= 0; i--) {
      if (progress >= steps[i].threshold) return i;
    }
    return 0;
  };

  const currentStepIndex = getCurrentStepIndex();
  const showDownload =
    (status === "pending" || status === "processing") &&
    (downloadProgress !== undefined || downloadStep);
  const downloadValue = Math.min(100, Math.max(0, downloadProgress || 0));

  return (
    <div className="space-y-4 p-6 rounded-2xl glass-card border border-border/50 relative overflow-hidden">
      {/* Background gradient based on status */}
      <div className={`absolute inset-0 pointer-events-none transition-opacity duration-500 ${
        status === "completed" ? "opacity-100" : "opacity-0"
      }`}>
        <div className="absolute inset-0 bg-gradient-to-br from-green-500/10 via-transparent to-emerald-500/10" />
      </div>
      <div className={`absolute inset-0 pointer-events-none transition-opacity duration-500 ${
        status === "error" ? "opacity-100" : "opacity-0"
      }`}>
        <div className="absolute inset-0 bg-gradient-to-br from-red-500/10 via-transparent to-rose-500/10" />
      </div>

      {/* Status header */}
      <div className="flex items-center gap-3 relative">
        {status === "pending" && (
          <>
            <div className="relative">
              <div className="absolute inset-0 bg-primary rounded-full blur-md opacity-50 animate-pulse" />
              <div className="relative w-10 h-10 rounded-full bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center">
                <Loader2 className="h-5 w-5 text-white animate-spin" />
              </div>
            </div>
            <div>
              <span className="text-sm font-semibold">Initializing</span>
              <p className="text-xs text-muted-foreground">Preparing your request...</p>
            </div>
          </>
        )}
        {status === "processing" && (
          <>
            <div className="relative">
              <div className="absolute inset-0 bg-primary rounded-full blur-md opacity-50 animate-glow-pulse" />
              <div className="relative w-10 h-10 rounded-full bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center">
                <Sparkles className="h-5 w-5 text-white animate-icon-pulse" />
              </div>
            </div>
            <div>
              <span className="text-sm font-semibold">Generating video</span>
              <p className="text-xs text-muted-foreground">
                {currentStep || "Processing..."}
                {eta ? ` • ETA ${eta}` : ""}
              </p>
            </div>
          </>
        )}
        {status === "completed" && (
          <>
            <div className="relative animate-celebration">
              <div className="absolute inset-0 bg-green-500 rounded-full blur-md opacity-50" />
              <div className="relative w-10 h-10 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
                <CheckCircle2 className="h-5 w-5 text-white" />
              </div>
            </div>
            <div>
              <span className="text-sm font-semibold text-green-500">Complete!</span>
              <p className="text-xs text-muted-foreground">Your video is ready</p>
            </div>
          </>
        )}
        {status === "error" && (
          <>
            <div className="relative">
              <div className="absolute inset-0 bg-destructive rounded-full blur-md opacity-50" />
              <div className="relative w-10 h-10 rounded-full bg-gradient-to-br from-destructive to-rose-600 flex items-center justify-center">
                <XCircle className="h-5 w-5 text-white" />
              </div>
            </div>
            <div>
              <span className="text-sm font-semibold text-destructive">Error</span>
              <p className="text-xs text-muted-foreground">Something went wrong</p>
            </div>
          </>
        )}

        {/* Percentage badge */}
        {(status === "pending" || status === "processing") && (
          <div className="ml-auto">
            <span className="text-2xl font-bold gradient-text">{Math.round(progress)}%</span>
          </div>
        )}
      </div>

      {/* Progress bar with neon glow */}
      {(status === "pending" || status === "processing") && (
        <div className="space-y-4 relative">
          {showDownload && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>{downloadStep || "Downloading model weights..."}</span>
                <span className="font-mono text-foreground">{Math.round(downloadValue)}%</span>
              </div>
              <div className="relative h-2 rounded-full bg-secondary/80 overflow-hidden">
                <div
                  className="absolute inset-y-0 left-0 bg-gradient-to-r from-sky-400 via-cyan-400 to-blue-500 rounded-full transition-all duration-300"
                  style={{ width: `${downloadValue}%` }}
                />
                <div
                  className="absolute inset-y-0 left-0 bg-gradient-to-r from-sky-400 via-cyan-400 to-blue-500 rounded-full blur-sm opacity-60 transition-all duration-300"
                  style={{ width: `${downloadValue}%` }}
                />
              </div>
            </div>
          )}
          {/* Neon progress bar */}
          <div className="relative h-3 rounded-full bg-secondary overflow-hidden">
            {/* Glow effect */}
            <div
              className="absolute inset-y-0 left-0 bg-gradient-to-r from-primary via-purple-500 to-primary rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
            {/* Additional glow layer */}
            <div
              className="absolute inset-y-0 left-0 bg-gradient-to-r from-primary via-purple-500 to-primary rounded-full blur-sm opacity-70 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
            {/* Shimmer effect on the progress */}
            <div
              className="absolute inset-y-0 left-0 overflow-hidden rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            >
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer" style={{ animationDuration: '1.5s' }} />
            </div>
          </div>

          {/* Step indicators */}
          <div className="flex justify-between items-center">
            {steps.map((step, index) => {
              const Icon = step.icon;
              // Use semantic stage position, not hardcoded progress thresholds (ranges are dynamic).
              // This block only renders for pending/processing, so `status` is narrowed here.
              const isCompleted = index < currentStepIndex;
              const isCurrent = index === currentStepIndex;
              const isActive = isCompleted || isCurrent;

              return (
                <div key={index} className="flex flex-col items-center gap-1">
                  <div className={`
                    relative p-2 rounded-lg transition-all duration-300
                    ${isActive
                      ? isCurrent
                        ? 'bg-primary/20 text-primary'
                        : 'bg-primary/10 text-primary/70'
                      : 'bg-secondary/50 text-muted-foreground/50'
                    }
                  `}>
                    {isCurrent && (
                      <div className="absolute inset-0 bg-primary rounded-lg blur-md opacity-30 animate-pulse" />
                    )}
                    <Icon className={`h-4 w-4 relative ${isCurrent ? 'animate-icon-bounce' : ''}`} />
                  </div>
                  <span className={`text-[10px] font-medium transition-colors ${
                    isActive ? 'text-primary' : 'text-muted-foreground/50'
                  }`}>
                    {step.label}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Completed state with animated particles */}
      {status === "completed" && (
        <div className="relative h-3 rounded-full bg-green-500/20 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full" />
          <div className="absolute inset-0 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full blur-sm opacity-50" />
          {/* Celebration sparkles */}
          <div className="absolute top-0 left-1/4 w-2 h-2 bg-white rounded-full animate-particle opacity-60" />
          <div className="absolute top-0 left-1/2 w-1.5 h-1.5 bg-white rounded-full animate-particle opacity-40" style={{ animationDelay: '0.5s' }} />
          <div className="absolute top-0 left-3/4 w-2 h-2 bg-white rounded-full animate-particle opacity-60" style={{ animationDelay: '1s' }} />
        </div>
      )}

      {/* Error state */}
      {status === "error" && error && (
        <div className="relative">
          <div className="p-4 rounded-xl bg-destructive/10 border border-destructive/20">
            <p className="text-sm text-destructive/90">{error}</p>
          </div>
        </div>
      )}
    </div>
  );
}
