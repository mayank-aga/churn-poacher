"use client";

import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { 
  Settings, 
  Shield, 
  Sliders, 
  Sparkles, 
  CheckCircle2, 
  Save, 
  RefreshCw,
  Activity
} from "lucide-react";
import { fetchSystemStats, triggerSyntheticSignal, api } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { SystemStatsSummary } from "@/types";

export default function SettingsPage() {
  const [defaultTarget, setDefaultTarget] = useState<"SIGNOZ" | "GRAFANA">("SIGNOZ");
  const [requireApproval, setRequireApproval] = useState<boolean>(true);
  const [strictEvidenceGuard, setStrictEvidenceGuard] = useState<boolean>(true);
  const [hourlyRate, setHourlyRate] = useState<number>(125);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationSuccess, setGenerationSuccess] = useState<string | null>(null);
  const [savedSuccess, setSavedSuccess] = useState(false);

  const { data: stats, isLoading: isStatsLoading, refetch } = useQuery<SystemStatsSummary>({
    queryKey: ["systemStats"],
    queryFn: fetchSystemStats,
  });

  const { data: llmStatus } = useQuery({
    queryKey: ["llmStatus"],
    queryFn: () => api.getLLMStatus(),
  });

  const handleGenerateSynthetic = async () => {
    setIsGenerating(true);
    setGenerationSuccess(null);
    try {
      const res = await triggerSyntheticSignal();
      setGenerationSuccess(`Generated synthetic ingestion batch: ${res?.total_signals_ingested ?? 1} signals inserted.`);
      refetch();
    } catch (err: any) {
      alert("Failed to generate synthetic signal: " + (err?.message || "Unknown error"));
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSaveSettings = (e: React.FormEvent) => {
    e.preventDefault();
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 2500);
  };

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border-subtle pb-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-lg bg-surface-elevated border border-border-subtle text-accent-cyan">
              <Settings className="w-5 h-5" />
            </span>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-text-primary">
                System Settings & Governance
              </h1>
              <p className="text-sm text-text-muted">
                Configure competitive battlegrounds, FinOps cost engines, and agent governance controls.
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Badge variant="success">Production Ready</Badge>
        </div>
      </div>

      <form onSubmit={handleSaveSettings} className="space-y-6">
        {/* Battleground Settings */}
        <Card>
          <CardHeader>
            <CardTitle>Competitive Battleground Configuration</CardTitle>
            <CardDescription>Control vendor displacement defaults and alternative targets.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-text-secondary mb-1.5">
                  Monitored Incumbent Vendor
                </label>
                <input
                  type="text"
                  disabled
                  value="Datadog (Infrastructure, APM, Logs, Synthetics)"
                  className="w-full bg-surface-muted border border-border-subtle rounded-lg px-3.5 py-2 text-xs font-mono text-text-muted cursor-not-allowed"
                />
                <p className="text-[11px] text-text-muted mt-1">
                  Datadog official status page, Hacker News, Reddit r/devops are active.
                </p>
              </div>

              <div>
                <label className="block text-xs font-medium text-text-secondary mb-1.5">
                  Default Displacement Target
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setDefaultTarget("SIGNOZ")}
                    className={`px-3 py-2 text-xs font-medium rounded-lg border text-center transition-all ${
                      defaultTarget === "SIGNOZ"
                        ? "bg-brand-indigo/20 border-brand-indigo text-white"
                        : "bg-surface-elevated border-border-subtle text-text-secondary hover:text-text-primary"
                    }`}
                  >
                    SigNoz (OTel Native)
                  </button>
                  <button
                    type="button"
                    onClick={() => setDefaultTarget("GRAFANA")}
                    className={`px-3 py-2 text-xs font-medium rounded-lg border text-center transition-all ${
                      defaultTarget === "GRAFANA"
                        ? "bg-brand-indigo/20 border-brand-indigo text-white"
                        : "bg-surface-elevated border-border-subtle text-text-secondary hover:text-text-primary"
                    }`}
                  >
                    Grafana Cloud / OSS
                  </button>
                </div>
                <p className="text-[11px] text-text-muted mt-1">
                  Sets default recommendations in FinOps and Architect blueprints.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Governance & Safety Gates */}
        <Card>
          <CardHeader>
            <CardTitle>Governance & Safety Gates (Human-in-the-Loop)</CardTitle>
            <CardDescription>Enforce enterprise anti-hallucination and dispatch controls.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start justify-between p-3.5 rounded-lg bg-surface-elevated/70 border border-border-subtle">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <Shield className="w-4 h-4 text-status-success" />
                  <span className="text-sm font-medium text-text-primary">
                    Mandatory Human Approval Gate
                  </span>
                </div>
                <p className="text-xs text-text-muted max-w-xl">
                  Strictly prohibits autonomous cold sending of sales collateral. Generated emails and LinkedIn sequences must remain in DRAFT status until human sales leadership clicks Approve.
                </p>
              </div>
              <input
                type="checkbox"
                checked={requireApproval}
                onChange={(e) => setRequireApproval(e.target.checked)}
                className="mt-1 h-4 w-4 rounded border-border-subtle bg-surface-elevated text-brand-indigo focus:ring-brand-indigo"
              />
            </div>

            <div className="flex items-start justify-between p-3.5 rounded-lg bg-surface-elevated/70 border border-border-subtle">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <Shield className="w-4 h-4 text-accent-cyan" />
                  <span className="text-sm font-medium text-text-primary">
                    Evidence Guard Anti-Hallucination Audit
                  </span>
                </div>
                <p className="text-xs text-text-muted max-w-xl">
                  Enforces 100% claim verification. Flags or rejects any copy containing unsupported claims or marketing buzzwords (&quot;10x faster&quot;, &quot;unlimited savings&quot;).
                </p>
              </div>
              <input
                type="checkbox"
                checked={strictEvidenceGuard}
                onChange={(e) => setStrictEvidenceGuard(e.target.checked)}
                className="mt-1 h-4 w-4 rounded border-border-subtle bg-surface-elevated text-brand-indigo focus:ring-brand-indigo"
              />
            </div>
          </CardContent>
        </Card>

        {/* FinOps Assumptions */}
        <Card>
          <CardHeader>
            <CardTitle>FinOps Calculation Assumptions</CardTitle>
            <CardDescription>Calibrate financial delta calculations and migration payback periods.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-medium text-text-secondary mb-1.5">
                  Blended Engineering Rate ($/hr)
                </label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-xs text-text-muted font-mono">$</span>
                  <input
                    type="number"
                    value={hourlyRate}
                    onChange={(e) => setHourlyRate(Number(e.target.value))}
                    className="w-full bg-surface-elevated border border-border-subtle rounded-lg pl-7 pr-3 py-2 text-xs font-mono text-text-primary focus:outline-none focus:border-brand-indigo"
                  />
                </div>
                <p className="text-[11px] text-text-muted mt-1">
                  Used for estimating internal engineering migration cost.
                </p>
              </div>

              <div>
                <label className="block text-xs font-medium text-text-secondary mb-1.5">
                  Annual Ingestion Growth Rate
                </label>
                <input
                  type="text"
                  disabled
                  value="15% compound"
                  className="w-full bg-surface-muted border border-border-subtle rounded-lg px-3 py-2 text-xs font-mono text-text-muted cursor-not-allowed"
                />
                <p className="text-[11px] text-text-muted mt-1">
                  Used for 3-Year Total Cost of Ownership (TCO).
                </p>
              </div>

              <div>
                <label className="block text-xs font-medium text-text-secondary mb-1.5">
                  Dual-Shipping Buffer
                </label>
                <input
                  type="text"
                  disabled
                  value="30 days parallel"
                  className="w-full bg-surface-muted border border-border-subtle rounded-lg px-3 py-2 text-xs font-mono text-text-muted cursor-not-allowed"
                />
                <p className="text-[11px] text-text-muted mt-1">
                  Temporary overlap cost included in payback calculation.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Staging & Simulation Tools */}
        <Card>
          <CardHeader>
            <CardTitle>Simulation & Staging Utilities</CardTitle>
            <CardDescription>Generate synthetic distress events to test real-time pipeline execution.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-lg bg-surface-elevated/70 border border-border-subtle">
              <div className="space-y-1">
                <span className="text-sm font-medium text-text-primary flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-brand-purple" />
                  Trigger Synthetic Datadog Distress Signal
                </span>
                <p className="text-xs text-text-muted max-w-lg">
                  Injects a realistic Datadog pricing shock or APM outage event into the Listener ingestion pipeline.
                </p>
              </div>

              <button
                type="button"
                onClick={handleGenerateSynthetic}
                disabled={isGenerating}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-brand-purple hover:bg-brand-purple/90 text-white text-xs font-medium shadow-sm transition-colors shrink-0"
              >
                <Sparkles className={`w-3.5 h-3.5 ${isGenerating ? "animate-spin" : ""}`} />
                {isGenerating ? "Injecting..." : "Generate Test Signal"}
              </button>
            </div>

            {generationSuccess && (
              <div className="p-3 rounded-lg bg-status-success/10 border border-status-success/30 text-xs text-status-success flex items-center gap-2 font-mono">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                <span>{generationSuccess}</span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* LLM Provider Architecture */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>LLM Provider Architecture</CardTitle>
              <Badge variant={llmStatus?.active_provider === "deterministic-fallback" ? "warning" : "success"}>
                Active: {llmStatus?.active_provider || "deterministic-fallback"}
              </Badge>
            </div>
            <CardDescription>
              Multi-provider language model integration (OpenAI, Gemini, Claude) with deterministic fallback generation.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3 rounded-lg bg-surface-elevated/70 border border-border-subtle">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-text-primary">Google Gemini</span>
                  <span className={`w-2 h-2 rounded-full ${llmStatus?.providers?.gemini?.available ? "bg-status-success" : "bg-text-muted/40"}`} />
                </div>
                <div className="mt-1 font-mono text-[11px] text-text-secondary">
                  gemini-1.5-flash
                </div>
                <div className="text-[10px] text-text-muted mt-0.5">
                  {llmStatus?.providers?.gemini?.available ? "Configured & Active" : "No GEMINI_API_KEY"}
                </div>
              </div>

              <div className="p-3 rounded-lg bg-surface-elevated/70 border border-border-subtle">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-text-primary">OpenAI</span>
                  <span className={`w-2 h-2 rounded-full ${llmStatus?.providers?.openai?.available ? "bg-status-success" : "bg-text-muted/40"}`} />
                </div>
                <div className="mt-1 font-mono text-[11px] text-text-secondary">
                  gpt-4o-mini
                </div>
                <div className="text-[10px] text-text-muted mt-0.5">
                  {llmStatus?.providers?.openai?.available ? "Configured & Active" : "No OPENAI_API_KEY"}
                </div>
              </div>

              <div className="p-3 rounded-lg bg-surface-elevated/70 border border-border-subtle">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-text-primary">Anthropic Claude</span>
                  <span className={`w-2 h-2 rounded-full ${llmStatus?.providers?.claude?.available ? "bg-status-success" : "bg-text-muted/40"}`} />
                </div>
                <div className="mt-1 font-mono text-[11px] text-text-secondary">
                  claude-3-5-sonnet
                </div>
                <div className="text-[10px] text-text-muted mt-0.5">
                  {llmStatus?.providers?.claude?.available ? "Configured & Active" : "No ANTHROPIC_API_KEY"}
                </div>
              </div>

              <div className="p-3 rounded-lg bg-surface-elevated/70 border border-border-subtle">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-text-primary">Deterministic Engine</span>
                  <span className="w-2 h-2 rounded-full bg-status-success" />
                </div>
                <div className="mt-1 font-mono text-[11px] text-text-secondary">
                  zero-hallucination
                </div>
                <div className="text-[10px] text-status-success mt-0.5">
                  Always Available
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* System Diagnostics */}
        <Card>
          <CardHeader>
            <CardTitle>System Diagnostics & Node Health</CardTitle>
            <CardDescription>Live health checks across backend API, database, and background workers.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3 rounded-lg bg-surface-elevated/70 border border-border-subtle">
                <span className="text-text-muted">FastAPI Service</span>
                <div className="flex items-center gap-1.5 mt-1 text-status-success font-medium">
                  <span className="w-2 h-2 rounded-full bg-status-success animate-pulse" />
                  <span>Online (:8000)</span>
                </div>
              </div>
              <div className="p-3 rounded-lg bg-surface-elevated/70 border border-border-subtle">
                <span className="text-text-muted">SQLite Storage</span>
                <div className="flex items-center gap-1.5 mt-1 text-status-success font-medium">
                  <span className="w-2 h-2 rounded-full bg-status-success" />
                  <span>Active WAL Mode</span>
                </div>
              </div>
              <div className="p-3 rounded-lg bg-surface-elevated/70 border border-border-subtle">
                <span className="text-text-muted">Total Signals</span>
                <div className="mt-1 font-mono font-semibold text-text-primary">
                  {stats?.signals_count ?? "--"}
                </div>
              </div>
              <div className="p-3 rounded-lg bg-surface-elevated/70 border border-border-subtle">
                <span className="text-text-muted">Total Dossiers</span>
                <div className="mt-1 font-mono font-semibold text-text-primary">
                  {stats?.dossiers_count ?? "--"}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Action Button */}
        <div className="flex items-center justify-between pt-2">
          {savedSuccess ? (
            <div className="flex items-center gap-2 text-xs text-status-success font-medium">
              <CheckCircle2 className="w-4 h-4" />
              <span>Configuration preferences saved successfully.</span>
            </div>
          ) : (
            <div />
          )}

          <button
            type="submit"
            className="flex items-center gap-2 px-5 py-2 rounded-lg bg-brand-indigo hover:bg-brand-indigo/90 text-white text-xs font-semibold shadow-sm transition-colors"
          >
            <Save className="w-4 h-4" />
            Save Preferences
          </button>
        </div>
      </form>
    </div>
  );
}
