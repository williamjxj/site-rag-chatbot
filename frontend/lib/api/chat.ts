/** Chat API client */

import { apiRequest } from "./base";
import type { ChatRequest, ChatResponse } from "../utils/types";

export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  return apiRequest<ChatResponse>("/chat", {
    method: "POST",
    body: JSON.stringify(request),
  });
}
