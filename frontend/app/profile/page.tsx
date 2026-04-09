"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { CalendarDays, LogOut, ShieldCheck, UserRound } from "lucide-react";

import { Button } from "@/components/ui/button";
import { getCurrentUser, logout } from "@/lib/api/auth";
import type { User } from "@/types/auth";

export default function ProfilePage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCurrentUser()
      .then(setUser)
      .catch(() => router.push("/auth/signin"))
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) {
    return (
      <main className="amber-theme flex h-full flex-1 items-center justify-center bg-[#0f0802]">
        <p className="rounded-2xl border border-amber-100/10 bg-white/5 px-4 py-2 text-sm uppercase tracking-[0.3em] text-amber-100">
          Loading profile…
        </p>
      </main>
    );
  }

  const statusText = user?.is_active ? "Active" : "Inactive";
  const statusColor = user?.is_active ? "text-emerald-300" : "text-red-300";

  return (
    <main className="amber-theme relative flex min-h-full flex-1 overflow-hidden">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(251,191,36,0.3),_transparent_65%),_linear-gradient(150deg,_rgba(14,8,4,0.95),_rgba(6,4,3,0.95))]"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 mix-blend-screen"
        style={{
          backgroundImage:
            "repeating-linear-gradient(35deg, rgba(255,255,255,0.03) 0, rgba(255,255,255,0.03) 1px, transparent 1px, transparent 7px)",
        }}
      />
      <div className="relative z-10 flex-1">
        <div className="mx-auto flex h-full w-full max-w-3xl flex-col px-4 py-8 sm:px-6 lg:px-10">
          <motion.section
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="rounded-3xl border border-amber-50/15 bg-[#120903]/80 p-8 text-amber-50 backdrop-blur"
          >
            <div className="flex flex-col gap-6">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-center gap-3">
                  <div className="rounded-2xl border border-amber-100/20 bg-black/30 p-3">
                    <UserRound className="h-6 w-6 text-amber-200" />
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-[0.3em] text-amber-200/80">Business seat</p>
                    <h1 className="text-3xl font-semibold">Subscriber workspace</h1>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  className="inline-flex items-center gap-2 rounded-xl border border-amber-50/20 text-amber-50 hover:bg-white/10"
                  onClick={() => {
                    logout();
                    router.push("/auth/signin");
                  }}
                >
                  <LogOut className="h-4 w-4" />
                  Sign out
                </Button>
              </div>

              <div className="grid gap-4 rounded-3xl border border-amber-50/10 bg-black/20 p-6 sm:grid-cols-2">
                <div>
                  <p className="text-xs uppercase tracking-[0.3em] text-amber-200/70">Username</p>
                  <p className="mt-2 text-lg font-medium">{user?.username}</p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-[0.3em] text-amber-200/70">Email</p>
                  <p className="mt-2 text-lg font-medium">{user?.email}</p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-[0.3em] text-amber-200/70">Full Name</p>
                  <p className="mt-2 text-lg font-medium">{user?.full_name || "Not set"}</p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-[0.3em] text-amber-200/70">Subscription tier</p>
                  <p className={`mt-2 text-lg font-semibold ${statusColor}`}>{statusText} · Business</p>
                </div>
              </div>

              <div className="grid gap-4 rounded-3xl border border-amber-50/10 bg-black/20 p-6 sm:grid-cols-2">
                <div className="flex items-center gap-3">
                  <ShieldCheck className="h-6 w-6 text-amber-300" />
                  <div>
                    <p className="text-xs uppercase tracking-[0.3em] text-amber-200/70">Security posture</p>
                    <p className="mt-1 text-base font-medium">Session verified · Business SLA</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <CalendarDays className="h-6 w-6 text-amber-300" />
                  <div>
                    <p className="text-xs uppercase tracking-[0.3em] text-amber-200/70">Member since</p>
                    <p className="mt-1 text-base font-medium">
                      {user?.created_at ? new Date(user.created_at).toLocaleDateString() : "N/A"}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </motion.section>
        </div>
      </div>
    </main>
  );
}
