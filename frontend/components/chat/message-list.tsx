"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Bot, UserRound } from "lucide-react";
import React from "react";

import type { Message } from "@/lib/utils/types";

import { MarkdownRenderer } from "./markdown-renderer";
import { SourceCitations } from "./source-citations";

interface MessageListProps {
  messages: Message[];
}

const messageVariants = {
  hidden: { opacity: 0, y: 18, scale: 0.98 },
  visible: { opacity: 1, y: 0, scale: 1 },
  exit: { opacity: 0, y: -10, scale: 0.98 },
};

export const MessageList = React.memo(function MessageList({
  messages,
}: MessageListProps) {
  if (messages.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 text-center text-amber-50/70">
        <div className="rounded-3xl border border-amber-100/15 bg-black/40 px-4 py-2 text-xs uppercase tracking-[0.35em]">
          Amber minimal
        </div>
        <p className="text-lg font-medium">Start a dialog with your knowledge base</p>
        <p className="max-w-sm text-sm text-amber-100/70">
          Ask for metrics, summaries, or clarifications and watch the assistant cite authoritative sources.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4 p-4">
      <AnimatePresence initial={false}>
        {messages.map((message) => {
          const isUser = message.type === "question";
          const Icon = isUser ? UserRound : Bot;
          const timeLabel = message.timestamp.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          });

          return (
            <motion.div
              key={message.id}
              layout
              variants={messageVariants}
              initial="hidden"
              animate="visible"
              exit="exit"
              transition={{ duration: 0.2, ease: "easeOut" }}
              className={`flex ${isUser ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`flex max-w-[min(640px,90%)] gap-3 ${
                  isUser ? "flex-row-reverse text-right" : "flex-row"
                }`}
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-2xl border border-amber-50/20 bg-black/40 text-amber-100">
                  <Icon className="h-4 w-4" />
                </div>
                <div
                  className={`group relative rounded-3xl border px-5 py-4 shadow-lg ${
                    isUser
                      ? "border-transparent bg-gradient-to-br from-amber-400/90 to-orange-500/80 text-slate-950"
                      : "border-amber-50/10 bg-[#0b0603]/85 text-amber-50"
                  }`}
                >
                  <div className="text-xs uppercase tracking-[0.3em] text-amber-100/70">
                    {isUser ? "You" : "Guide"} · {timeLabel}
                  </div>
                  <div className="mt-2 leading-relaxed">
                    {isUser ? (
                      <p className="whitespace-pre-wrap text-base">{message.content}</p>
                    ) : (
                      <MarkdownRenderer content={message.content} />
                    )}
                  </div>
                  {message.sources && message.sources.length > 0 && (
                    <SourceCitations sources={message.sources} />
                  )}
                </div>
              </div>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
});
