"use client";

interface SourceCitationsProps {
  sources: string[];
}

export function SourceCitations({ sources }: SourceCitationsProps) {
  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <div className="mt-2 pt-2 border-t border-border/50">
      <p className="text-xs font-semibold mb-1">Sources:</p>
      <ul className="text-xs space-y-1">
        {sources.map((source, idx) => (
          <li key={idx} className="break-all text-muted-foreground">
            {source}
          </li>
        ))}
      </ul>
    </div>
  );
}
