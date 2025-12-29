"use client";

import { useState, FormEvent, useRef } from "react";
import { Button } from "@/components/ui/button";
import { uploadDocument } from "@/lib/api/admin";

interface UploadFormProps {
  onUpload?: () => void;
}

export function UploadForm({ onUpload }: UploadFormProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsUploading(true);
    setError(null);
    setSuccess(null);

    const fileInput = fileInputRef.current;
    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
      setError("Please select a file to upload");
      setIsUploading(false);
      return;
    }

    const file = fileInput.files[0];

    try {
      const response = await uploadDocument(file);
      setSuccess(
        `File "${response.filename}" uploaded successfully! ${response.chunks_ingested} chunks ingested.`
      );
      // Reset file input
      if (fileInput) {
        fileInput.value = "";
      }
      // Call callback to refresh document list
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
          ref={fileInputRef}
          type="file"
          id="file"
          name="file"
          accept=".pdf,.md,.mdx,.txt,.doc,.docx,.xlsx,.xls,.ppt,.pptx,.html,.htm,.csv"
          disabled={isUploading}
          className="block w-full text-sm text-muted-foreground file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-primary-foreground hover:file:bg-primary/90"
          aria-label="Upload document"
          required
        />
        <p className="mt-1 text-xs text-muted-foreground">
          Supported formats: PDF, Markdown (.md, .mdx), Text (.txt), Word (.doc, .docx), Excel (.xlsx, .xls), PowerPoint (.ppt, .pptx), HTML (.html, .htm), CSV (.csv)
        </p>
      </div>
      <Button type="submit" disabled={isUploading}>
        {isUploading ? "Uploading and processing..." : "Upload"}
      </Button>
      {error && (
        <p className="text-sm text-destructive" role="alert">
          {error}
        </p>
      )}
      {success && (
        <p className="text-sm text-green-600 dark:text-green-400" role="alert">
          {success}
        </p>
      )}
    </form>
  );
}
