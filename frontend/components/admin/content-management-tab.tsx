"use client";

import { useRef } from "react";
import { UploadForm } from "@/components/admin/upload-form";
import { DocumentList } from "@/components/admin/document-list";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

/**
 * ContentManagementTab component for managing document uploads and listings.
 * Contains upload form and document list functionality.
 */
export function ContentManagementTab() {
  const documentListRef = useRef<{ refresh: () => void }>(null);

  const handleUpload = () => {
    // Refresh document list after upload
    documentListRef.current?.refresh();
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Upload Documents</CardTitle>
          <CardDescription>
            Upload documents to add them to the knowledge base
          </CardDescription>
        </CardHeader>
        <CardContent>
          <UploadForm onUpload={handleUpload} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Manage Documents</CardTitle>
          <CardDescription>
            View and manage all documents in the knowledge base
          </CardDescription>
        </CardHeader>
        <CardContent>
          <DocumentList ref={documentListRef} />
        </CardContent>
      </Card>
    </div>
  );
}

