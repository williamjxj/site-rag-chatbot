"use client";

import { useState } from "react";
import { triggerIngestion } from "@/lib/api/ingest";
import { Button } from "@/components/ui/button";

interface IngestionStatusProps {
  onIngestComplete?: () => void;
}

export function IngestionStatus({ onIngestComplete }: IngestionStatusProps) {
  const [isIngesting, setIsIngesting] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleIngest = async (source: "web" | "file" | "all" = "all") => {
    setIsIngesting(true);
    setStatus(null);
    setError(null);

    try {
      const response = await triggerIngestion({ source });
      setStatus(response.message);
      onIngestComplete?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ingestion failed");
    } finally {
      setIsIngesting(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <Button
          onClick={() => handleIngest("all")}
          disabled={isIngesting}
          variant="default"
        >
          {isIngesting ? "Ingesting..." : "Ingest All"}
        </Button>
        <Button
          onClick={() => handleIngest("web")}
          disabled={isIngesting}
          variant="outline"
        >
          Ingest Website
        </Button>
        <Button
          onClick={() => handleIngest("file")}
          disabled={isIngesting}
          variant="outline"
        >
          Ingest Files
        </Button>
      </div>
      {status && (
        <div className="p-4 bg-muted rounded-md">
          <p className="text-sm">{status}</p>
        </div>
      )}
      {error && (
        <div className="p-4 bg-destructive/10 rounded-md">
          <p className="text-sm text-destructive" role="alert">
            {error}
          </p>
        </div>
      )}
    </div>
  );
}
