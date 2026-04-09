"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { LogOut, ShieldCheck, Sparkles } from "lucide-react";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ContentManagementTab } from "@/components/admin/content-management-tab";
import { SettingsTab } from "@/components/admin/settings-tab";
import { SystemStatusTab } from "@/components/admin/system-status-tab";
import { Button } from "@/components/ui/button";
import { getCurrentUser, logout } from "@/lib/api/auth";
import type { User } from "@/types/auth";

export default function AdminPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("content");

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
          Loading admin…
        </p>
      </main>
    );
  }

  return (
    <main className="amber-theme relative flex min-h-full flex-1 overflow-hidden">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(251,191,36,0.25),_transparent_65%),_linear-gradient(140deg,_rgba(17,10,6,0.95),_rgba(9,6,4,0.95))]"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 mix-blend-screen"
        style={{
          backgroundImage:
            "repeating-linear-gradient(60deg, rgba(255,255,255,0.03) 0, rgba(255,255,255,0.03) 1px, transparent 1px, transparent 8px)",
        }}
      />
      <div className="relative z-10 flex-1">
        <div className="mx-auto flex h-full max-w-6xl flex-col gap-8 px-4 py-8 sm:px-6 lg:px-10">
          <motion.header
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="rounded-3xl border border-amber-50/15 bg-[#140903]/70 p-6 text-amber-50 backdrop-blur"
          >
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <div className="mb-2 inline-flex items-center gap-2 rounded-full border border-amber-100/20 px-3 py-1 text-xs uppercase tracking-[0.35em] text-amber-200/80">
                  <Sparkles className="h-3.5 w-3.5" />
                  Business ops
                </div>
                <h1 className="text-3xl font-semibold">Business subscription control room</h1>
                <p className="text-amber-100/80">
                  Govern ingestion, provider mix, and uptime SLAs across every business tenant from a single amber dashboard.
                </p>
              </div>
              <div className="flex items-center gap-3 rounded-2xl border border-amber-100/15 bg-black/30 px-4 py-3 text-sm">
                <ShieldCheck className="h-5 w-5 text-amber-300" />
                <div className="text-left">
                  <p className="text-xs uppercase tracking-[0.3em] text-amber-200/70">Operator</p>
                  <p className="font-medium text-amber-50">{user?.username}</p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="ml-2 inline-flex items-center gap-2 rounded-xl text-amber-50 hover:bg-white/10"
                  onClick={() => {
                    logout();
                    router.push("/auth/signin");
                  }}
                >
                  <LogOut className="h-4 w-4" />
                  Sign out
                </Button>
              </div>
            </div>
          </motion.header>

          <motion.section
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55, delay: 0.05 }}
            className="flex-1 rounded-3xl border border-amber-50/15 bg-[#0b0503]/80 p-6 text-amber-50 backdrop-blur"
          >
            <Tabs value={activeTab} onValueChange={setActiveTab} className="flex h-full flex-col">
              <TabsList className="mb-6 rounded-2xl border border-amber-100/20 bg-black/30 p-1">
                <TabsTrigger value="content" className="data-[state=active]:bg-[#1d0f05] data-[state=active]:text-amber-50">
                  Content
                </TabsTrigger>
                <TabsTrigger value="settings" className="data-[state=active]:bg-[#1d0f05] data-[state=active]:text-amber-50">
                  Settings
                </TabsTrigger>
                <TabsTrigger value="status" className="data-[state=active]:bg-[#1d0f05] data-[state=active]:text-amber-50">
                  System Status
                </TabsTrigger>
              </TabsList>
              <div className="flex-1 overflow-hidden rounded-2xl border border-amber-100/10 bg-black/20 p-4">
                <TabsContent value="content" className="h-full overflow-y-auto">
                  <ContentManagementTab key={activeTab === "content" ? "active" : "inactive"} />
                </TabsContent>
                <TabsContent value="settings" className="h-full overflow-y-auto">
                  <SettingsTab />
                </TabsContent>
                <TabsContent value="status" className="h-full overflow-y-auto">
                  <SystemStatusTab />
                </TabsContent>
              </div>
            </Tabs>
          </motion.section>
        </div>
      </div>
    </main>
  );
}
