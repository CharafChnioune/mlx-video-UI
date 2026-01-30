import { TrainingForm } from "@/components/training-form";
import { GraduationCap } from "lucide-react";

export default function TrainPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-7xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-12 relative">
          <div className="absolute inset-0 -top-20 spotlight pointer-events-none" />

          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card border border-primary/20 mb-6">
            <GraduationCap className="h-4 w-4 text-primary" />
            <span className="text-sm text-muted-foreground">MLX Trainer</span>
          </div>

          <h2 className="text-4xl sm:text-5xl font-bold mb-6 tracking-tight">
            Train Your{" "}
            <span className="gradient-text-animated inline-block">Models</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Fine-tune LTX-2 models with LoRA or full training. Optimized for Apple Silicon with MLX.
          </p>

          {/* Feature badges */}
          <div className="flex flex-wrap items-center justify-center gap-3 mt-8">
            <div className="flex items-center gap-2 px-4 py-2 rounded-full glass-card text-sm">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-muted-foreground">LoRA Training</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 rounded-full glass-card text-sm">
              <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
              <span className="text-muted-foreground">Full Fine-tuning</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 rounded-full glass-card text-sm">
              <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
              <span className="text-muted-foreground">Audio Support</span>
            </div>
          </div>
        </div>

        {/* Training Form */}
        <TrainingForm />
      </div>
    </div>
  );
}
