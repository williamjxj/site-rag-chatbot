/** Admin API client */

import { apiRequest } from "./base";
import type { DocumentListResponse, DeleteResponse, UploadResponse } from "../utils/types";

export async function listDocuments(
  source?: "web" | "file",
  limit = 100,
  offset = 0
): Promise<DocumentListResponse> {
  const params = new URLSearchParams();
  if (source) params.append("source", source);
  params.append("limit", limit.toString());
  params.append("offset", offset.toString());

  return apiRequest<DocumentListResponse>(`/admin/documents?${params}`);
}

export async function deleteDocument(documentId: string): Promise<DeleteResponse> {
  // URL encode the document ID in case it contains special characters
  const encodedId = encodeURIComponent(documentId);
  return apiRequest<DeleteResponse>(`/admin/documents/${encodedId}`, {
    method: "DELETE",
  });
}

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const response = await fetch(`${API_URL}/admin/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.message || `HTTP ${response.status}: ${response.statusText}`
    );
  }

  return response.json();
}
