"use client";

import { useRef } from "react";
import { IngestionStatus } from "@/components/admin/ingestion-status";
import { UploadForm } from "@/components/admin/upload-form";
import { DocumentList } from "@/components/admin/document-list";

export default function AdminPage() {
  const documentListRef = useRef<{ refresh: () => void }>(null);

  const handleUpload = () => {
    // Refresh document list after upload
    documentListRef.current?.refresh();
  };

  return (
    <main className="container mx-auto p-8">
      <div className="space-y-8">
        <header>
          <h1 className="text-3xl font-bold">Admin - Content Management</h1>
          <p className="text-muted-foreground mt-2">
            Manage knowledge base content and trigger ingestion
          </p>
        </header>

        <section>
          <h2 className="text-2xl font-semibold mb-4">Ingest Content</h2>
          <IngestionStatus onIngestComplete={handleUpload} />
        </section>

        <section>
          <h2 className="text-2xl font-semibold mb-4">Upload Documents</h2>
          <UploadForm onUpload={handleUpload} />
        </section>

        <section>
          <h2 className="text-2xl font-semibold mb-4">Manage Documents</h2>
          <DocumentList ref={documentListRef} />
        </section>
      </div>
    </main>
  );
}
