"use client";

import { Link2 } from "lucide-react";

interface SourceCitationsProps {
  sources: string[];
}

export function SourceCitations({ sources }: SourceCitationsProps) {
  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <div className="mt-4 rounded-2xl border border-amber-100/15 bg-black/30 px-3 py-3 text-xs text-amber-100/80">
      <div className="mb-2 flex items-center gap-2 text-[11px] uppercase tracking-[0.3em] text-amber-200">
        <Link2 className="h-3.5 w-3.5" />
        Sources
      </div>
      <ul className="space-y-1">
        {sources.map((source, idx) => (
          <li key={idx} className="break-all text-amber-50/80">
            {source}
          </li>
        ))}
      </ul>
    </div>
  );
}
