"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ContentManagementTab } from "@/components/admin/content-management-tab";
import { SettingsTab } from "@/components/admin/settings-tab";
import { SystemStatusTab } from "@/components/admin/system-status-tab";
import { getCurrentUser, logout } from "@/lib/api/auth";
import type { User } from "@/types/auth";

/**
 * AdminPage component with organized tabs for content management.
 * Three tabs: Content Management, Settings, System Status
 */
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
      <main className="container mx-auto p-8">
        <p className="text-muted-foreground">Loading...</p>
      </main>
    );
  }

  return (
    <main className="container mx-auto p-8">
      <header className="mb-6 flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold">Admin - Content Management</h1>
          <p className="text-muted-foreground mt-2">
            Manage knowledge base content and configure settings
          </p>
        </div>
        <button
          onClick={() => {
            logout();
            router.push("/auth/signin");
          }}
          className="text-sm text-muted-foreground hover:text-foreground"
        >
          Sign Out ({user?.username})
        </button>
      </header>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList>
          <TabsTrigger value="content">Content Management</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
          <TabsTrigger value="status">System Status</TabsTrigger>
        </TabsList>
        <TabsContent value="content" className="mt-6">
          <ContentManagementTab key={activeTab === "content" ? "active" : "inactive"} />
        </TabsContent>
        <TabsContent value="settings" className="mt-6">
          <SettingsTab />
        </TabsContent>
        <TabsContent value="status" className="mt-6">
          <SystemStatusTab />
        </TabsContent>
      </Tabs>
    </main>
  );
}
