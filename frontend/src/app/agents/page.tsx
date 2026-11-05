"use client";

import React, { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  MarkerType,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import {
  Network,
  Play,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  Radio,
  Building2,
  DollarSign,
  Cpu,
  Mail,
  ShieldAlert,
} from "lucide-react";
import { api } from "@/lib/api";
import { Header } from "@/components/layout/Header";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/Card";
import { Badge, StatusBadge } from "@/components/ui/Badge";
import { formatDate } from "@/lib/utils";

// Custom Node for React Flow
function AgentNode({ data }: { data: any }) {
  const Icon = data.icon || Network;
  return (
    <div
      className={`px-4 py-3 rounded-lg border backdrop-blur shadow-lg min-w-[180px] transition-all ${
        data.active
          ? "border-brand-400 bg-brand-950/40 glow-purple"
          : data.status === "ONLINE"
          ? "border-emerald-500/30 bg-surface-100"
          : "border-border bg-surface-100/80"
      }`}
    >
      <div className="flex items-center justify-between gap-2 mb-1.5">
        <div className="flex items-center gap-1.5">
          <Icon className="w-3.5 h-3.5 text-brand-400" />
          <span className="text-xs font-semibold text-white">{data.label}</span>
        </div>
        <span
          className={`w-2 h-2 rounded-full ${
            data.active
              ? "bg-brand-400 animate-ping"
              : data.status === "ONLINE"
              ? "bg-emerald-400"
              : "bg-gray-500"
          }`}
        />
      </div>
      <p className="text-[10px] text-gray-400 leading-tight">{data.role}</p>
      <div className="mt-2 pt-1.5 border-t border-border/50 flex items-center justify-between text-[9px] font-mono text-gray-500">
        <span>{data.status}</span>
        <span className="text-gray-400">{data.duration}</span>
      </div>
    </div>
  );
}

const nodeTypes = {
  agentNode: AgentNode,
};

export default function AgentMonitorPage() {
  const queryClient = useQueryClient();
  const [triggerStatus, setTriggerStatus] = useState<string | null>(null);

  const { data: metrics } = useQuery({
    queryKey: ["orchestratorMetrics"],
    queryFn: () => api.getOrchestratorMetrics(),
  });

  const { data: workflows, refetch: refetchWorkflows } = useQuery({
    queryKey: ["orchestratorWorkflows"],
    queryFn: () => api.listWorkflows({ limit: 10 }),
  });

  const runMutation = useMutation({
    mutationFn: () =>
      api.runWorkflow({
        target_challenger: "SigNoz Cloud",
        include_synthetic: true,
        timeout_seconds: 60,
      }),
    onSuccess: (data) => {
      setTriggerStatus(`Workflow ${data.workflow_id.slice(0, 8)} successfully dispatched!`);
      queryClient.invalidateQueries({ queryKey: ["orchestratorWorkflows"] });
      queryClient.invalidateQueries({ queryKey: ["orchestratorMetrics"] });
      setTimeout(() => setTriggerStatus(null), 5000);
    },
    onError: (err: any) => {
      setTriggerStatus(`Execution error: ${err.message}`);
      setTimeout(() => setTriggerStatus(null), 5000);
    },
  });

  // Construct React Flow graph
  const nodes: Node[] = useMemo(
    () => [
      {
        id: "listener",
        type: "agentNode",
        position: { x: 50, y: 120 },
        data: {
          label: "1. Listener Agent",
          role: "Multi-Source Distress Streams",
          status: "ONLINE",
          duration: "~180ms",
          icon: Radio,
        },
      },
      {
        id: "profiler",
        type: "agentNode",
        position: { x: 280, y: 120 },
        data: {
          label: "2. Profiler Agent",
          role: "Entity Resolution & ICP Scorer",
          status: "ONLINE",
          duration: "~320ms",
          icon: Building2,
        },
      },
      {
        id: "finops",
        type: "agentNode",
        position: { x: 510, y: 50 },
        data: {
          label: "3. FinOps Engine",
          role: "5-Platform Pricing Delta",
          status: "ONLINE",
          duration: "~150ms",
          icon: DollarSign,
        },
      },
      {
        id: "architect",
        type: "agentNode",
        position: { x: 510, y: 190 },
        data: {
          label: "4. Architect Agent",
          role: "OTel Port 8126 Collector Blueprint",
          status: "ONLINE",
          duration: "~210ms",
          icon: Cpu,
        },
      },
      {
        id: "copywriter",
        type: "agentNode",
        position: { x: 740, y: 120 },
        data: {
          label: "5. Copywriter Agent",
          role: "Collateral & Evidence Guard",
          status: "ONLINE",
          duration: "~280ms",
          icon: Mail,
        },
      },
      {
        id: "governance",
        type: "agentNode",
        position: { x: 970, y: 120 },
        data: {
          label: "6. Human Approval Gate",
          role: "Strict Review Before Export",
          status: "PROTECTED",
          duration: "Human-gated",
          icon: ShieldAlert,
          active: true,
        },
      },
    ],
    []
  );

  const edges: Edge[] = useMemo(
    () => [
      {
        id: "e1-2",
        source: "listener",
        target: "profiler",
        animated: true,
        style: { stroke: "#6366f1", strokeWidth: 2 },
        markerEnd: { type: MarkerType.ArrowClosed, color: "#6366f1" },
      },
      {
        id: "e2-3",
        source: "profiler",
        target: "finops",
        animated: true,
        style: { stroke: "#6366f1", strokeWidth: 2 },
        markerEnd: { type: MarkerType.ArrowClosed, color: "#6366f1" },
      },
      {
        id: "e2-4",
        source: "profiler",
        target: "architect",
        animated: true,
        style: { stroke: "#6366f1", strokeWidth: 2 },
        markerEnd: { type: MarkerType.ArrowClosed, color: "#6366f1" },
      },
      {
        id: "e3-5",
        source: "finops",
        target: "copywriter",
        animated: true,
        style: { stroke: "#6366f1", strokeWidth: 2 },
        markerEnd: { type: MarkerType.ArrowClosed, color: "#6366f1" },
      },
      {
        id: "e4-5",
        source: "architect",
        target: "copywriter",
        animated: true,
        style: { stroke: "#6366f1", strokeWidth: 2 },
        markerEnd: { type: MarkerType.ArrowClosed, color: "#6366f1" },
      },
      {
        id: "e5-6",
        source: "copywriter",
        target: "governance",
        animated: true,
        style: { stroke: "#f59e0b", strokeWidth: 2 },
        markerEnd: { type: MarkerType.ArrowClosed, color: "#f59e0b" },
      },
    ],
    []
  );

  return (
    <div className="flex-1 flex flex-col min-w-0">
      <Header
        title="Agent Topology & Orchestration Monitor"
        description="Interactive multi-agent execution DAG visualizer, state machine transitions, and concurrency telemetry."
      />

      <div className="p-6 space-y-6 max-w-7xl mx-auto w-full">
        {/* Action Header */}
        <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-lg bg-surface-100 border border-border">
          <div>
            <span className="text-xs font-semibold text-white block">Multi-Agent Orchestrator</span>
            <span className="text-[11px] text-gray-400">
              Total Executed: {metrics?.total_workflows || 0} &bull; Pending Review: {metrics?.pending_approval_count || 0}
            </span>
          </div>

          <div className="flex items-center gap-3">
            {triggerStatus && (
              <span className="text-xs font-mono px-3 py-1 rounded bg-brand-500/20 text-brand-300 border border-brand-500/30">
                {triggerStatus}
              </span>
            )}

            <button
              onClick={() => runMutation.mutate()}
              disabled={runMutation.isPending}
              className="flex items-center gap-1.5 px-4 py-2 rounded bg-brand-600 hover:bg-brand-500 text-white text-xs font-medium transition cursor-pointer shadow-sm shadow-brand-500/30 disabled:opacity-50"
            >
              {runMutation.isPending ? (
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Play className="w-3.5 h-3.5 fill-current" />
              )}
              <span>{runMutation.isPending ? "Executing..." : "Dispatch Full Pipeline"}</span>
            </button>
          </div>
        </div>

        {/* Interactive React Flow Diagram */}
        <Card className="p-0 overflow-hidden h-[360px] border-border bg-[#090b10] relative">
          <div className="absolute top-3 left-4 z-10 text-[10px] font-mono text-gray-400 uppercase tracking-wider bg-surface-100/80 px-2 py-1 rounded border border-border">
            Execution DAG Flow (Left to Right)
          </div>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            nodeTypes={nodeTypes}
            fitView
            proOptions={{ hideAttribution: true }}
            className="bg-[#090b10]"
          >
            <Background color="#1c212e" gap={18} size={1} />
            <Controls className="!bg-surface-100 !border-border text-gray-300" />
          </ReactFlow>
        </Card>

        {/* Live Workflow History Table */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Recent Workflow Orchestrations</CardTitle>
                <CardDescription>Step execution history and state machine transitions.</CardDescription>
              </div>
              <button
                onClick={() => refetchWorkflows()}
                className="p-1.5 rounded bg-surface-50 hover:bg-surface-200 border border-border text-gray-400 hover:text-white transition"
              >
                <RefreshCw className="w-3.5 h-3.5" />
              </button>
            </div>
          </CardHeader>
          <CardContent>
            {workflows && workflows.workflows.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                  <thead>
                    <tr className="border-b border-border text-[10px] font-mono text-gray-400 uppercase bg-surface-50/50">
                      <th className="py-2.5 px-3">Workflow ID</th>
                      <th className="py-2.5 px-3">Type</th>
                      <th className="py-2.5 px-3">Status</th>
                      <th className="py-2.5 px-3">Target</th>
                      <th className="py-2.5 px-3">Current Step</th>
                      <th className="py-2.5 px-3">Duration</th>
                      <th className="py-2.5 px-3">Retries</th>
                      <th className="py-2.5 px-3 text-right">Timestamp</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/50 font-mono">
                    {workflows.workflows.map((wf) => (
                      <tr key={wf.workflow_id} className="hover:bg-surface-50/50">
                        <td className="py-3 px-3 font-bold text-white">{wf.workflow_id.slice(0, 8)}...</td>
                        <td className="py-3 px-3 text-gray-400">{wf.workflow_type}</td>
                        <td className="py-3 px-3 font-sans">
                          <StatusBadge status={wf.status} />
                        </td>
                        <td className="py-3 px-3 text-gray-300">{wf.target_challenger}</td>
                        <td className="py-3 px-3 text-brand-300">{wf.current_step}</td>
                        <td className="py-3 px-3 text-gray-400">
                          {wf.execution_duration_ms > 0 ? `${(wf.execution_duration_ms / 1000).toFixed(1)}s` : "-"}
                        </td>
                        <td className="py-3 px-3 text-gray-400">{wf.retry_count}/{wf.max_retries}</td>
                        <td className="py-3 px-3 text-right text-gray-500 font-sans">{formatDate(wf.created_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="p-8 text-center text-xs text-gray-500">No workflow history available.</div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
