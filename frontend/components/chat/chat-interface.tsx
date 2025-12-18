"use client";

import { useState } from "react";
import { MessageList } from "./message-list";
import { MessageInput } from "./message-input";
import { sendChatMessage } from "@/lib/api/chat";
import type { Message } from "@/lib/utils/types";

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSend = async (question: string) => {
    // Add user question to messages
    const questionMessage: Message = {
      id: `q-${Date.now()}`,
      type: "question",
      content: question,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, questionMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await sendChatMessage({ question });
      const answerMessage: Message = {
        id: `a-${Date.now()}`,
        type: "answer",
        content: response.answer,
        sources: response.sources,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, answerMessage]);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to get response";
      setError(errorMessage);
      const errorMsg: Message = {
        id: `e-${Date.now()}`,
        type: "answer",
        content: `Error: ${errorMessage}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen">
      <div className="flex-1 overflow-y-auto">
        <MessageList messages={messages} />
        {isLoading && (
          <div className="flex justify-start p-4">
            <div className="bg-muted rounded-lg p-4">
              <p className="text-muted-foreground">Thinking...</p>
            </div>
          </div>
        )}
      </div>
      <div className="border-t p-4">
        <MessageInput onSend={handleSend} disabled={isLoading} />
        {error && (
          <p className="mt-2 text-sm text-destructive" role="alert">
            {error}
          </p>
        )}
      </div>
    </div>
  );
}
