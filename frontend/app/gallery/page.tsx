import { GalleryGrid } from "@/components/gallery-grid";
import { Film } from "lucide-react";

export default function GalleryPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-7xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-12 relative">
          <div className="absolute inset-0 -top-20 spotlight pointer-events-none" />

          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card border border-primary/20 mb-6">
            <Film className="h-4 w-4 text-primary" />
            <span className="text-sm text-muted-foreground">Video Gallery</span>
          </div>

          <h2 className="text-4xl sm:text-5xl font-bold mb-6 tracking-tight">
            Your{" "}
            <span className="gradient-text-animated inline-block">Creations</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Browse, preview, and manage all your AI-generated videos in one place.
          </p>

          {/* Feature badges */}
          <div className="flex flex-wrap items-center justify-center gap-3 mt-8">
            <div className="flex items-center gap-2 px-4 py-2 rounded-full glass-card text-sm">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-muted-foreground">Quick Preview</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 rounded-full glass-card text-sm">
              <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
              <span className="text-muted-foreground">Easy Download</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 rounded-full glass-card text-sm">
              <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
              <span className="text-muted-foreground">Smart Filtering</span>
            </div>
          </div>
        </div>

        {/* Gallery Grid */}
        <GalleryGrid />
      </div>
    </div>
  );
}
