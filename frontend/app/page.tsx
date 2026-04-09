"use client";

import { useEffect, useRef, useState } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { gsap } from "gsap";
import {
  Activity,
  LogOut,
  MessageSquare,
  ShieldCheck,
  Sparkles,
  UserRound,
} from "lucide-react";

import { ChatInterface } from "@/components/chat/chat-interface";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { getCurrentUser, logout } from "@/lib/api/auth";
import type { User } from "@/types/auth";

const highlights = [
  {
    icon: ShieldCheck,
    title: "Compliance first",
    copy: "Enterprise guardrails, SOC 2 alignment, and per-tenant isolation.",
  },
  {
    icon: MessageSquare,
    title: "Business briefings",
    copy: "Multi-turn narratives tuned for leadership-ready summaries.",
  },
  {
    icon: Activity,
    title: "Usage telemetry",
    copy: "Token, latency, and source freshness metrics in real time.",
  },
];

export default function Home() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const gradientRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    getCurrentUser()
      .then(setUser)
      .catch(() => router.push("/auth/signin"))
      .finally(() => setLoading(false));
  }, [router]);

  useEffect(() => {
    if (!gradientRef.current) return;

    const ctx = gsap.context(() => {
      if (!gradientRef.current) return;
      gsap.to(gradientRef.current, {
        backgroundPosition: "200% 0%",
        duration: 18,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
      });
    }, gradientRef);

    return () => ctx.revert();
  }, []);

  if (loading) {
    return (
      <main className="amber-theme flex h-full flex-1 items-center justify-center overflow-hidden bg-[#0f0802]">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="rounded-3xl border border-amber-200/10 bg-white/5 px-6 py-4 text-sm uppercase tracking-[0.4rem] text-amber-100"
        >
          Preparing chat space…
        </motion.div>
      </main>
    );
  }

  const userDisplayName = user?.username ?? "Guest";

  return (
    <main className="amber-theme relative flex min-h-full flex-1 overflow-hidden">
      <div
        ref={gradientRef}
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(251,191,36,0.35),_transparent_60%),_linear-gradient(120deg,_rgba(17,10,6,0.9),_rgba(9,6,4,0.9))]"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 mix-blend-screen"
        style={{
          backgroundImage:
            "repeating-linear-gradient(45deg, rgba(255,255,255,0.04) 0, rgba(255,255,255,0.04) 1px, transparent 1px, transparent 6px)",
        }}
      />
      <div className="relative z-10 flex-1">
        <div className="mx-auto flex h-full max-w-6xl flex-col px-4 py-6 sm:px-6 lg:px-10">
          <div className="grid min-h-[calc(100vh-120px)] items-stretch gap-6 lg:grid-cols-[minmax(0,0.65fr)_minmax(0,1.35fr)]">
            <motion.section
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="flex flex-col justify-between gap-5 rounded-3xl border border-amber-100/10 bg-white/5/80 p-5 text-amber-100 backdrop-blur lg:max-w-[460px]"
            >
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className="rounded-2xl border border-amber-200/40 bg-[#201106]/80 p-3">
                    <Sparkles className="h-5 w-5 text-amber-300" />
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-[0.3em] text-amber-300/80">
                      Amber minimal
                    </p>
                    <p className="text-lg font-semibold leading-tight">Site RAG Chatspace</p>
                  </div>
                </div>
                <div className="space-y-2">
                  <p className="text-sm uppercase tracking-[0.4em] text-amber-200/70">Business subscription</p>
                  <h1 className="text-2xl font-semibold leading-snug text-amber-50">
                    Executive-ready answers sourced from your private corpus.
                  </h1>
                  <p className="text-sm text-amber-100/80">
                    Built for business subscribers who need audit-ready citations, per-seat controls, and instant insight without leaving the chat canvas.
                  </p>
                </div>
                <div className="grid gap-3 sm:grid-cols-2">
                  {highlights.slice(0, 2).map((highlight) => (
                    <div
                      key={highlight.title}
                      className="rounded-2xl border border-amber-200/20 bg-[#120902]/70 p-3 shadow-[0_4px_30px_rgba(251,191,36,0.12)]"
                    >
                      <highlight.icon className="mb-3 h-5 w-5 text-amber-300" />
                      <p className="text-sm font-medium text-amber-50">{highlight.title}</p>
                      <p className="text-xs text-amber-100/70">{highlight.copy}</p>
                    </div>
                  ))}
                </div>
              </div>
              <div className="flex items-center gap-3 rounded-3xl border border-amber-50/20 bg-[#120902]/70 p-4">
                <div className="shrink-0 overflow-hidden rounded-2xl border border-amber-50/10 bg-black/20">
                  <Image
                    src="/canva-1.png"
                    alt="Amber companion representing the chatbot"
                    width={160}
                    height={160}
                    sizes="160px"
                    priority
                    className="h-auto w-[140px] object-cover"
                  />
                </div>
                <div className="text-sm text-amber-100/80">
                  <p className="text-xs uppercase tracking-[0.3em] text-amber-200">Business concierge</p>
                  <p className="mt-2 font-semibold text-amber-50">Premium guidance</p>
                  <p>
                    This avatar signals the dedicated concierge included in every business subscription—your human-in-the-loop contact for escalations and rollout strategies.
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3 rounded-2xl border border-amber-200/10 bg-[#120902]/80 px-4 py-2 text-xs">
                <UserRound className="h-4 w-4 text-amber-200" />
                <div className="flex flex-col leading-tight">
                  <span className="text-xs uppercase tracking-wide text-amber-200/70">Signed in as</span>
                  <span className="font-medium text-amber-50">{userDisplayName}</span>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="ml-auto inline-flex items-center gap-2 rounded-xl border border-transparent text-amber-100 hover:border-amber-200/20 hover:bg-white/5"
                  onClick={() => {
                    logout();
                    router.push("/auth/signin");
                  }}
                >
                  <LogOut className="h-4 w-4" />
                  Sign out
                </Button>
              </div>
            </motion.section>

            <motion.section
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="flex h-full flex-col"
            >
              <Card className="flex h-full flex-col border-amber-100/15 bg-[#0a0503]/80 p-0 text-amber-50 shadow-[0_20px_60px_rgba(12,6,2,0.85)] backdrop-blur">
                <div className="rounded-t-2xl border-b border-amber-100/10 bg-gradient-to-r from-amber-500/10 to-transparent px-6 py-4">
                  <p className="text-sm uppercase tracking-[0.4em] text-amber-200/80">Chatbot console</p>
                  <p className="text-lg font-semibold text-amber-50">Explore your site knowledge base</p>
                </div>
                <div className="flex flex-1 flex-col p-1">
                  <div className="flex-1 rounded-[28px] border border-amber-50/10 bg-black/20 p-4">
                    <ChatInterface />
                  </div>
                </div>
              </Card>
            </motion.section>
          </div>
        </div>
      </div>
    </main>
  );
}
