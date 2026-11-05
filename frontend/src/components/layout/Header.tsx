"use client";

import React, { useState } from "react";
import { Play, Sparkles, CheckCircle2, AlertCircle, RefreshCw } from "lucide-react";
import { api } from "@/lib/api";

export function Header({ title, description }: { title?: string; description?: string }) {
  const [isRunning, setIsRunning] = useState(false);
  const [runMessage, setRunMessage] = useState<string | null>(null);

  const handleQuickRun = async () => {
    setIsRunning(true);
    setRunMessage(null);
    try {
      const res = await api.runWorkflow({
        target_challenger: "SigNoz Cloud",
        include_synthetic: true,
        timeout_seconds: 45,
      });
      setRunMessage(`Pipeline initiated: Workflow ${res.workflow_id.slice(0, 8)}`);
      setTimeout(() => setRunMessage(null), 5000);
    } catch (err: any) {
      setRunMessage(`Run error: ${err.message || "Failed"}`);
      setTimeout(() => setRunMessage(null), 6000);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <header className="h-16 border-b border-border bg-surface-200/80 backdrop-blur px-6 flex items-center justify-between sticky top-0 z-20">
      <div>
        {title && <h1 className="text-base font-semibold text-white tracking-tight">{title}</h1>}
        {description && <p className="text-xs text-gray-400">{description}</p>}
      </div>

      <div className="flex items-center gap-3">
        {runMessage && (
          <span className="text-xs font-mono px-2.5 py-1 rounded bg-brand-500/20 text-brand-300 border border-brand-500/30 animate-fade-in">
            {runMessage}
          </span>
        )}

        {/* Live Status Pill */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-surface-100 border border-border text-xs">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="text-[11px] font-mono text-gray-300">SYSTEM READY</span>
        </div>

        {/* Trigger Pipeline Action */}
        <button
          onClick={handleQuickRun}
          disabled={isRunning}
          className="flex items-center gap-2 px-3.5 py-1.5 rounded-md bg-brand-600 hover:bg-brand-500 disabled:opacity-50 text-white text-xs font-medium transition shadow-sm shadow-brand-600/30 cursor-pointer"
        >
          {isRunning ? (
            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <Play className="w-3.5 h-3.5 fill-current" />
          )}
          <span>{isRunning ? "Orchestrating..." : "Run Pipeline"}</span>
        </button>
      </div>
    </header>
  );
}
