"use client";

import { EmbeddingProviderSelector } from "@/components/admin/embedding-provider-selector";

/**
 * SettingsTab component for application configuration settings.
 * Contains embedding provider selector and other settings.
 */
export function SettingsTab() {
  return (
    <div className="space-y-6">
      <EmbeddingProviderSelector />
    </div>
  );
}

