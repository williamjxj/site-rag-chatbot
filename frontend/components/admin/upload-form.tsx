"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { uploadDocuments } from "@/lib/api/admin";

interface UploadFormProps {
  onUpload?: () => void;
}

export function UploadForm({ onUpload }: UploadFormProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [details, setDetails] = useState<string[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const fileInput = fileInputRef.current;
    if (!fileInput) return;

    fileInput.setAttribute("webkitdirectory", "");
    fileInput.setAttribute("directory", "");
  }, []);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsUploading(true);
    setError(null);
    setSuccess(null);
    setDetails([]);

    const fileInput = fileInputRef.current;
    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
      setError("Please select a file or folder to upload");
      setIsUploading(false);
      return;
    }

    const files = Array.from(fileInput.files);

    try {
      const response = await uploadDocuments(files);

      setSuccess(
        response.failed_files === 0
          ? `Batch upload complete. ${response.succeeded_files} files uploaded, ${response.chunks_ingested} chunks ingested.`
          : `Batch upload finished with ${response.failed_files} failure(s). ${response.succeeded_files} files uploaded, ${response.chunks_ingested} chunks ingested.`
      );
      setDetails(
        response.results.map((item) =>
          item.ok
            ? `OK: ${item.relative_path} (${item.chunks_ingested} chunks)`
            : `FAIL: ${item.relative_path} - ${item.message}`
        )
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
          Upload Document or Folder
        </label>
        <input
          ref={fileInputRef}
          type="file"
          id="file"
          name="file"
          multiple
          accept=".pdf,.md,.mdx,.txt,.doc,.docx,.xlsx,.xls,.ppt,.pptx,.html,.htm,.csv"
          disabled={isUploading}
          className="block w-full text-sm text-muted-foreground file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-primary-foreground hover:file:bg-primary/90"
          aria-label="Upload document or folder"
          required
        />
        <p className="mt-1 text-xs text-muted-foreground">
          Select multiple files or a folder. Supported formats: PDF, Markdown (.md, .mdx), Text (.txt), Word (.doc, .docx), Excel (.xlsx, .xls), PowerPoint (.ppt, .pptx), HTML (.html, .htm), CSV (.csv)
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
      {details.length > 0 && (
        <div className="rounded-md border border-border/60 bg-muted/40 p-3 text-xs text-muted-foreground">
          <p className="mb-2 font-medium text-foreground">Upload details</p>
          <ul className="space-y-1">
            {details.map((detail) => (
              <li key={detail}>{detail}</li>
            ))}
          </ul>
        </div>
      )}
    </form>
  );
}
