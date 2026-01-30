"use client";

import { useState, useEffect, useCallback } from "react";
import {
  listVideos,
  deleteVideo,
  getVideoUrl,
  getVideoThumbnailUrl,
  GalleryVideo,
} from "@/lib/api";
import {
  Play,
  Download,
  Trash2,
  X,
  Calendar,
  Clock,
  Maximize2,
  Film,
  Search,
  SortAsc,
  SortDesc,
  RefreshCw,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  Copy,
  Check,
  Loader2,
} from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

type SortField = "created_at" | "size" | "duration";
type SortDirection = "asc" | "desc";

export function GalleryGrid() {
  const [videos, setVideos] = useState<GalleryVideo[]>([]);
  const [filteredVideos, setFilteredVideos] = useState<GalleryVideo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [sortField, setSortField] = useState<SortField>("created_at");
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc");
  const [selectedVideo, setSelectedVideo] = useState<GalleryVideo | null>(null);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [copiedPrompt, setCopiedPrompt] = useState(false);

  // Fetch videos
  const fetchVideos = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listVideos();
      setVideos(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load videos");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchVideos();
  }, [fetchVideos]);

  // Filter and sort videos
  useEffect(() => {
    let result = [...videos];

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(
        (video) =>
          video.filename.toLowerCase().includes(query) ||
          video.prompt?.toLowerCase().includes(query)
      );
    }

    // Sort
    result.sort((a, b) => {
      let comparison = 0;
      switch (sortField) {
        case "created_at":
          comparison =
            new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
          break;
        case "size":
          comparison = (a.size || 0) - (b.size || 0);
          break;
        case "duration":
          comparison = (a.duration || 0) - (b.duration || 0);
          break;
      }
      return sortDirection === "asc" ? comparison : -comparison;
    });

    setFilteredVideos(result);
  }, [videos, searchQuery, sortField, sortDirection]);

  // Handle delete
  const handleDelete = async (video: GalleryVideo) => {
    if (!confirm("Are you sure you want to delete this video?")) return;

    setDeleting(video.id);
    try {
      await deleteVideo(video.id);
      setVideos((prev) => prev.filter((v) => v.id !== video.id));
      if (selectedVideo?.id === video.id) {
        setSelectedVideo(null);
      }
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to delete video");
    } finally {
      setDeleting(null);
    }
  };

  // Handle download
  const handleDownload = (video: GalleryVideo) => {
    const link = document.createElement("a");
    link.href = getVideoUrl(video.filename);
    link.download = video.filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Copy prompt to clipboard
  const copyPrompt = async (prompt: string) => {
    await navigator.clipboard.writeText(prompt);
    setCopiedPrompt(true);
    setTimeout(() => setCopiedPrompt(false), 2000);
  };

  // Navigate between videos in modal
  const navigateVideo = (direction: "prev" | "next") => {
    if (!selectedVideo) return;
    const currentIndex = filteredVideos.findIndex(
      (v) => v.id === selectedVideo.id
    );
    const newIndex =
      direction === "prev"
        ? (currentIndex - 1 + filteredVideos.length) % filteredVideos.length
        : (currentIndex + 1) % filteredVideos.length;
    setSelectedVideo(filteredVideos[newIndex]);
  };

  // Format file size
  const formatSize = (bytes?: number) => {
    if (!bytes) return "Unknown";
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(1)} MB`;
  };

  // Format date
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  // Format duration
  const formatDuration = (seconds?: number) => {
    if (!seconds) return "Unknown";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return mins > 0 ? `${mins}:${secs.toString().padStart(2, "0")}` : `${secs}s`;
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="relative">
          <div className="w-16 h-16 rounded-full border-4 border-primary/20 border-t-primary animate-spin" />
          <Film className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-6 h-6 text-primary" />
        </div>
        <p className="mt-4 text-muted-foreground">Loading your videos...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-20 glass-card rounded-2xl">
        <AlertCircle className="w-12 h-12 text-red-500 mb-4" />
        <p className="text-lg font-medium mb-2">Failed to load videos</p>
        <p className="text-muted-foreground mb-4">{error}</p>
        <button
          onClick={fetchVideos}
          className="px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Toolbar */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        {/* Search */}
        <div className="relative w-full sm:w-80">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search by filename or prompt..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-lg glass-card border border-border/50 bg-transparent focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
          />
        </div>

        {/* Sort & Refresh */}
        <div className="flex items-center gap-2">
          <select
            value={sortField}
            onChange={(e) => setSortField(e.target.value as SortField)}
            className="px-3 py-2 rounded-lg glass-card border border-border/50 bg-transparent focus:outline-none focus:ring-2 focus:ring-primary/50 text-sm"
          >
            <option value="created_at">Date</option>
            <option value="size">Size</option>
            <option value="duration">Duration</option>
          </select>

          <button
            onClick={() =>
              setSortDirection((d) => (d === "asc" ? "desc" : "asc"))
            }
            className="p-2 rounded-lg glass-card border border-border/50 hover:bg-accent/50 transition-colors"
          >
            {sortDirection === "asc" ? (
              <SortAsc className="w-4 h-4" />
            ) : (
              <SortDesc className="w-4 h-4" />
            )}
          </button>

          <button
            onClick={fetchVideos}
            className="p-2 rounded-lg glass-card border border-border/50 hover:bg-accent/50 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Video count */}
      <p className="text-sm text-muted-foreground">
        {filteredVideos.length} video{filteredVideos.length !== 1 ? "s" : ""}
        {searchQuery && ` matching "${searchQuery}"`}
      </p>

      {/* Grid */}
      {filteredVideos.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 glass-card rounded-2xl">
          <Film className="w-16 h-16 text-muted-foreground/50 mb-4" />
          <p className="text-lg font-medium mb-2">No videos yet</p>
          <p className="text-muted-foreground text-center max-w-md">
            {searchQuery
              ? "No videos match your search. Try different keywords."
              : "Start generating videos to see them appear here!"}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredVideos.map((video) => (
            <div
              key={video.id}
              className="group relative glass-card rounded-xl overflow-hidden border border-border/50 hover:border-primary/50 transition-all duration-300 hover:scale-[1.02] hover:shadow-lg hover:shadow-primary/10"
            >
              {/* Thumbnail */}
              <div
                className="relative aspect-video bg-muted cursor-pointer"
                onClick={() => setSelectedVideo(video)}
              >
                {video.thumbnail ? (
                  <img
                    src={getVideoThumbnailUrl(video.filename)}
                    alt={video.filename}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-primary/10 to-purple-600/10">
                    <Film className="w-12 h-12 text-muted-foreground/50" />
                  </div>
                )}

                {/* Play overlay */}
                <div className="absolute inset-0 flex items-center justify-center bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity">
                  <div className="w-14 h-14 rounded-full bg-primary/90 flex items-center justify-center transform scale-90 group-hover:scale-100 transition-transform">
                    <Play className="w-6 h-6 text-primary-foreground ml-1" />
                  </div>
                </div>

                {/* Duration badge */}
                {video.duration && (
                  <div className="absolute bottom-2 right-2 px-2 py-1 rounded bg-black/70 text-xs text-white">
                    {formatDuration(video.duration)}
                  </div>
                )}
              </div>

              {/* Info */}
              <div className="p-4 space-y-2">
                <p className="font-medium text-sm truncate" title={video.filename}>
                  {video.filename}
                </p>

                {video.prompt && (
                  <p
                    className="text-xs text-muted-foreground line-clamp-2"
                    title={video.prompt}
                  >
                    {video.prompt}
                  </p>
                )}

                <div className="flex items-center gap-3 text-xs text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    {new Date(video.created_at).toLocaleDateString()}
                  </span>
                  {video.width && video.height && (
                    <span className="flex items-center gap-1">
                      <Maximize2 className="w-3 h-3" />
                      {video.width}x{video.height}
                    </span>
                  )}
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 pt-2">
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <button
                        onClick={() => handleDownload(video)}
                        className="flex-1 flex items-center justify-center gap-1 px-3 py-2 rounded-lg bg-accent/50 hover:bg-accent transition-colors text-sm"
                      >
                        <Download className="w-4 h-4" />
                        Download
                      </button>
                    </TooltipTrigger>
                    <TooltipContent>Download video</TooltipContent>
                  </Tooltip>

                  <Tooltip>
                    <TooltipTrigger asChild>
                      <button
                        onClick={() => handleDelete(video)}
                        disabled={deleting === video.id}
                        className="p-2 rounded-lg hover:bg-red-500/20 text-red-500 transition-colors disabled:opacity-50"
                      >
                        {deleting === video.id ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <Trash2 className="w-4 h-4" />
                        )}
                      </button>
                    </TooltipTrigger>
                    <TooltipContent>Delete video</TooltipContent>
                  </Tooltip>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Video Modal */}
      {selectedVideo && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
          onClick={() => setSelectedVideo(null)}
        >
          <div
            className="relative w-full max-w-5xl mx-4 glass-intense rounded-2xl overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close button */}
            <button
              onClick={() => setSelectedVideo(null)}
              className="absolute top-4 right-4 z-10 p-2 rounded-full bg-black/50 hover:bg-black/70 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            {/* Navigation arrows */}
            {filteredVideos.length > 1 && (
              <>
                <button
                  onClick={() => navigateVideo("prev")}
                  className="absolute left-4 top-1/2 -translate-y-1/2 z-10 p-2 rounded-full bg-black/50 hover:bg-black/70 transition-colors"
                >
                  <ChevronLeft className="w-6 h-6" />
                </button>
                <button
                  onClick={() => navigateVideo("next")}
                  className="absolute right-4 top-1/2 -translate-y-1/2 z-10 p-2 rounded-full bg-black/50 hover:bg-black/70 transition-colors"
                >
                  <ChevronRight className="w-6 h-6" />
                </button>
              </>
            )}

            {/* Video player */}
            <div className="aspect-video bg-black">
              <video
                src={getVideoUrl(selectedVideo.filename)}
                controls
                autoPlay
                className="w-full h-full"
              />
            </div>

            {/* Video info */}
            <div className="p-6 space-y-4">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <h3 className="text-lg font-semibold truncate">
                    {selectedVideo.filename}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {formatDate(selectedVideo.created_at)}
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleDownload(selectedVideo)}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
                  >
                    <Download className="w-4 h-4" />
                    Download
                  </button>
                  <button
                    onClick={() => handleDelete(selectedVideo)}
                    disabled={deleting === selectedVideo.id}
                    className="p-2 rounded-lg hover:bg-red-500/20 text-red-500 transition-colors"
                  >
                    {deleting === selectedVideo.id ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Trash2 className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>

              {/* Prompt */}
              {selectedVideo.prompt && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium">Prompt</p>
                    <button
                      onClick={() => copyPrompt(selectedVideo.prompt!)}
                      className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
                    >
                      {copiedPrompt ? (
                        <>
                          <Check className="w-3 h-3 text-green-500" />
                          Copied!
                        </>
                      ) : (
                        <>
                          <Copy className="w-3 h-3" />
                          Copy
                        </>
                      )}
                    </button>
                  </div>
                  <p className="text-sm text-muted-foreground bg-accent/30 rounded-lg p-3">
                    {selectedVideo.prompt}
                  </p>
                </div>
              )}

              {/* Metadata grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                {selectedVideo.width && selectedVideo.height && (
                  <div className="glass-card rounded-lg p-3">
                    <p className="text-muted-foreground text-xs mb-1">Resolution</p>
                    <p className="font-medium">
                      {selectedVideo.width}x{selectedVideo.height}
                    </p>
                  </div>
                )}
                {selectedVideo.duration && (
                  <div className="glass-card rounded-lg p-3">
                    <p className="text-muted-foreground text-xs mb-1">Duration</p>
                    <p className="font-medium">
                      {formatDuration(selectedVideo.duration)}
                    </p>
                  </div>
                )}
                {selectedVideo.size && (
                  <div className="glass-card rounded-lg p-3">
                    <p className="text-muted-foreground text-xs mb-1">Size</p>
                    <p className="font-medium">{formatSize(selectedVideo.size)}</p>
                  </div>
                )}
                {selectedVideo.params?.pipeline && (
                  <div className="glass-card rounded-lg p-3">
                    <p className="text-muted-foreground text-xs mb-1">Pipeline</p>
                    <p className="font-medium capitalize">
                      {selectedVideo.params.pipeline}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
