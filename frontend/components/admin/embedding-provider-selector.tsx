"use client";

import { useState, useEffect } from "react";
import {
  getEmbeddingProvider,
  updateEmbeddingProvider,
  type ConfigResponse,
} from "@/lib/api/admin";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

/**
 * EmbeddingProviderSelector component for selecting embedding provider.
 * Allows administrators to switch between OpenAI and sentence-transformers.
 */
export function EmbeddingProviderSelector() {
  const [config, setConfig] = useState<ConfigResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    loadProvider();
  }, []);

  const loadProvider = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getEmbeddingProvider();
      setConfig(response);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load embedding provider"
      );
    } finally {
      setLoading(false);
    }
  };

  const handleChange = async (value: "openai" | "local") => {
    if (!config || config.embedding_provider === value) {
      return;
    }

    setUpdating(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await updateEmbeddingProvider(value);
      setConfig(response);
      setSuccess(
        `Embedding provider updated to ${response.available_providers.find((p) => p.value === value)?.label || value}. Change will take effect on next ingestion.`
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to update embedding provider"
      );
    } finally {
      setUpdating(false);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Embedding Provider</CardTitle>
          <CardDescription>Loading configuration...</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  if (!config) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Embedding Provider</CardTitle>
          <CardDescription>Failed to load configuration</CardDescription>
        </CardHeader>
        <CardContent>
          {error && (
            <p className="text-sm text-destructive" role="alert">
              {error}
            </p>
          )}
          <Button onClick={loadProvider} variant="outline" className="mt-2">
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  const currentProvider = config.embedding_provider || "auto-detect";

  return (
    <Card>
      <CardHeader>
        <CardTitle>Embedding Provider</CardTitle>
        <CardDescription>
          Select the embedding provider for generating vector embeddings. Change
          takes effect on next ingestion operation.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <p className="text-sm font-medium mb-2">Current Provider:</p>
          <p className="text-sm text-muted-foreground">
            {currentProvider === "auto-detect"
              ? "Auto-detect (based on API key availability)"
              : config.available_providers.find(
                  (p) => p.value === currentProvider
                )?.label || currentProvider}
          </p>
          {config.embedding_model && (
            <p className="text-xs text-muted-foreground mt-1">
              Model: {config.embedding_model}
            </p>
          )}
        </div>

        <div className="space-y-2">
          <p className="text-sm font-medium">Available Providers:</p>
          {config.available_providers.map((provider) => (
            <div
              key={provider.value}
              className="flex items-start justify-between p-3 border rounded-lg"
            >
              <div className="flex-1">
                <p className="text-sm font-medium">{provider.label}</p>
                {provider.description && (
                  <p className="text-xs text-muted-foreground mt-1">
                    {provider.description}
                  </p>
                )}
              </div>
              <Button
                onClick={() => handleChange(provider.value)}
                disabled={
                  updating ||
                  config.embedding_provider === provider.value ||
                  loading
                }
                variant={
                  config.embedding_provider === provider.value
                    ? "default"
                    : "outline"
                }
                size="sm"
              >
                {updating && config.embedding_provider !== provider.value
                  ? "Updating..."
                  : config.embedding_provider === provider.value
                  ? "Current"
                  : "Select"}
              </Button>
            </div>
          ))}
        </div>

        {error && (
          <div className="p-3 bg-destructive/10 rounded-md">
            <p className="text-sm text-destructive" role="alert">
              {error}
            </p>
          </div>
        )}

        {success && (
          <div className="p-3 bg-green-50 dark:bg-green-950 rounded-md">
            <p className="text-sm text-green-700 dark:text-green-300" role="alert">
              {success}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

