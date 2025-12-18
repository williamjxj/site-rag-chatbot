"use client";

import { useState, useEffect } from "react";
import { listDocuments, deleteDocument } from "@/lib/api/admin";
import type { Document } from "@/lib/utils/types";
import { Button } from "@/components/ui/button";

export function DocumentList() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<"web" | "file" | "all">("all");
  const [deleting, setDeleting] = useState<string | null>(null);

  const loadDocuments = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await listDocuments(
        filter === "all" ? undefined : filter
      );
      setDocuments(response.documents);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load documents");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, [filter]);

  const handleDelete = async (uri: string) => {
    if (!confirm(`Are you sure you want to delete this document?\n\n${uri}`)) {
      return;
    }

    setDeleting(uri);
    try {
      await deleteDocument(uri);
      await loadDocuments(); // Reload list
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to delete document");
    } finally {
      setDeleting(null);
    }
  };

  if (loading) {
    return <p className="text-muted-foreground">Loading documents...</p>;
  }

  if (error) {
    return (
      <div className="p-4 bg-destructive/10 rounded-md">
        <p className="text-destructive" role="alert">
          {error}
        </p>
        <Button onClick={loadDocuments} className="mt-2" variant="outline">
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <Button
          onClick={() => setFilter("all")}
          variant={filter === "all" ? "default" : "outline"}
        >
          All
        </Button>
        <Button
          onClick={() => setFilter("web")}
          variant={filter === "web" ? "default" : "outline"}
        >
          Website
        </Button>
        <Button
          onClick={() => setFilter("file")}
          variant={filter === "file" ? "default" : "outline"}
        >
          Files
        </Button>
      </div>

      {documents.length === 0 ? (
        <p className="text-muted-foreground">No documents found</p>
      ) : (
        <div className="space-y-2">
          {documents.map((doc) => (
            <div
              key={doc.uri}
              className="border rounded-lg p-4 flex justify-between items-start"
            >
              <div className="flex-1">
                <h3 className="font-semibold">{doc.title || doc.uri}</h3>
                <p className="text-sm text-muted-foreground break-all">
                  {doc.uri}
                </p>
                <div className="mt-2 flex gap-4 text-xs text-muted-foreground">
                  <span>Source: {doc.source}</span>
                  <span>Chunks: {doc.chunk_count}</span>
                  {doc.first_ingested_at && (
                    <span>
                      Ingested: {new Date(doc.first_ingested_at).toLocaleDateString()}
                    </span>
                  )}
                </div>
              </div>
              <Button
                onClick={() => handleDelete(doc.uri)}
                disabled={deleting === doc.uri}
                variant="destructive"
                size="sm"
              >
                {deleting === doc.uri ? "Deleting..." : "Delete"}
              </Button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
