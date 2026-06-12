"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import Link from "next/link";
import { Sparkles, ArrowRight } from "lucide-react";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-background flex flex-col items-center justify-center text-center px-4 relative overflow-hidden">
      {/* Glow blobs */}
      <div className="absolute -top-60 -left-60 w-[700px] h-[700px] rounded-full bg-primary/5 blur-3xl -z-10" />
      <div className="absolute -bottom-60 -right-60 w-[700px] h-[700px] rounded-full bg-primary/5 blur-3xl -z-10" />

      <div className="flex items-center justify-center w-16 h-16 rounded-2xl bg-primary/10 border border-primary/20 mb-6">
        <Sparkles className="w-8 h-8 text-primary" />
      </div>

      <h1 className="text-5xl sm:text-6xl font-extrabold tracking-tight mb-4 max-w-3xl">
        AI-Powered Language{" "}
        <span className="text-primary">Translation</span>
      </h1>
      <p className="text-muted-foreground text-lg max-w-xl mb-10">
        Translate across 100+ languages with GPT-4o, Gemini, and DeepSeek — with
        tone control, confidence scores, and full history.
      </p>

      <div className="flex flex-col sm:flex-row gap-4">
        <Link
          href="/register"
          className="flex items-center gap-2 bg-primary text-primary-foreground px-7 py-3 rounded-xl font-semibold hover:bg-primary/90 transition"
        >
          Get Started Free
          <ArrowRight className="w-4 h-4" />
        </Link>
        <Link
          href="/login"
          className="flex items-center gap-2 bg-secondary text-secondary-foreground px-7 py-3 rounded-xl font-semibold hover:bg-secondary/80 transition border"
        >
          Sign In
        </Link>
      </div>
    </main>
  );
}
