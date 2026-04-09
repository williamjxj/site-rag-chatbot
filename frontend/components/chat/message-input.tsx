"use client";

import { FormEvent, useState } from "react";
import { motion } from "framer-motion";
import { Loader2, SendHorizonal, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";

interface MessageInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  isLoading?: boolean;
}

export function MessageInput({ onSend, disabled = false, isLoading = false }: MessageInputProps) {
  const [input, setInput] = useState("");

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput("");
    }
  };

  const isButtonDisabled = disabled || !input.trim();

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 text-xs uppercase tracking-[0.3em] text-amber-100/70">
        <Sparkles className="h-4 w-4" />
        RAG secured channel
      </div>
      <form onSubmit={handleSubmit} className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1 rounded-2xl border border-amber-50/20 bg-black/40 shadow-inner focus-within:border-amber-200/70">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask anything about your site content…"
            disabled={disabled}
            aria-label="Question input"
            className="w-full rounded-2xl bg-transparent px-4 py-3 text-base text-amber-50 placeholder:text-amber-100/50 focus:outline-none"
          />
          <div className="pointer-events-none absolute inset-0 rounded-2xl border border-white/5 opacity-40" />
        </div>
        <Button
          type="submit"
          disabled={isButtonDisabled}
          className="inline-flex min-w-[120px] items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-amber-400 to-orange-500 text-slate-950 shadow-[0_10px_30px_rgba(251,191,36,0.35)] hover:from-amber-300 hover:to-orange-400"
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <motion.span
              initial={{ x: 0 }}
              animate={{ x: isButtonDisabled ? 0 : 2 }}
              transition={{ repeat: Infinity, repeatDelay: 1.4, duration: 0.6, ease: "easeInOut" }}
              className="flex items-center gap-2"
            >
              <SendHorizonal className="h-4 w-4" />
            </motion.span>
          )}
          <span className="font-semibold">Send</span>
        </Button>
      </form>
    </div>
  );
}
