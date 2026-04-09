"use client";

import React from "react";
import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import rehypeSanitize from "rehype-sanitize";
import "highlight.js/styles/github.css";

/**
 * MarkdownRenderer component for rendering markdown content with syntax highlighting.
 * 
 * Features:
 * - Syntax highlighting for code blocks
 * - Sanitization to prevent XSS attacks
 * - Styled with Tailwind CSS utilities
 * - Error handling for malformed markdown
 * 
 * @param content - The markdown content to render
 */
export function MarkdownRenderer({ content }: { content: string }) {
  
  try {
    return (
      <div className="markdown-content prose prose-sm max-w-none text-amber-50 prose-headings:text-amber-50 prose-strong:text-amber-50">
        <ReactMarkdown
          rehypePlugins={[rehypeHighlight, rehypeSanitize]}
          components={{
          // Style code blocks
          code: ({ className, children, ...props }) => {
            const match = /language-(\w+)/.exec(className || "");
            const isInline = !className || !match;
            return !isInline ? (
              <code
                className={`${className} block rounded-xl bg-[#1a0e05] p-4 text-sm font-mono text-amber-50/90 shadow-inner`}
                {...props}
              >
                {children}
              </code>
            ) : (
              <code
                className="rounded bg-[#1a0e05] px-1.5 py-0.5 text-sm font-mono"
                {...props}
              >
                {children}
              </code>
            );
          },
          // Style links
          a: (props) => (
            <a
              className="text-amber-200 underline underline-offset-4 hover:text-amber-100"
              target="_blank"
              rel="noopener noreferrer"
              {...props}
            />
          ),
          // Style headings
          h1: (props) => (
            <h1 className="text-2xl font-bold mt-4 mb-2" {...props} />
          ),
          h2: (props) => (
            <h2 className="text-xl font-semibold mt-3 mb-2" {...props} />
          ),
          h3: (props) => (
            <h3 className="text-lg font-semibold mt-2 mb-1" {...props} />
          ),
          // Style lists
          ul: (props) => (
            <ul className="list-disc list-inside my-2 space-y-1" {...props} />
          ),
          ol: (props) => (
            <ol className="list-decimal list-inside my-2 space-y-1" {...props} />
          ),
          // Style paragraphs
          p: (props) => (
            <p className="my-2" {...props} />
          ),
          }}
        >
          {content}
        </ReactMarkdown>
      </div>
    );
  } catch (error) {
    // Fallback to plain text if markdown rendering fails
    console.error("Markdown rendering error:", error);
    return (
      <div className="text-sm">
        <p className="whitespace-pre-wrap">{content}</p>
      </div>
    );
  }
}
