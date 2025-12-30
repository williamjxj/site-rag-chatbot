"use client";

import { IngestionStatus } from "@/components/admin/ingestion-status";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

/**
 * SystemStatusTab component for system status and ingestion controls.
 * Contains ingestion status and trigger controls.
 */
export function SystemStatusTab() {
  const handleIngestComplete = () => {
    // Could refresh document list or show notification
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Ingest Content</CardTitle>
          <CardDescription>
            Trigger content ingestion from website or uploaded files
          </CardDescription>
        </CardHeader>
        <CardContent>
          <IngestionStatus onIngestComplete={handleIngestComplete} />
        </CardContent>
      </Card>
    </div>
  );
}

