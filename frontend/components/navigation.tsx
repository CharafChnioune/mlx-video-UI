"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Sparkles, Video, GraduationCap, Image, Github, Apple, Menu, X } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";

const navItems = [
  {
    href: "/",
    label: "Generate",
    icon: Video,
    description: "Create AI videos",
  },
  {
    href: "/train",
    label: "Train",
    icon: GraduationCap,
    description: "Fine-tune models",
  },
  {
    href: "/gallery",
    label: "Gallery",
    icon: Image,
    description: "View creations",
  },
];

export function Navigation() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="relative border-b border-border/50 glass sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-primary to-purple-600 rounded-xl blur-lg opacity-50 group-hover:opacity-75 transition-opacity" />
              <div className="relative w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center glow-primary">
                <Sparkles className="h-5 w-5 text-white animate-icon-pulse" />
              </div>
            </div>
            <div>
              <h1 className="text-xl font-bold gradient-text-animated">MLX Video</h1>
              <p className="text-xs text-muted-foreground">
                LTX-2 on Apple Silicon
              </p>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`
                    relative flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium
                    transition-all duration-300
                    ${isActive
                      ? "text-primary bg-primary/10"
                      : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
                    }
                  `}
                >
                  <Icon className={`h-4 w-4 ${isActive ? 'animate-icon-pulse' : ''}`} />
                  <span>{item.label}</span>
                  {isActive && (
                    <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-1/2 h-0.5 bg-gradient-to-r from-primary to-purple-500 rounded-full" />
                  )}
                </Link>
              );
            })}
          </nav>

          {/* Right side items */}
          <div className="flex items-center gap-4">
            <a
              href="https://github.com/CharafChnioune/mlx-video"
              target="_blank"
              rel="noopener noreferrer"
              className="hidden sm:flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-all duration-300 hover:scale-105"
            >
              <Github className="h-4 w-4" />
              <span className="hidden lg:inline">GitHub</span>
            </a>
            <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full glass text-xs border border-primary/20">
              <Apple className="h-3.5 w-3.5 text-primary" />
              <span className="gradient-text font-medium">MLX Optimized</span>
            </div>

            {/* Mobile menu button */}
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? (
                <X className="h-5 w-5" />
              ) : (
                <Menu className="h-5 w-5" />
              )}
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <nav className="md:hidden mt-4 pb-2 border-t border-border/50 pt-4 animate-in slide-in-from-top-2 duration-200">
            <div className="flex flex-col gap-2">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`
                      flex items-center gap-3 px-4 py-3 rounded-xl
                      transition-all duration-300
                      ${isActive
                        ? "text-primary bg-primary/10 glow-primary"
                        : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
                      }
                    `}
                  >
                    <div className={`p-2 rounded-lg ${isActive ? 'bg-primary/20' : 'bg-secondary/50'}`}>
                      <Icon className="h-4 w-4" />
                    </div>
                    <div>
                      <span className="font-medium">{item.label}</span>
                      <p className="text-xs text-muted-foreground">{item.description}</p>
                    </div>
                  </Link>
                );
              })}
            </div>
            <div className="flex items-center justify-center gap-4 mt-4 pt-4 border-t border-border/50">
              <a
                href="https://github.com/CharafChnioune/mlx-video"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
              >
                <Github className="h-4 w-4" />
                GitHub
              </a>
              <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full glass text-xs border border-primary/20">
                <Apple className="h-3.5 w-3.5 text-primary" />
                <span className="gradient-text font-medium">MLX</span>
              </div>
            </div>
          </nav>
        )}
      </div>
    </header>
  );
}
