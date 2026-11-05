"use client";

import React, { useState } from "react";
import { Copy, Check } from "lucide-react";
import { cn } from "@/lib/utils";

interface CodeViewerProps {
  code: string;
  language?: string;
  title?: string;
  className?: string;
}

export function CodeViewer({ code, language = "yaml", title, className }: CodeViewerProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={cn("rounded-lg border border-border bg-[#090b10] overflow-hidden text-xs", className)}>
      <div className="flex items-center justify-between px-4 py-2 border-b border-border bg-surface-100/80">
        <span className="font-mono text-[11px] text-gray-400">
          {title || language.toUpperCase()}
        </span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-2 py-1 rounded bg-surface-50 hover:bg-surface-200 border border-border text-gray-300 hover:text-white transition cursor-pointer text-[11px]"
        >
          {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
          <span>{copied ? "Copied" : "Copy"}</span>
        </button>
      </div>
      <div className="p-4 overflow-x-auto font-mono text-gray-300 whitespace-pre leading-relaxed select-text">
        {code}
      </div>
    </div>
  );
}
