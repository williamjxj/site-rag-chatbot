/** Ingestion API client */

import { apiRequest } from "./base";
import type { IngestRequest, IngestResponse } from "../utils/types";

export async function triggerIngestion(
  request?: IngestRequest
): Promise<IngestResponse> {
  return apiRequest<IngestResponse>("/ingest", {
    method: "POST",
    body: JSON.stringify(request || {}),
  });
}
