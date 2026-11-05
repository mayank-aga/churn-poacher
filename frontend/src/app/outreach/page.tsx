"use client";

import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Mail,
  CheckCircle2,
  XCircle,
  Download,
  AlertTriangle,
  RotateCw,
  Copy,
  ExternalLink,
  ShieldAlert,
  Sparkles,
  Check,
} from "lucide-react";
import { api } from "@/lib/api";
import { Header } from "@/components/layout/Header";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/Card";
import { Badge, StatusBadge } from "@/components/ui/Badge";
import { formatCurrency } from "@/lib/utils";

export default function OutreachStudioPage() {
  const queryClient = useQueryClient();
  const [selectedCompanyId, setSelectedCompanyId] = useState<string>("");
  const [rejectReason, setRejectReason] = useState("");
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [copiedSection, setCopiedSection] = useState<string | null>(null);
  const [actionAlert, setActionAlert] = useState<string | null>(null);

  const { data: companies } = useQuery({
    queryKey: ["companiesForOutreach"],
    queryFn: () => api.getCompanies({ limit: 50 }),
  });

  const activeCompanyId = selectedCompanyId || (companies && companies.length > 0 ? companies[0].id : "");

  const { data: draftData, isLoading: loadingDraft } = useQuery({
    queryKey: ["copywriterDraft", activeCompanyId],
    queryFn: () => api.getCopywriterDrafts(activeCompanyId),
    enabled: Boolean(activeCompanyId),
  });

  const { data: copyMetrics } = useQuery({
    queryKey: ["copywriterMetrics"],
    queryFn: () => api.getCopywriterMetrics(),
  });

  const dossierId = draftData?.dossier_id;
  const dossierStatus = draftData?.status || "DRAFT_PENDING_APPROVAL";
  const pack = draftData?.outreach_package;

  // Mutations
  const approveMutation = useMutation({
    mutationFn: (dId: string) => api.approveDraft(dId),
    onSuccess: () => {
      setActionAlert("Draft successfully approved! Export is unlocked.");
      queryClient.invalidateQueries({ queryKey: ["copywriterDraft", activeCompanyId] });
      queryClient.invalidateQueries({ queryKey: ["copywriterMetrics"] });
      setTimeout(() => setActionAlert(null), 4000);
    },
    onError: (err: any) => setActionAlert(`Approval failed: ${err.message}`),
  });

  const rejectMutation = useMutation({
    mutationFn: ({ dId, reason }: { dId: string; reason: string }) =>
      api.rejectDraft(dId, reason),
    onSuccess: () => {
      setActionAlert("Draft marked as rejected with revision notes.");
      setShowRejectModal(false);
      queryClient.invalidateQueries({ queryKey: ["copywriterDraft", activeCompanyId] });
      queryClient.invalidateQueries({ queryKey: ["copywriterMetrics"] });
      setTimeout(() => setActionAlert(null), 4000);
    },
    onError: (err: any) => setActionAlert(`Rejection failed: ${err.message}`),
  });

  const regenerateMutation = useMutation({
    mutationFn: () => api.runCopywriter(activeCompanyId, "SigNoz Cloud"),
    onSuccess: () => {
      setActionAlert("Outreach package regenerated with refreshed evidence!");
      queryClient.invalidateQueries({ queryKey: ["copywriterDraft", activeCompanyId] });
      setTimeout(() => setActionAlert(null), 4000);
    },
    onError: (err: any) => setActionAlert(`Regeneration failed: ${err.message}`),
  });

  const exportMutation = useMutation({
    mutationFn: (dId: string) => api.exportDossier(dId),
    onSuccess: (data) => {
      const blob = new Blob([data.markdown_bundle], { type: "text/markdown" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `deposition-pack-${data.company_name.toLowerCase().replace(/\s+/g, "-")}.md`;
      a.click();
      setActionAlert("Markdown bundle downloaded successfully!");
      setTimeout(() => setActionAlert(null), 4000);
    },
    onError: (err: any) => setActionAlert(`Export blocked: ${err.message}`),
  });

  const handleCopy = (text: string, sectionId: string) => {
    navigator.clipboard.writeText(text);
    setCopiedSection(sectionId);
    setTimeout(() => setCopiedSection(null), 2000);
  };

  return (
    <div className="flex-1 flex flex-col min-w-0">
      <Header
        title="Outreach Studio"
        description="Evidence-backed competitive deposition collateral: executive emails, LinkedIn sequences, and objection handlers."
      />

      <div className="p-6 space-y-6 max-w-7xl mx-auto w-full">
        {/* Metric Bar */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="p-4 rounded-lg bg-surface-100 border border-border">
            <span className="text-[10px] font-mono text-gray-400 uppercase block">Total Generated Packs</span>
            <div className="text-2xl font-bold text-white font-mono mt-1">
              {copyMetrics?.total_dossiers_with_drafts || 0}
            </div>
          </div>
          <div className="p-4 rounded-lg bg-surface-100 border border-border">
            <span className="text-[10px] font-mono text-amber-400 uppercase block">Pending Human Review</span>
            <div className="text-2xl font-bold text-amber-400 font-mono mt-1">
              {copyMetrics?.pending_human_approval || 0}
            </div>
          </div>
          <div className="p-4 rounded-lg bg-surface-100 border border-border">
            <span className="text-[10px] font-mono text-emerald-400 uppercase block">Approved Packs</span>
            <div className="text-2xl font-bold text-emerald-400 font-mono mt-1">
              {copyMetrics?.approved || 0}
            </div>
          </div>
          <div className="p-4 rounded-lg bg-surface-100 border border-border">
            <span className="text-[10px] font-mono text-gray-400 uppercase block">Governance Enforcement</span>
            <div className="text-xs font-semibold text-emerald-400 mt-1">
              Export Gate Active
            </div>
            <span className="text-[10px] text-gray-500 block">Strictly requires human sign-off</span>
          </div>
        </div>

        {/* Company Selector & Action Header */}
        <div className="p-4 rounded-lg bg-surface-100 border border-border flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="text-xs text-gray-400 font-medium">Select Company:</span>
            <select
              value={activeCompanyId}
              onChange={(e) => setSelectedCompanyId(e.target.value)}
              className="bg-surface-50 border border-border text-xs text-white rounded px-3 py-1.5 focus:outline-none"
            >
              {(companies || []).map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name} ({c.qualification_status})
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2">
            <StatusBadge status={dossierStatus} />

            <button
              onClick={() => regenerateMutation.mutate()}
              disabled={regenerateMutation.isPending || !activeCompanyId}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-surface-50 hover:bg-surface-200 border border-border text-xs text-gray-300 font-medium transition cursor-pointer"
            >
              <RotateCw className={`w-3.5 h-3.5 ${regenerateMutation.isPending ? "animate-spin" : ""}`} />
              <span>Regenerate</span>
            </button>

            {dossierStatus !== "APPROVED" ? (
              <>
                <button
                  onClick={() => approveMutation.mutate(dossierId!)}
                  disabled={approveMutation.isPending || !dossierId}
                  className="flex items-center gap-1.5 px-3.5 py-1.5 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium transition cursor-pointer"
                >
                  <CheckCircle2 className="w-3.5 h-3.5" /> Approve
                </button>
                <button
                  onClick={() => setShowRejectModal(true)}
                  disabled={!dossierId}
                  className="flex items-center gap-1.5 px-3.5 py-1.5 rounded bg-rose-900/40 hover:bg-rose-800/60 border border-rose-500/30 text-rose-300 text-xs font-medium transition cursor-pointer"
                >
                  <XCircle className="w-3.5 h-3.5" /> Reject
                </button>
              </>
            ) : null}

            <button
              onClick={() => exportMutation.mutate(dossierId!)}
              disabled={dossierStatus !== "APPROVED" || exportMutation.isPending}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded bg-brand-600 hover:bg-brand-500 disabled:opacity-40 text-white text-xs font-medium transition cursor-pointer shadow-sm"
              title={dossierStatus !== "APPROVED" ? "Requires approval first" : "Export markdown bundle"}
            >
              <Download className="w-3.5 h-3.5" /> Export Pack
            </button>
          </div>
        </div>

        {actionAlert && (
          <div className="p-3 rounded bg-brand-500/20 text-brand-300 border border-brand-500/30 text-xs font-mono">
            {actionAlert}
          </div>
        )}

        {/* Rejection Modal */}
        {showRejectModal && (
          <div className="p-4 rounded-lg bg-rose-950/20 border border-rose-500/40 space-y-3">
            <div className="text-xs font-semibold text-rose-300">Specify Rejection Reason</div>
            <textarea
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              placeholder="Explain why this outreach collateral requires revision..."
              className="w-full h-20 p-2.5 rounded bg-surface-200 border border-border text-xs text-white focus:outline-none"
            />
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowRejectModal(false)}
                className="px-3 py-1 rounded bg-surface-50 text-xs text-gray-300"
              >
                Cancel
              </button>
              <button
                onClick={() => rejectMutation.mutate({ dId: dossierId!, reason: rejectReason })}
                className="px-3 py-1 rounded bg-rose-600 text-white text-xs font-medium"
              >
                Confirm Rejection
              </button>
            </div>
          </div>
        )}

        {/* Evidence Guard Audit Badge Banner */}
        {pack?.evidence_audit && (
          <Card className="border-emerald-500/30 bg-emerald-950/15">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400">
                  <CheckCircle2 className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-semibold text-white">Evidence Guard Anti-Hallucination Audit Passed</h4>
                  <p className="text-[11px] text-gray-400 mt-0.5">{pack.evidence_audit.audit_summary}</p>
                </div>
              </div>
              <div className="text-right font-mono text-xs">
                <span className="text-emerald-400 font-bold">Risk Score: {pack.evidence_audit.hallucination_risk_score}</span>
                <span className="text-[10px] text-gray-500 block">{pack.evidence_audit.claims_checked} claims verified</span>
              </div>
            </div>
          </Card>
        )}

        {/* Main Content: Email Variants, LinkedIn, Objections */}
        {loadingDraft ? (
          <div className="p-12 text-center text-xs text-gray-500">Loading generated sales collateral...</div>
        ) : pack ? (
          <div className="space-y-6">
            {/* Email Variants */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {(pack.executive_emails || []).map((email: any, idx: number) => {
                const secId = `email-${idx}`;
                return (
                  <Card key={idx} className="flex flex-col justify-between">
                    <div>
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <CardTitle className="text-xs">{email.variant_type}</CardTitle>
                          <Badge variant="purple">{email.target_role}</Badge>
                        </div>
                        <CardDescription>Preheader: {email.preheader}</CardDescription>
                      </CardHeader>
                      <CardContent className="space-y-3 text-xs">
                        <div>
                          <span className="text-[10px] font-mono text-gray-400 uppercase block mb-1">Subject Lines</span>
                          <ul className="space-y-1 font-mono text-gray-300 text-[11px]">
                            {email.subject_lines?.map((subj: string, sIdx: number) => (
                              <li key={sIdx} className="p-1.5 rounded bg-surface-50 border border-border">
                                {subj}
                              </li>
                            ))}
                          </ul>
                        </div>

                        <div>
                          <span className="text-[10px] font-mono text-gray-400 uppercase block mb-1">Body</span>
                          <div className="p-3.5 rounded bg-surface-50 border border-border whitespace-pre-line text-gray-200 leading-relaxed font-sans text-xs">
                            {email.body_markdown}
                          </div>
                        </div>
                      </CardContent>
                    </div>

                    <div className="p-4 pt-0 flex justify-end">
                      <button
                        onClick={() => handleCopy(email.body_markdown, secId)}
                        className="flex items-center gap-1.5 px-3 py-1 rounded bg-surface-50 hover:bg-surface-200 border border-border text-gray-300 text-[11px] font-mono"
                      >
                        {copiedSection === secId ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                        <span>{copiedSection === secId ? "Copied" : "Copy Email"}</span>
                      </button>
                    </div>
                  </Card>
                );
              })}
            </div>

            {/* LinkedIn Sequence */}
            {pack.linkedin_sequence && (
              <Card>
                <CardHeader>
                  <CardTitle>LinkedIn Multi-Touch Cadence</CardTitle>
                  <CardDescription>Engineering peer tone with strict connection length constraints.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3 text-xs">
                  <div className="p-3 rounded bg-surface-50 border border-border">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-[10px] font-mono text-brand-400 uppercase">Touch 1: Connection Request (&le; 300 chars)</span>
                      <span className="text-[10px] font-mono text-gray-500">
                        {pack.linkedin_sequence.step_1_connection_request.length}/300 chars
                      </span>
                    </div>
                    <p className="text-gray-300 font-mono text-[11px]">{pack.linkedin_sequence.step_1_connection_request}</p>
                  </div>

                  <div className="p-3 rounded bg-surface-50 border border-border">
                    <span className="text-[10px] font-mono text-brand-400 uppercase block mb-1">Touch 2: Value-Add Follow-Up</span>
                    <p className="text-gray-300 whitespace-pre-line text-[11px]">{pack.linkedin_sequence.step_2_value_add}</p>
                  </div>

                  <div className="p-3 rounded bg-surface-50 border border-border">
                    <span className="text-[10px] font-mono text-brand-400 uppercase block mb-1">Touch 3: Technical-Commercial Follow-Up</span>
                    <p className="text-gray-300 whitespace-pre-line text-[11px]">{pack.linkedin_sequence.step_3_technical_commercial}</p>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Objection Matrix */}
            <Card>
              <CardHeader>
                <CardTitle>Enterprise Objection Handling Matrix</CardTitle>
                <CardDescription>Pre-armed responses and technical proofs for top objections.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3 text-xs">
                {(pack.objection_matrix?.items || []).map((obj: any) => (
                  <div key={obj.objection_id} className="p-3.5 rounded bg-surface-50 border border-border space-y-1.5">
                    <div className="font-semibold text-rose-300 flex items-center gap-1.5">
                      <AlertTriangle className="w-3.5 h-3.5" /> {obj.objection}
                    </div>
                    <p className="text-gray-300 leading-relaxed text-[11px]">{obj.recommended_response}</p>
                    <div className="pt-1 text-[10px] font-mono text-emerald-400">
                      Proof Point: {obj.technical_proof_point}
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        ) : (
          <div className="p-12 text-center text-xs text-gray-500 bg-surface-100 rounded-lg border border-border">
            No outreach drafts found for this organization. Click &quot;Regenerate&quot; to synthesize sales collateral.
          </div>
        )}
      </div>
    </div>
  );
}
