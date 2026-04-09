"use client";

import { ChatInterface } from "@/components/chat/chat-interface";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getCurrentUser, logout } from "@/lib/api/auth";
import type { User } from "@/types/auth";

export default function Home() {
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
      <main className="h-full flex flex-col items-center justify-center">
        <p className="text-muted-foreground">Loading...</p>
      </main>
    );
  }

  return (
    <main className="h-full flex flex-col">
      <div className="container mx-auto flex-1 flex flex-col min-h-0">
        <div className="border-b p-4 flex-shrink-0 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold">Site RAG Chatbot</h1>
            <p className="text-sm text-muted-foreground">
              Ask questions about the website content
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
        </div>
        <div className="flex-1 min-h-0">
          <ChatInterface />
        </div>
      </div>
    </main>
  );
}
