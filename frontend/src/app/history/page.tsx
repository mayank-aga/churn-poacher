"use client";

import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { 
  History, 
  RotateCw, 
  Search, 
  Filter, 
  ChevronDown, 
  ChevronRight, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  AlertTriangle, 
  ArrowUpRight,
  Cpu,
  Layers,
  Copy,
  Check
} from "lucide-react";
import Link from "next/link";
import { fetchWorkflows, fetchWorkflowMetrics } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import { StatusBadge, Badge } from "@/components/ui/Badge";
import { MetricCard } from "@/components/ui/MetricCard";
import { WorkflowResponse, WorkflowMetricsResponse } from "@/types";
import { formatDate } from "@/lib/utils";

export default function HistoryPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [expandedWorkflowId, setExpandedWorkflowId] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const { data: workflows = [], isLoading, refetch, isFetching } = useQuery<WorkflowResponse[]>({
    queryKey: ["workflows"],
    queryFn: () => fetchWorkflows(100),
    refetchInterval: 10000,
  });

  const { data: metrics } = useQuery<WorkflowMetricsResponse>({
    queryKey: ["workflowMetrics"],
    queryFn: fetchWorkflowMetrics,
    refetchInterval: 10000,
  });

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(text);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const filteredWorkflows = workflows.filter((w) => {
    const matchesSearch = 
      w.workflow_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      w.target_challenger.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (w.current_step && w.current_step.toLowerCase().includes(searchTerm.toLowerCase()));
    
    if (statusFilter === "ALL") return matchesSearch;
    if (statusFilter === "RUNNING") {
      return matchesSearch && (w.status.includes("RUNNING") || w.status === "PENDING");
    }
    return matchesSearch && w.status === statusFilter;
  });

  const toggleExpand = (id: string) => {
    setExpandedWorkflowId(expandedWorkflowId === id ? null : id);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border-subtle pb-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-lg bg-surface-elevated border border-border-subtle text-accent-cyan">
              <History className="w-5 h-5" />
            </span>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-text-primary">
                Execution History
              </h1>
              <p className="text-sm text-text-muted">
                Complete audit trail of multi-agent pipeline executions and step transitions.
              </p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-border-subtle bg-surface-elevated hover:bg-surface-elevated/80 text-xs font-medium text-text-secondary transition-colors"
          >
            <RotateCw className={`w-3.5 h-3.5 ${isFetching ? "animate-spin text-accent-cyan" : ""}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <MetricCard
          title="Total Executions"
          value={metrics?.total_workflows ?? workflows.length}
          subtitle="Lifetime runs"
          icon={Layers}
        />
        <MetricCard
          title="Completed"
          value={metrics?.completed_count ?? workflows.filter(w => w.status === "COMPLETED").length}
          subtitle="Fully processed"
          icon={CheckCircle2}
        />
        <MetricCard
          title="Pending Gate"
          value={metrics?.pending_approval_count ?? workflows.filter(w => w.status === "DRAFT_PENDING_APPROVAL").length}
          subtitle="Awaiting human sign-off"
          icon={Clock}
        />
        <MetricCard
          title="Approved"
          value={metrics?.approved_count ?? workflows.filter(w => w.status === "APPROVED").length}
          subtitle="Ready for SDR dispatch"
          icon={CheckCircle2}
        />
        <MetricCard
          title="Avg Duration"
          value={`${((metrics?.average_duration_ms ?? 0) / 1000).toFixed(1)}s`}
          subtitle="Per pipeline run"
          icon={Cpu}
        />
      </div>

      {/* Filters and Search */}
      <div className="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center justify-between">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
          <input
            type="text"
            placeholder="Search by workflow ID, challenger, or step..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-surface-elevated border border-border-subtle rounded-lg pl-9 pr-4 py-2 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-brand-indigo"
          />
        </div>

        <div className="flex items-center gap-2 overflow-x-auto pb-1 sm:pb-0">
          <Filter className="w-3.5 h-3.5 text-text-muted shrink-0" />
          {(["ALL", "COMPLETED", "DRAFT_PENDING_APPROVAL", "APPROVED", "REJECTED", "FAILED", "RUNNING"] as const).map((filter) => (
            <button
              key={filter}
              onClick={() => setStatusFilter(filter)}
              className={`px-2.5 py-1 text-xs font-medium rounded-md whitespace-nowrap transition-colors ${
                statusFilter === filter
                  ? "bg-brand-indigo text-white shadow-sm"
                  : "bg-surface-elevated border border-border-subtle text-text-secondary hover:text-text-primary"
              }`}
            >
              {filter.replace(/_/g, " ")}
            </button>
          ))}
        </div>
      </div>

      {/* Workflows Table */}
      <Card>
        <CardHeader>
          <CardTitle>Workflows ({filteredWorkflows.length})</CardTitle>
          <CardDescription>
            Click any row to inspect granular step transitions, payload artifacts, and latency.
          </CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-8 text-center text-text-muted">Loading workflow history...</div>
          ) : filteredWorkflows.length === 0 ? (
            <div className="p-8 text-center text-text-muted">
              No workflow runs match the selected criteria.
            </div>
          ) : (
            <div className="divide-y divide-border-subtle">
              {filteredWorkflows.map((workflow) => {
                const isExpanded = expandedWorkflowId === workflow.workflow_id;
                const durationSeconds = (workflow.execution_duration_ms / 1000).toFixed(2);

                return (
                  <div key={workflow.workflow_id} className="transition-colors hover:bg-surface-elevated/40">
                    {/* Summary Row */}
                    <div
                      onClick={() => toggleExpand(workflow.workflow_id)}
                      className="p-4 flex flex-col md:flex-row md:items-center justify-between gap-4 cursor-pointer"
                    >
                      <div className="flex items-start md:items-center gap-3">
                        <button className="text-text-muted hover:text-text-primary p-0.5 mt-0.5 md:mt-0">
                          {isExpanded ? (
                            <ChevronDown className="w-4 h-4" />
                          ) : (
                            <ChevronRight className="w-4 h-4" />
                          )}
                        </button>

                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-mono text-xs font-semibold text-text-primary">
                              {workflow.workflow_id.slice(0, 8)}...
                            </span>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                copyToClipboard(workflow.workflow_id);
                              }}
                              className="text-text-muted hover:text-text-primary"
                              title="Copy full workflow ID"
                            >
                              {copiedId === workflow.workflow_id ? (
                                <Check className="w-3 h-3 text-status-success" />
                              ) : (
                                <Copy className="w-3 h-3" />
                              )}
                            </button>
                            <StatusBadge status={workflow.status} />
                            {workflow.is_synthetic && (
                              <Badge variant="synthetic">
                                Synthetic
                              </Badge>
                            )}
                          </div>
                          <div className="flex items-center gap-3 mt-1 text-xs text-text-muted">
                            <span>Target: <strong className="text-text-secondary">{workflow.target_challenger}</strong></span>
                            <span>•</span>
                            <span>Step: <strong className="text-text-secondary">{workflow.current_step}</strong></span>
                            <span>•</span>
                            <span>{formatDate(workflow.created_at)}</span>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-6 pl-7 md:pl-0">
                        <div className="text-right hidden sm:block">
                          <div className="text-xs font-mono text-text-secondary">
                            {durationSeconds}s
                          </div>
                          <div className="text-[11px] text-text-muted">
                            {workflow.step_history?.length || 0} steps • {workflow.retry_count} retries
                          </div>
                        </div>

                        {workflow.company_id && (
                          <Link
                            href={`/companies/${workflow.company_id}`}
                            onClick={(e) => e.stopPropagation()}
                            className="flex items-center gap-1 text-xs font-medium text-brand-indigo hover:text-accent-cyan transition-colors"
                          >
                            <span>Dossier</span>
                            <ArrowUpRight className="w-3.5 h-3.5" />
                          </Link>
                        )}
                      </div>
                    </div>

                    {/* Step History Expansion */}
                    {isExpanded && (
                      <div className="px-6 pb-6 pt-2 bg-surface-muted/60 border-t border-border-subtle/60">
                        <h4 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3">
                          Step Execution Sequence ({workflow.step_history?.length || 0})
                        </h4>

                        {(!workflow.step_history || workflow.step_history.length === 0) ? (
                          <p className="text-xs text-text-muted">No step history recorded for this workflow.</p>
                        ) : (
                          <div className="space-y-2">
                            {workflow.step_history.map((step, idx) => (
                              <div
                                key={idx}
                                className="flex items-start justify-between p-2.5 rounded-md bg-surface-elevated/70 border border-border-subtle text-xs"
                              >
                                <div className="flex items-start gap-2.5">
                                  <div className="mt-0.5">
                                    {step.status === "COMPLETED" || step.status === "SUCCESS" ? (
                                      <CheckCircle2 className="w-3.5 h-3.5 text-status-success" />
                                    ) : step.status === "FAILED" ? (
                                      <XCircle className="w-3.5 h-3.5 text-status-danger" />
                                    ) : step.status === "SKIPPED" ? (
                                      <AlertTriangle className="w-3.5 h-3.5 text-text-muted" />
                                    ) : (
                                      <Clock className="w-3.5 h-3.5 text-status-warning" />
                                    )}
                                  </div>
                                  <div>
                                    <div className="font-medium text-text-primary">
                                      {step.step_name}
                                    </div>
                                    {step.error_message && (
                                      <p className="text-status-danger mt-1 text-[11px] font-mono">
                                        Error: {step.error_message}
                                      </p>
                                    )}
                                    {step.details && Object.keys(step.details).length > 0 && (
                                      <div className="mt-1 text-[11px] text-text-muted font-mono truncate max-w-xl">
                                        {JSON.stringify(step.details)}
                                      </div>
                                    )}
                                  </div>
                                </div>
                                <div className="text-right shrink-0">
                                  <span className="font-mono text-text-secondary">
                                    {step.duration_ms}ms
                                  </span>
                                  <div className="text-[10px] text-text-muted">
                                    {step.completed_at ? formatDate(step.completed_at) : "In progress"}
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}

                        {workflow.error_details && (
                          <div className="mt-4 p-3 rounded-lg bg-status-danger/10 border border-status-danger/30 text-xs">
                            <span className="font-semibold text-status-danger">Workflow Error:</span>
                            <pre className="mt-1 font-mono text-[11px] text-text-secondary whitespace-pre-wrap">
                              {workflow.error_details}
                            </pre>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
