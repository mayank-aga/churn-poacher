"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Building2,
  Search,
  Filter,
  ArrowUpRight,
  Play,
  ShieldCheck,
  RefreshCw,
  TrendingUp,
} from "lucide-react";
import { api } from "@/lib/api";
import { Header } from "@/components/layout/Header";
import { Card, CardContent } from "@/components/ui/Card";
import { Badge, StatusBadge } from "@/components/ui/Badge";
import { formatDate } from "@/lib/utils";

export default function CompaniesPage() {
  const queryClient = useQueryClient();
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [activeCompanyId, setActiveCompanyId] = useState<string | null>(null);

  const { data: companies, isLoading, refetch } = useQuery({
    queryKey: ["companies", statusFilter],
    queryFn: () =>
      api.getCompanies({
        qualification_status: statusFilter || undefined,
        limit: 100,
      }),
  });

  const investigateMutation = useMutation({
    mutationFn: (companyId: string) =>
      api.runWorkflow({
        company_id: companyId,
        target_challenger: "SigNoz Cloud",
        timeout_seconds: 45,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["companies"] });
      queryClient.invalidateQueries({ queryKey: ["dossiers"] });
    },
  });

  const filteredCompanies = (companies || []).filter((c) => {
    if (!searchQuery) return true;
    return (
      c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (c.domain && c.domain.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (c.industry && c.industry.toLowerCase().includes(searchQuery.toLowerCase()))
    );
  });

  return (
    <div className="flex-1 flex flex-col min-w-0">
      <Header
        title="Verified Companies & Prospects"
        description="Resolved corporate entities, tech stack profiles, and explainable ICP qualification scoring."
      />

      <div className="p-6 space-y-6 max-w-7xl mx-auto w-full">
        {/* Search & Filter Bar */}
        <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-lg bg-surface-100 border border-border">
          <div className="flex items-center gap-3 flex-1 min-w-[240px]">
            <Search className="w-4 h-4 text-gray-500" />
            <input
              type="text"
              placeholder="Search companies, domains, industries..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-transparent border-none text-xs text-white placeholder-gray-500 focus:outline-none w-full"
            />
          </div>

          <div className="flex items-center gap-3">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-surface-50 border border-border text-xs text-gray-300 rounded px-2.5 py-1.5 focus:outline-none"
            >
              <option value="">All Qualifications</option>
              <option value="ACCEPTED">Accepted (High Conviction)</option>
              <option value="REVIEW_REQUIRED">Review Required</option>
              <option value="REJECTED">Rejected</option>
            </select>

            <button
              onClick={() => refetch()}
              className="p-1.5 rounded bg-surface-50 hover:bg-surface-200 border border-border text-gray-400 hover:text-white transition"
              title="Refresh companies"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Companies Table / List */}
        <Card className="p-0 overflow-hidden">
          <div className="p-4 border-b border-border/80 flex items-center justify-between">
            <span className="text-xs font-mono text-gray-400">
              Showing {filteredCompanies.length} profiled organizations
            </span>
            <span className="text-[11px] text-gray-500 font-mono">
              Qualification Threshold: ICP Fit &ge; 75%
            </span>
          </div>

          {isLoading ? (
            <div className="p-12 text-center text-xs text-gray-500">Loading company profiles...</div>
          ) : filteredCompanies.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead>
                  <tr className="border-b border-border text-[10px] font-mono text-gray-400 uppercase bg-surface-50/50">
                    <th className="py-3 px-4">Company</th>
                    <th className="py-3 px-4">Industry / Scale</th>
                    <th className="py-3 px-4">ICP Fit Score</th>
                    <th className="py-3 px-4">Confidence Ratings</th>
                    <th className="py-3 px-4">Qualification</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/50">
                  {filteredCompanies.map((c) => {
                    const isRunning = investigateMutation.isPending && activeCompanyId === c.id;
                    return (
                      <tr key={c.id} className="hover:bg-surface-50/50 transition">
                        <td className="py-3.5 px-4">
                          <div className="flex items-center gap-2">
                            <Link
                              href={`/companies/${c.id}`}
                              className="font-medium text-white hover:text-brand-400 text-xs transition"
                            >
                              {c.name}
                            </Link>
                            {c.is_synthetic && <Badge variant="synthetic">SYNTHETIC</Badge>}
                          </div>
                          {c.domain && (
                            <span className="text-[11px] font-mono text-gray-500 block mt-0.5">{c.domain}</span>
                          )}
                        </td>

                        <td className="py-3.5 px-4 text-gray-300">
                          <div>{c.industry || "Technology"}</div>
                          <div className="text-[10px] text-gray-500">{c.estimated_size}</div>
                        </td>

                        <td className="py-3.5 px-4">
                          <div className="flex items-center gap-2">
                            <span className="font-mono font-bold text-sm text-emerald-400">
                              {(c.icp_score * 100).toFixed(0)}%
                            </span>
                            <div className="w-16 h-1.5 rounded-full bg-surface-200 overflow-hidden">
                              <div
                                className="h-full bg-gradient-to-r from-brand-500 to-emerald-400 rounded-full"
                                style={{ width: `${c.icp_score * 100}%` }}
                              />
                            </div>
                          </div>
                        </td>

                        <td className="py-3.5 px-4">
                          <div className="text-[11px] font-mono text-gray-400 space-y-0.5">
                            <div>ID: {(c.identity_confidence * 100).toFixed(0)}%</div>
                            <div>Tech: {(c.technology_confidence * 100).toFixed(0)}%</div>
                          </div>
                        </td>

                        <td className="py-3.5 px-4">
                          <StatusBadge status={c.qualification_status} />
                        </td>

                        <td className="py-3.5 px-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <Link
                              href={`/companies/${c.id}`}
                              className="px-2.5 py-1 rounded bg-surface-50 hover:bg-surface-200 border border-border text-gray-300 hover:text-white transition text-[11px] font-medium"
                            >
                              Dossier
                            </Link>
                            <button
                              onClick={() => {
                                setActiveCompanyId(c.id);
                                investigateMutation.mutate(c.id);
                              }}
                              disabled={isRunning}
                              className="px-2.5 py-1 rounded bg-brand-600 hover:bg-brand-500 text-white transition text-[11px] font-medium disabled:opacity-50 cursor-pointer flex items-center gap-1"
                            >
                              {isRunning ? <RefreshCw className="w-3 h-3 animate-spin" /> : <Play className="w-3 h-3 fill-current" />}
                              <span>{isRunning ? "Running" : "Poach"}</span>
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-12 text-center text-xs text-gray-500">
              No companies match your search or filter.
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
