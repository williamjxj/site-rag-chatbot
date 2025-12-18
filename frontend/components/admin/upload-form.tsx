"use client";

import { useState, FormEvent } from "react";
import { Button } from "@/components/ui/button";

interface UploadFormProps {
  onUpload?: () => void;
}

export function UploadForm({ onUpload }: UploadFormProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsUploading(true);
    setError(null);

    try {
      // Note: File upload would require multipart/form-data handling
      // For now, this is a placeholder for the upload UI
      // Actual file upload would be implemented with a file input
      await new Promise((resolve) => setTimeout(resolve, 1000));
      onUpload?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="file" className="block text-sm font-medium mb-2">
          Upload Document
        </label>
        <input
          type="file"
          id="file"
          accept=".pdf,.md,.mdx,.txt"
          disabled={isUploading}
          className="block w-full text-sm text-muted-foreground file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-primary-foreground hover:file:bg-primary/90"
          aria-label="Upload document"
        />
      </div>
      <Button type="submit" disabled={isUploading}>
        {isUploading ? "Uploading..." : "Upload"}
      </Button>
      {error && (
        <p className="text-sm text-destructive" role="alert">
          {error}
        </p>
      )}
    </form>
  );
}
