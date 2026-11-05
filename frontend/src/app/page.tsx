"use client";

import React from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import {
  Radio,
  Building2,
  TrendingUp,
  DollarSign,
  FileCheck2,
  Activity,
  ArrowUpRight,
  ShieldAlert,
  Clock,
  Sparkles,
} from "lucide-react";
import { api } from "@/lib/api";
import { Header } from "@/components/layout/Header";
import { MetricCard } from "@/components/ui/MetricCard";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { StatusBadge, Badge } from "@/components/ui/Badge";
import { formatCurrency, formatDate, cleanSignalText } from "@/lib/utils";

export default function OverviewPage() {
  const { data: stats, isLoading: loadingStats } = useQuery({
    queryKey: ["statsSummary"],
    queryFn: () => api.getStatsSummary(),
  });

  const { data: signals, isLoading: loadingSignals } = useQuery({
    queryKey: ["recentSignals"],
    queryFn: () => api.getSignals({ limit: 5 }),
  });

  const { data: companies, isLoading: loadingCompanies } = useQuery({
    queryKey: ["topCompanies"],
    queryFn: () => api.getCompanies({ limit: 5, qualification_status: "ACCEPTED" }),
  });

  const { data: workflows, isLoading: loadingWorkflows } = useQuery({
    queryKey: ["recentWorkflows"],
    queryFn: () => api.listWorkflows({ limit: 5 }),
  });

  const { data: finopsMetrics } = useQuery({
    queryKey: ["finopsMetrics"],
    queryFn: () => api.getFinOpsMetrics(),
  });

  return (
    <div className="flex-1 flex flex-col min-w-0">
      <Header
        title="Intelligence Overview"
        description="Real-time competitive deposition and customer acquisition operations against Datadog."
      />

      <div className="p-6 space-y-6 max-w-7xl mx-auto w-full">
        {/* KPI Metric Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <MetricCard
            title="Total Signals"
            value={stats?.signals_count ?? "..."}
            subtitle="Public vendor complaints"
            icon={Radio}
            trend="+12% this week"
            trendPositive
          />
          <MetricCard
            title="Companies Identified"
            value={stats?.companies_count ?? "..."}
            subtitle="Verified employer profiles"
            icon={Building2}
          />
          <MetricCard
            title="Qualified Prospects"
            value={stats?.qualified_prospects_count ?? "..."}
            subtitle="ICP fit score >= 0.75"
            icon={TrendingUp}
            trend="High conviction"
            trendPositive
          />
          <MetricCard
            title="Dossiers Generated"
            value={stats?.dossiers_count ?? "..."}
            subtitle="Takeout blueprints ready"
            icon={FileCheck2}
          />
          <MetricCard
            title="Potential Savings"
            value={formatCurrency(finopsMetrics?.total_potential_annual_savings_usd ?? stats?.potential_annual_savings_usd ?? 0)}
            subtitle="Annual modeled delta"
            icon={DollarSign}
            className="border-emerald-500/20 bg-gradient-to-br from-surface-100 to-emerald-950/15"
          />
        </div>

        {/* 2-Column Main Section: High Conviction Opportunities & Recent Signals */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top Opportunities */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <div>
                <CardTitle>Top Migration Opportunities</CardTitle>
                <p className="text-xs text-gray-400">Accepted companies with verified Datadog usage and high ICP fit.</p>
              </div>
              <Link
                href="/companies"
                className="text-xs text-brand-400 hover:text-brand-300 flex items-center gap-1 font-medium"
              >
                View all <ArrowUpRight className="w-3.5 h-3.5" />
              </Link>
            </CardHeader>
            <CardContent>
              {loadingCompanies ? (
                <div className="py-8 text-center text-xs text-gray-500">Loading company profiles...</div>
              ) : companies && companies.length > 0 ? (
                <div className="divide-y divide-border/60">
                  {companies.map((c) => (
                    <div key={c.id} className="py-3 flex items-center justify-between gap-4">
                      <div>
                        <div className="flex items-center gap-2">
                          <Link
                            href={`/companies/${c.id}`}
                            className="font-medium text-xs text-white hover:text-brand-400 transition"
                          >
                            {c.name}
                          </Link>
                          {c.is_synthetic && <Badge variant="synthetic">SYNTHETIC</Badge>}
                        </div>
                        <p className="text-[11px] text-gray-400 mt-0.5">
                          {c.industry || "Technology"} &bull; {c.estimated_size}
                        </p>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="text-right">
                          <span className="text-xs font-mono font-semibold text-emerald-400">
                            ICP: {(c.icp_score * 100).toFixed(0)}%
                          </span>
                          <span className="block text-[10px] text-gray-500">ID Conf: {(c.identity_confidence * 100).toFixed(0)}%</span>
                        </div>
                        <StatusBadge status={c.qualification_status} />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="py-8 text-center text-xs text-gray-500">
                  No accepted companies found yet. Run an ingestion cycle to discover signals.
                </div>
              )}
            </CardContent>
          </Card>

          {/* Incoming Distress Signals */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <div>
                <CardTitle>Recent Public Distress Signals</CardTitle>
                <p className="text-xs text-gray-400">Live vents, billing shocks, and outage discussions.</p>
              </div>
              <Link
                href="/signals"
                className="text-xs text-brand-400 hover:text-brand-300 flex items-center gap-1 font-medium"
              >
                View monitor <ArrowUpRight className="w-3.5 h-3.5" />
              </Link>
            </CardHeader>
            <CardContent>
              {loadingSignals ? (
                <div className="py-8 text-center text-xs text-gray-500">Loading incoming signals...</div>
              ) : signals && signals.length > 0 ? (
                <div className="divide-y divide-border/60">
                  {signals.map((s) => (
                    <div key={s.id} className="py-3 space-y-1.5">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Badge variant="purple">{s.source}</Badge>
                          <Badge variant="danger">{s.complaint_category}</Badge>
                          {s.is_synthetic && <Badge variant="synthetic">SYNTHETIC</Badge>}
                        </div>
                        <span className="text-[11px] font-mono text-gray-500">{formatDate(s.created_at)}</span>
                      </div>
                      <p className="text-xs text-gray-300 line-clamp-2 leading-relaxed">
                        &ldquo;{cleanSignalText(s.raw_content)}&rdquo;
                      </p>
                      <div className="flex items-center justify-between text-[11px] text-gray-500">
                        <span>Urgency: {(s.urgency_score * 10).toFixed(1)}/10</span>
                        <a
                          href={s.original_url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-brand-400 hover:underline flex items-center gap-1"
                        >
                          Source <ArrowUpRight className="w-3 h-3" />
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="py-8 text-center text-xs text-gray-500">
                  No signals detected. Click &quot;Run Pipeline&quot; to fetch public feeds.
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Recent Orchestrator Workflows & Agent Architecture Health */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Workflows table */}
          <Card className="lg:col-span-2">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <div>
                <CardTitle>Recent Orchestrator Workflows</CardTitle>
                <p className="text-xs text-gray-400">Autonomous execution tracking through the 7-phase state machine.</p>
              </div>
              <Link
                href="/history"
                className="text-xs text-brand-400 hover:text-brand-300 flex items-center gap-1 font-medium"
              >
                Full history <ArrowUpRight className="w-3.5 h-3.5" />
              </Link>
            </CardHeader>
            <CardContent>
              {loadingWorkflows ? (
                <div className="py-8 text-center text-xs text-gray-500">Loading workflows...</div>
              ) : workflows && workflows.workflows.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-left">
                    <thead>
                      <tr className="border-b border-border/80 text-[10px] font-mono text-gray-400 uppercase">
                        <th className="py-2">Workflow ID</th>
                        <th className="py-2">Current Step</th>
                        <th className="py-2">Status</th>
                        <th className="py-2">Duration</th>
                        <th className="py-2">Timestamp</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border/50">
                      {workflows.workflows.map((wf) => (
                        <tr key={wf.workflow_id} className="hover:bg-surface-50/50 transition">
                          <td className="py-2.5 font-mono text-white">{wf.workflow_id.slice(0, 8)}...</td>
                          <td className="py-2.5 font-mono text-gray-300">{wf.current_step}</td>
                          <td className="py-2.5">
                            <StatusBadge status={wf.status} />
                          </td>
                          <td className="py-2.5 font-mono text-gray-400">
                            {wf.execution_duration_ms > 0 ? `${(wf.execution_duration_ms / 1000).toFixed(1)}s` : "-"}
                          </td>
                          <td className="py-2.5 text-gray-500">{formatDate(wf.created_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="py-8 text-center text-xs text-gray-500">
                  No workflows recorded yet. Click &quot;Run Pipeline&quot; to execute your first deposition cycle.
                </div>
              )}
            </CardContent>
          </Card>

          {/* Multi-Agent System Status */}
          <Card>
            <CardHeader>
              <CardTitle>Autonomous Agent Ensemble</CardTitle>
              <p className="text-xs text-gray-400">Operational readiness and state telemetry.</p>
            </CardHeader>
            <CardContent className="space-y-3">
              {[
                { name: "Listener Agent", desc: "Reddit, HN & Datadog Status Streams", key: "listener", step: "LISTENER" },
                { name: "Profiler Agent", desc: "Entity Resolution & Tech Profiler", key: "profiler", step: "PROFILER" },
                { name: "FinOps Engine", desc: "5-Platform Pricing Delta Matrix", key: "finops_architect", step: "FINOPS" },
                { name: "Architect Agent", desc: "OpenTelemetry Port :8126 Dual-Ship", key: "finops_architect", step: "ARCHITECT" },
                { name: "Copywriter Agent", desc: "Executive Collateral & Evidence Guard", key: "copywriter", step: "COPYWRITER" },
                { name: "Human Approval Gate", desc: "Strictly Enforces Human Review", key: "governance", step: "APPROVAL_GATE", isProtected: true },
              ].map((agent) => {
                let telemetry = { status: "Unknown", color: "text-gray-500" };
                if (agent.isProtected) {
                  telemetry = { status: "Protected", color: "text-amber-400" };
                } else if (loadingStats) {
                  telemetry = { status: "Unknown", color: "text-gray-500" };
                } else {
                  const runningWf = workflows?.workflows?.find(
                    (w) => w.status?.includes("RUNNING") || w.status === "PENDING"
                  );
                  if (runningWf && runningWf.current_step === agent.step) {
                    telemetry = { status: "Running", color: "text-amber-400 animate-pulse" };
                  } else {
                    const latestWf = workflows?.workflows?.[0];
                    if (latestWf?.status === "FAILED" && latestWf.current_step === agent.step) {
                      telemetry = { status: "Failed", color: "text-rose-400" };
                    } else if (stats?.agent_status?.[agent.key] === "idle") {
                      telemetry = { status: "Idle", color: "text-blue-400" };
                    } else if (stats?.agent_status?.[agent.key]) {
                      telemetry = { status: "Available", color: "text-emerald-400" };
                    } else {
                      telemetry = { status: "Available", color: "text-emerald-400" };
                    }
                  }
                }
                return (
                  <div key={agent.name} className="flex items-center justify-between p-2.5 rounded bg-surface-50/70 border border-border/60">
                    <div>
                      <div className="text-xs font-medium text-white">{agent.name}</div>
                      <div className="text-[10px] text-gray-400">{agent.desc}</div>
                    </div>
                    <span className={`text-[10px] font-mono font-semibold ${telemetry.color}`}>
                      {telemetry.status}
                    </span>
                  </div>
                );
              })}
              <div className="pt-2">
                <Link
                  href="/agents"
                  className="w-full block text-center py-2 rounded bg-surface-50 hover:bg-surface-200 border border-border text-xs text-brand-400 font-medium transition"
                >
                  Open Agent Topology Visualizer &rarr;
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
