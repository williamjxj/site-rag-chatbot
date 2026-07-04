/** Shared TypeScript types for the application */

export interface ChatRequest {
  question: string;
}

export interface ChatResponse {
  answer: string;
  sources: string[];
}

export interface IngestRequest {
  source?: "web" | "file" | "all";
  force?: boolean;
}

export interface IngestResponse {
  ok: boolean;
  message: string;
  job_id?: string;
}

export interface Document {
  uri: string;
  source: "web" | "file";
  title?: string;
  chunk_count: number;
  first_ingested_at?: string;
  last_updated_at?: string;
}

export interface DocumentListResponse {
  documents: Document[];
  total: number;
  limit: number;
  offset: number;
}

export interface DeleteResponse {
  ok: boolean;
  message: string;
  chunks_deleted: number;
}

export interface UploadResponse {
  ok: boolean;
  message: string;
  filename: string;
  chunks_ingested: number;
}

export interface BatchUploadItemResponse {
  ok: boolean;
  filename: string;
  relative_path: string;
  uri: string;
  chunks_ingested: number;
  message: string;
}

export interface BatchUploadResponse {
  ok: boolean;
  message: string;
  total_files: number;
  succeeded_files: number;
  failed_files: number;
  chunks_ingested: number;
  results: BatchUploadItemResponse[];
}

export interface ErrorResponse {
  error: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface Message {
  id: string;
  type: "question" | "answer";
  content: string;
  sources?: string[];
  timestamp: Date;
}
