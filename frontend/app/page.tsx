import { VideoGenerator } from "@/components/video-generator";

export default function Home() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-7xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-16 relative">
          {/* Spotlight effect behind hero */}
          <div className="absolute inset-0 -top-20 spotlight pointer-events-none" />

          {/* Decorative elements */}
          <div className="absolute left-1/2 -translate-x-1/2 top-0 -translate-y-1/2 w-32 h-32 bg-gradient-to-br from-primary/20 to-purple-600/20 rounded-full blur-3xl" />

          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6 tracking-tight">
            Generate AI Videos with{" "}
            <span className="gradient-text-animated inline-block">LTX-2</span>
          </h2>
          <p className="text-lg sm:text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
            Create stunning AI-generated videos using state-of-the-art LTX-2
            models, optimized for{" "}
            <span className="text-foreground font-medium">Apple Silicon</span> with MLX.
            Fast (Slow), local, and private.
          </p>

          {/* Feature badges */}
          <div className="flex flex-wrap items-center justify-center gap-3 mt-8">
            <div className="flex items-center gap-2 px-4 py-2 rounded-full glass-card text-sm">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-muted-foreground">100% Local</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 rounded-full glass-card text-sm">
              <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
              <span className="text-muted-foreground">GPU Accelerated</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 rounded-full glass-card text-sm">
              <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
              <span className="text-muted-foreground">No API Keys</span>
            </div>
          </div>
        </div>

        {/* Video Generator */}
        <VideoGenerator />
      </div>
    </div>
  );
}
