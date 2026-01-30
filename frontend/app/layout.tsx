import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Navigation } from "@/components/navigation";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "MLX Video Generator",
  description: "Generate AI videos with LTX-2 on Apple Silicon",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <TooltipProvider>
          <div className="min-h-screen bg-background relative overflow-hidden">
            {/* Background layers */}
            <div className="fixed inset-0 bg-gradient-to-br from-primary/5 via-background to-purple-900/5 pointer-events-none" />
            <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/10 via-transparent to-transparent pointer-events-none" />

            {/* Animated grid background */}
            <div className="fixed inset-0 bg-grid opacity-50 pointer-events-none" />

            {/* Floating orbs */}
            <div className="fixed inset-0 pointer-events-none overflow-hidden">
              <div
                className="orb orb-primary w-[500px] h-[500px] -top-48 -right-48 animate-float-slow"
                style={{ animationDelay: "0s" }}
              />
              <div
                className="orb orb-secondary w-[400px] h-[400px] -bottom-32 -left-32 animate-float-reverse"
                style={{ animationDelay: "2s" }}
              />
              <div
                className="orb orb-accent w-[300px] h-[300px] top-1/2 -right-24 animate-float"
                style={{ animationDelay: "1s" }}
              />
              <div
                className="orb orb-primary w-[200px] h-[200px] top-32 left-1/4 animate-float-slow opacity-50"
                style={{ animationDelay: "3s" }}
              />
            </div>

            {/* Navigation */}
            <Navigation />

            {/* Main content */}
            <main className="relative">{children}</main>

            {/* Footer */}
            <footer className="relative border-t border-border/50 mt-16 glass">
              <div className="container mx-auto px-4 py-6">
                <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
                  <p className="flex items-center gap-2">
                    Powered by{" "}
                    <span className="gradient-text font-medium">MLX</span> and{" "}
                    <span className="gradient-text font-medium">LTX-2</span>
                  </p>
                  <div className="flex items-center gap-4">
                    <a
                      href="https://huggingface.co/Amlxcommunity"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="hover:text-foreground transition-colors hover:scale-105 transform"
                    >
                      Models on HuggingFace
                    </a>
                  </div>
                </div>
              </div>
            </footer>
          </div>
        </TooltipProvider>
      </body>
    </html>
  );
}
