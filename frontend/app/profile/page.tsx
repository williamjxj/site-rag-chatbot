"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
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
      <main className="container mx-auto p-8">
        <p className="text-muted-foreground">Loading...</p>
      </main>
    );
  }

  return (
    <main className="container mx-auto p-8 max-w-2xl">
      <h1 className="text-3xl font-bold mb-6">My Profile</h1>
      
      <div className="bg-card border rounded-lg p-6">
        <div className="space-y-4">
          <div className="flex justify-between border-b pb-4">
            <span className="text-muted-foreground">Username</span>
            <span className="font-medium">{user?.username}</span>
          </div>
          
          <div className="flex justify-between border-b pb-4">
            <span className="text-muted-foreground">Email</span>
            <span className="font-medium">{user?.email}</span>
          </div>
          
          <div className="flex justify-between border-b pb-4">
            <span className="text-muted-foreground">Full Name</span>
            <span className="font-medium">{user?.full_name || "Not set"}</span>
          </div>
          
          <div className="flex justify-between border-b pb-4">
            <span className="text-muted-foreground">Account Status</span>
            <span className={`font-medium ${user?.is_active ? "text-green-600" : "text-red-600"}`}>
              {user?.is_active ? "Active" : "Inactive"}
            </span>
          </div>
          
          <div className="flex justify-between">
            <span className="text-muted-foreground">Member Since</span>
            <span className="font-medium">
              {user?.created_at ? new Date(user.created_at).toLocaleDateString() : "N/A"}
            </span>
          </div>
        </div>
        
        <div className="mt-6 pt-4 border-t">
          <button
            onClick={() => {
              logout();
              router.push("/auth/signin");
            }}
            className="px-4 py-2 bg-destructive text-destructive-foreground rounded hover:bg-destructive/90"
          >
            Sign Out
          </button>
        </div>
      </div>
    </main>
  );
}