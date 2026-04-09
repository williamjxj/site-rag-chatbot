"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Loader2, RotateCcw, Sparkles } from "lucide-react";

import { MessageList } from "./message-list";
import { MessageInput } from "./message-input";
import { sendChatMessage } from "@/lib/api/chat";
import { Button } from "@/components/ui/button";
import type { Message } from "@/lib/utils/types";

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSend = async (question: string) => {
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

  const handleReset = () => {
    setMessages([]);
    setError(null);
  };

  return (
    <div className="chat-shell flex h-full min-h-[520px] flex-col gap-4 rounded-[28px] border border-amber-50/15 bg-gradient-to-br from-[#120903]/80 to-[#050302]/90 p-4 text-amber-50 shadow-[0_12px_40px_rgba(3,0,0,0.65)]">
      <div className="flex items-center justify-between rounded-2xl border border-amber-50/10 bg-white/5 px-4 py-3 backdrop-blur">
        <div className="flex items-center gap-3 text-[11px] font-semibold uppercase tracking-[0.3em] text-amber-200/80">
          <Sparkles className="h-4 w-4" />
          Context aware answers
        </div>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className="gap-2 rounded-xl bg-white/5 text-amber-100 hover:bg-white/10"
          onClick={handleReset}
        >
          <RotateCcw className="h-4 w-4" />
          Reset
        </Button>
      </div>

      <div className="relative flex-1 overflow-hidden rounded-[22px] border border-amber-50/5 bg-black/30">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 opacity-70"
          style={{
            backgroundImage:
              "radial-gradient(circle at 20% 20%, rgba(251,191,36,0.15), transparent 45%), radial-gradient(circle at 80% 0%, rgba(234,179,8,0.2), transparent 55%)",
          }}
        />
        <div className="relative flex h-full flex-col">
          <div className="flex-1 overflow-y-auto">
            <MessageList messages={messages} />
            <AnimatePresence>
              {isLoading && (
                <motion.div
                  key="thinking"
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  className="flex justify-start p-4"
                >
                  <div className="flex items-center gap-3 rounded-2xl border border-amber-100/10 bg-black/50 px-4 py-3 text-sm text-amber-100">
                    <Loader2 className="h-4 w-4 animate-spin text-amber-200" />
                    Synthesizing a reply…
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
          <div className="border-t border-amber-100/5 p-4">
            <MessageInput onSend={handleSend} disabled={isLoading} isLoading={isLoading} />
            <AnimatePresence>
              {error && (
                <motion.p
                  role="alert"
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -4 }}
                  className="mt-3 rounded-xl border border-red-500/20 bg-red-500/10 px-3 py-2 text-sm text-red-200"
                >
                  {error}
                </motion.p>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}
