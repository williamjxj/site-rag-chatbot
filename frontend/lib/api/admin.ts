/** Admin API client */

import { apiRequest } from "./base";
import type { DocumentListResponse, DeleteResponse } from "../utils/types";

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
