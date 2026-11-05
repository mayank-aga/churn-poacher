"use client";

import React, { useState, useEffect } from "react";
import {
  Compass,
  Search,
  Building2,
  User,
  Zap,
  ShieldCheck,
  Coins,
  History,
  Download,
  Copy,
  ExternalLink,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Cpu,
  DollarSign,
  Briefcase,
  Users,
  Award,
  Globe,
  ArrowRight,
  Layers,
} from "lucide-react";
import { api } from "@/lib/api";
import {
  CrustdataCreditsInfo,
  EntitySearchResponse,
  EntityCandidate,
  CompanyIntelligenceProfile,
  PersonIntelligenceProfile,
  CrustdataEntityType,
  CrustdataEnrichmentLevel,
  DeepEnrichmentCostEstimate,
} from "@/types";
import { formatCurrency } from "@/lib/utils";

export default function CrustdataExplorerPage() {
  const [query, setQuery] = useState("");
  const [entityTypeFilter, setEntityTypeFilter] = useState<CrustdataEntityType>("UNKNOWN");
  const [credits, setCredits] = useState<CrustdataCreditsInfo | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [isEnriching, setIsEnriching] = useState(false);
  const [searchResults, setSearchResults] = useState<EntitySearchResponse | null>(null);
  const [activeProfile, setActiveProfile] = useState<CompanyIntelligenceProfile | PersonIntelligenceProfile | null>(null);
  const [activeTab, setActiveTab] = useState<string>("technographics");
  const [searchHistory, setSearchHistory] = useState<any[]>([]);
  const [deepCostEstimate, setDeepCostEstimate] = useState<DeepEnrichmentCostEstimate | null>(null);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [exportNotice, setExportNotice] = useState<string | null>(null);

  useEffect(() => {
    loadCredits();
    loadSearchHistory();
  }, []);

  const loadCredits = async () => {
    try {
      const data = await api.getCrustdataCredits();
      setCredits(data);
    } catch (err) {
      console.error("Failed to load credits:", err);
    }
  };

  const loadSearchHistory = async () => {
    try {
      const hist = await api.getCrustdataSearchHistory(10);
      setSearchHistory(hist);
    } catch (err) {
      console.error("Failed to load history:", err);
    }
  };

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;

    setIsSearching(true);
    setSearchResults(null);
    setActiveProfile(null);
    setDeepCostEstimate(null);

    try {
      const filter = entityTypeFilter === "UNKNOWN" ? undefined : entityTypeFilter;
      const res = await api.searchCrustdata({ query: query.trim(), entity_type: filter, limit: 6 });
      setSearchResults(res);
      loadCredits();
      loadSearchHistory();

      // If single unambiguous candidate returned, auto-enrich standard profile
      if (res.candidates.length === 1 && !res.is_ambiguous) {
        const singleCand = res.candidates[0];
        handleEnrichCandidate(singleCand, "LEVEL_2_STANDARD");
      }
    } catch (err: any) {
      alert(`Search failed: ${err.message || err}`);
    } finally {
      setIsSearching(false);
    }
  };

  const handleEnrichCandidate = async (
    candidate: EntityCandidate,
    level: CrustdataEnrichmentLevel = "LEVEL_2_STANDARD",
    confirmationConfirmed = false
  ) => {
    setIsEnriching(true);
    setDeepCostEstimate(null);

    try {
      const targetId = candidate.primary_domain || candidate.profile_url || candidate.name;
      const res = await api.enrichCrustdata({
        identifier: targetId,
        entity_type: candidate.entity_type,
        level,
        confirmation_confirmed: confirmationConfirmed,
      });

      if (res.estimated_credits && !confirmationConfirmed) {
        // Deep enrichment requires explicit confirmation
        setDeepCostEstimate(res as DeepEnrichmentCostEstimate);
        setShowConfirmModal(true);
      } else {
        setActiveProfile(res);
        if (candidate.entity_type === "COMPANY") {
          setActiveTab("technographics");
        } else {
          setActiveTab("profile");
        }
        setShowConfirmModal(false);
      }
      loadCredits();
    } catch (err: any) {
      alert(`Enrichment failed: ${err.message || err}`);
    } finally {
      setIsEnriching(false);
    }
  };

  const handleConfirmDeepEnrichment = () => {
    if (!deepCostEstimate) return;
    const dummyCand: EntityCandidate = {
      candidate_id: deepCostEstimate.target_identifier,
      entity_type: deepCostEstimate.entity_type,
      name: deepCostEstimate.entity_name,
      primary_domain: deepCostEstimate.target_identifier,
      confidence_score: 1.0,
      is_ambiguous: false,
      is_mock: false,
    };
    handleEnrichCandidate(dummyCand, "LEVEL_3_DEEP", true);
  };

  const handleExport = async (format: "markdown" | "json") => {
    if (!activeProfile) return;
    try {
      const res = await api.exportCrustdataReport(activeProfile.entity_id, format);
      if (format === "markdown") {
        navigator.clipboard.writeText(res.content);
        setExportNotice("Intelligence Report copied to clipboard as Markdown!");
      } else {
        const blob = new Blob([JSON.stringify(res, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `crustdata_${activeProfile.entity_id}.json`;
        a.click();
        setExportNotice("JSON file downloaded!");
      }
      setTimeout(() => setExportNotice(null), 3500);
    } catch (err: any) {
      alert(`Export failed: ${err.message || err}`);
    }
  };

  const quickSearch = (term: string) => {
    setQuery(term);
    setTimeout(() => {
      // Trigger programmatic search
      api.searchCrustdata({ query: term, limit: 6 }).then((res) => {
        setSearchResults(res);
        if (res.candidates.length === 1 && !res.is_ambiguous) {
          handleEnrichCandidate(res.candidates[0], "LEVEL_2_STANDARD");
        }
        loadCredits();
      });
    }, 50);
  };

  const isCompany = activeProfile && "technographics" in activeProfile;
  const companyProfile = isCompany ? (activeProfile as CompanyIntelligenceProfile) : null;
  const personProfile = !isCompany ? (activeProfile as PersonIntelligenceProfile) : null;

  return (
    <div className="space-y-6">
      {/* Header & Credit Meter */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-6">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
              <Compass className="h-6 w-6 text-primary" />
              Crustdata Intelligence Explorer
            </h1>
            <span className="text-xs px-2 py-0.5 rounded-full font-mono font-medium bg-primary/20 text-primary border border-primary/30">
              AI EXTRACTION
            </span>
            {credits?.is_mock && (
              <span className="text-xs px-2 py-0.5 rounded-full font-mono font-medium bg-warning/20 text-warning border border-warning/30">
                OFFLINE / MOCK MODE
              </span>
            )}
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Universal B2B entity search, verified technographics, decision makers, and funding telemetry.
          </p>
        </div>

        {/* Credit Meter Widget */}
        <div className="flex items-center gap-3 bg-surface-100 border border-border px-4 py-2 rounded-lg">
          <Coins className="h-5 w-5 text-warning" />
          <div>
            <div className="text-xs text-muted-foreground font-mono">CRUSTDATA CREDITS</div>
            <div className="text-sm font-bold font-mono">
              {credits ? credits.remaining_credits.toFixed(1) : "—"} / {credits ? credits.total_credits.toFixed(0) : "—"}
            </div>
          </div>
          <button
            onClick={loadCredits}
            className="p-1 hover:bg-surface-200 rounded text-muted-foreground hover:text-foreground"
            title="Refresh Credits"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Omnibar Search Form */}
      <div className="bg-surface-100 border border-border p-4 rounded-xl shadow-sm space-y-3">
        <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter company name, person name, domain (spacex.com), or LinkedIn profile URL..."
              className="w-full pl-9 pr-4 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>

          <select
            value={entityTypeFilter}
            onChange={(e) => setEntityTypeFilter(e.target.value as CrustdataEntityType)}
            className="bg-background border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary"
          >
            <option value="UNKNOWN">Auto-Detect Entity</option>
            <option value="COMPANY">Company Only</option>
            <option value="PERSON">Person Only</option>
          </select>

          <button
            type="submit"
            disabled={isSearching || !query.trim()}
            className="btn btn-primary flex items-center gap-2 whitespace-nowrap"
          >
            {isSearching ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
            Extract Intelligence
          </button>
        </form>

        {/* Quick Example Chips */}
        <div className="flex flex-wrap items-center gap-2 pt-1 text-xs text-muted-foreground">
          <span>Quick queries:</span>
          {["SpaceX", "Elon Musk", "OpenAI", "Sam Altman", "NVIDIA", "Datadog"].map((term) => (
            <button
              key={term}
              onClick={() => quickSearch(term)}
              className="px-2.5 py-1 bg-surface-200 hover:bg-surface-300 text-foreground rounded-md border border-border transition-colors font-mono"
            >
              {term}
            </button>
          ))}
        </div>
      </div>

      {/* Search Candidates (Level 1 Candidate Selection) */}
      {searchResults && searchResults.candidates.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
              <Users className="h-4 w-4" />
              Candidate Matches ({searchResults.candidates.length})
            </h2>
            {searchResults.is_ambiguous && (
              <span className="text-xs px-2 py-0.5 rounded bg-warning/20 text-warning border border-warning/30 flex items-center gap-1">
                <AlertTriangle className="h-3 w-3" />
                Multiple candidates detected — select to enrich
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {searchResults.candidates.map((cand) => (
              <div
                key={cand.candidate_id}
                className="bg-surface-100 border border-border hover:border-primary/50 p-4 rounded-lg flex flex-col justify-between gap-3 transition-colors"
              >
                <div className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-xs px-2 py-0.5 rounded font-mono font-medium bg-surface-200 text-muted-foreground flex items-center gap-1">
                      {cand.entity_type === "COMPANY" ? <Building2 className="h-3 w-3" /> : <User className="h-3 w-3" />}
                      {cand.entity_type}
                    </span>
                    <span className="text-xs text-muted-foreground font-mono">
                      {(cand.confidence_score * 100).toFixed(0)}% match
                    </span>
                  </div>
                  <h3 className="font-semibold text-foreground text-base">{cand.name}</h3>
                  {cand.current_title && (
                    <p className="text-xs font-medium text-primary">
                      {cand.current_title} {cand.company_name ? `@ ${cand.company_name}` : ""}
                    </p>
                  )}
                  {cand.primary_domain && (
                    <p className="text-xs text-muted-foreground font-mono">{cand.primary_domain}</p>
                  )}
                  {cand.headline && <p className="text-xs text-muted-foreground line-clamp-2">{cand.headline}</p>}
                </div>

                <div className="flex items-center gap-2 pt-2 border-t border-border">
                  <button
                    onClick={() => handleEnrichCandidate(cand, "LEVEL_2_STANDARD")}
                    disabled={isEnriching}
                    className="flex-1 btn btn-secondary text-xs py-1.5 flex items-center justify-center gap-1"
                  >
                    <CheckCircle2 className="h-3.5 w-3.5 text-success" />
                    Standard Enrich (1-2 cr)
                  </button>
                  <button
                    onClick={() => handleEnrichCandidate(cand, "LEVEL_3_DEEP")}
                    disabled={isEnriching}
                    className="btn btn-outline text-xs py-1.5 px-2.5 text-warning hover:bg-warning/10"
                    title="Deep Real-Time Scrape"
                  >
                    <Zap className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Export Feedback Banner */}
      {exportNotice && (
        <div className="bg-success/20 border border-success/40 text-success px-4 py-2.5 rounded-lg text-sm flex items-center justify-between">
          <span>{exportNotice}</span>
          <button onClick={() => setExportNotice(null)} className="text-xs underline">
            Dismiss
          </button>
        </div>
      )}

      {/* Main Profile Explorer Display */}
      {activeProfile && (
        <div className="bg-surface-100 border border-border rounded-xl shadow-sm overflow-hidden space-y-6 p-6">
          {/* Entity Profile Header */}
          <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 border-b border-border pb-6">
            <div className="space-y-2">
              <div className="flex flex-wrap items-center gap-2">
                <h2 className="text-2xl font-bold tracking-tight text-foreground">
                  {companyProfile ? companyProfile.name : personProfile?.full_name}
                </h2>
                <span className="text-xs px-2.5 py-0.5 rounded font-mono font-medium bg-primary/20 text-primary border border-primary/30">
                  {companyProfile ? "COMPANY" : "PERSON"}
                </span>
                <span className="text-xs px-2.5 py-0.5 rounded font-mono font-medium bg-surface-200 text-muted-foreground">
                  {activeProfile.data_freshness}
                </span>
                {activeProfile.is_mock && (
                  <span className="text-xs px-2 py-0.5 rounded font-mono bg-warning/20 text-warning border border-warning/30">
                    SYNTHETIC FIXTURE
                  </span>
                )}
              </div>

              {companyProfile && (
                <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                  <span className="font-mono text-primary flex items-center gap-1">
                    <Globe className="h-3.5 w-3.5" />
                    {companyProfile.primary_domain}
                  </span>
                  <span>•</span>
                  <span>{companyProfile.industry || "Technology"}</span>
                  <span>•</span>
                  <span>{companyProfile.headcount || "Unknown size"}</span>
                  <span>•</span>
                  <span>{companyProfile.headquarters || "Global"}</span>
                </div>
              )}

              {personProfile && (
                <div className="space-y-1">
                  <p className="text-base font-semibold text-primary">
                    {personProfile.current_title} {personProfile.current_company ? `@ ${personProfile.current_company}` : ""}
                  </p>
                  <p className="text-xs text-muted-foreground">{personProfile.location}</p>
                </div>
              )}

              <p className="text-sm text-muted-foreground max-w-3xl pt-1">
                {companyProfile?.description || personProfile?.headline || personProfile?.summary_bio}
              </p>
            </div>

            {/* Actions: Export & Deep Refresh */}
            <div className="flex flex-wrap items-center gap-2 self-start">
              <button
                onClick={() => handleExport("markdown")}
                className="btn btn-secondary text-xs flex items-center gap-1.5"
                title="Copy structured report as Markdown"
              >
                <Copy className="h-3.5 w-3.5" />
                Copy Markdown
              </button>
              <button
                onClick={() => handleExport("json")}
                className="btn btn-secondary text-xs flex items-center gap-1.5"
                title="Download JSON report"
              >
                <Download className="h-3.5 w-3.5" />
                JSON
              </button>
              <button
                onClick={() => {
                  const dummyCand: EntityCandidate = {
                    candidate_id: activeProfile.entity_id,
                    entity_type: isCompany ? "COMPANY" : "PERSON",
                    name: companyProfile ? companyProfile.name : personProfile!.full_name,
                    primary_domain: companyProfile?.primary_domain,
                    confidence_score: 1.0,
                    is_ambiguous: false,
                    is_mock: false,
                  };
                  handleEnrichCandidate(dummyCand, "LEVEL_3_DEEP");
                }}
                className="btn btn-outline text-xs text-warning hover:bg-warning/10 flex items-center gap-1.5"
              >
                <Zap className="h-3.5 w-3.5" />
                Deep Real-Time Scrape
              </button>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex items-center gap-2 border-b border-border overflow-x-auto text-sm">
            {companyProfile ? (
              <>
                <button
                  onClick={() => setActiveTab("technographics")}
                  className={`pb-3 px-3 font-medium transition-colors border-b-2 whitespace-nowrap flex items-center gap-2 ${
                    activeTab === "technographics"
                      ? "border-primary text-primary"
                      : "border-transparent text-muted-foreground hover:text-foreground"
                  }`}
                >
                  <Cpu className="h-4 w-4" />
                  Technographics ({companyProfile.technographics.length})
                </button>
                <button
                  onClick={() => setActiveTab("funding")}
                  className={`pb-3 px-3 font-medium transition-colors border-b-2 whitespace-nowrap flex items-center gap-2 ${
                    activeTab === "funding"
                      ? "border-primary text-primary"
                      : "border-transparent text-muted-foreground hover:text-foreground"
                  }`}
                >
                  <DollarSign className="h-4 w-4" />
                  Funding & Investors
                </button>
                <button
                  onClick={() => setActiveTab("leadership")}
                  className={`pb-3 px-3 font-medium transition-colors border-b-2 whitespace-nowrap flex items-center gap-2 ${
                    activeTab === "leadership"
                      ? "border-primary text-primary"
                      : "border-transparent text-muted-foreground hover:text-foreground"
                  }`}
                >
                  <Users className="h-4 w-4" />
                  Leadership ({companyProfile.leadership.length})
                </button>
                <button
                  onClick={() => setActiveTab("jobs")}
                  className={`pb-3 px-3 font-medium transition-colors border-b-2 whitespace-nowrap flex items-center gap-2 ${
                    activeTab === "jobs"
                      ? "border-primary text-primary"
                      : "border-transparent text-muted-foreground hover:text-foreground"
                  }`}
                >
                  <Briefcase className="h-4 w-4" />
                  Hiring & Jobs ({companyProfile.active_jobs.length})
                </button>
                <button
                  onClick={() => setActiveTab("evidence")}
                  className={`pb-3 px-3 font-medium transition-colors border-b-2 whitespace-nowrap flex items-center gap-2 ${
                    activeTab === "evidence"
                      ? "border-primary text-primary"
                      : "border-transparent text-muted-foreground hover:text-foreground"
                  }`}
                >
                  <ShieldCheck className="h-4 w-4" />
                  Provenance Audit ({companyProfile.evidence.length})
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={() => setActiveTab("profile")}
                  className={`pb-3 px-3 font-medium transition-colors border-b-2 whitespace-nowrap flex items-center gap-2 ${
                    activeTab === "profile"
                      ? "border-primary text-primary"
                      : "border-transparent text-muted-foreground hover:text-foreground"
                  }`}
                >
                  <User className="h-4 w-4" />
                  Professional Profile
                </button>
                <button
                  onClick={() => setActiveTab("history")}
                  className={`pb-3 px-3 font-medium transition-colors border-b-2 whitespace-nowrap flex items-center gap-2 ${
                    activeTab === "history"
                      ? "border-primary text-primary"
                      : "border-transparent text-muted-foreground hover:text-foreground"
                  }`}
                >
                  <Briefcase className="h-4 w-4" />
                  Work History ({personProfile?.work_history.length})
                </button>
                <button
                  onClick={() => setActiveTab("evidence")}
                  className={`pb-3 px-3 font-medium transition-colors border-b-2 whitespace-nowrap flex items-center gap-2 ${
                    activeTab === "evidence"
                      ? "border-primary text-primary"
                      : "border-transparent text-muted-foreground hover:text-foreground"
                  }`}
                >
                  <ShieldCheck className="h-4 w-4" />
                  Provenance Audit ({personProfile?.evidence.length})
                </button>
              </>
            )}
          </div>

          {/* TAB 1: TECHNOGRAPHICS (Company) */}
          {companyProfile && activeTab === "technographics" && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <p className="text-xs text-muted-foreground">
                  Verified software installations, cloud providers, and observability stacks detected across public signals and career postings.
                </p>
                <span className="text-xs font-mono text-muted-foreground">
                  {companyProfile.technographics.length} Technologies
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {companyProfile.technographics.map((tech) => {
                  const isDatadog = tech.name.toLowerCase() === "datadog";
                  const isVerified = tech.classification === "VERIFIED";

                  return (
                    <div
                      key={tech.name}
                      className={`p-3.5 rounded-lg border flex flex-col justify-between gap-2 ${
                        isDatadog
                          ? "bg-primary/10 border-primary/40"
                          : "bg-surface-200/50 border-border"
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-semibold text-foreground text-sm">{tech.name}</span>
                            {isDatadog && (
                              <span className="text-[10px] px-1.5 py-0.5 rounded font-mono font-bold bg-primary text-primary-foreground">
                                TARGET
                              </span>
                            )}
                          </div>
                          <span className="text-xs text-muted-foreground">{tech.category}</span>
                        </div>
                        <span
                          className={`text-[10px] font-mono px-2 py-0.5 rounded font-medium ${
                            isVerified
                              ? "bg-success/20 text-success border border-success/30"
                              : "bg-warning/20 text-warning border border-warning/30"
                          }`}
                        >
                          {tech.classification}
                        </span>
                      </div>

                      {tech.source_url && (
                        <a
                          href={tech.source_url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-[11px] text-primary hover:underline flex items-center gap-1 truncate"
                        >
                          <ExternalLink className="h-3 w-3 shrink-0" />
                          <span className="truncate">{tech.source_url}</span>
                        </a>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* TAB 2: FUNDING (Company) */}
          {companyProfile && activeTab === "funding" && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="bg-surface-200/50 border border-border p-4 rounded-lg">
                  <div className="text-xs font-mono text-muted-foreground">TOTAL FUNDING RAISED</div>
                  <div className="text-xl font-bold font-mono text-foreground mt-1">
                    {companyProfile.total_funding_usd ? formatCurrency(companyProfile.total_funding_usd) : "Undisclosed / Public"}
                  </div>
                </div>
                <div className="bg-surface-200/50 border border-border p-4 rounded-lg">
                  <div className="text-xs font-mono text-muted-foreground">ANNUAL REVENUE BAND</div>
                  <div className="text-xl font-bold font-mono text-foreground mt-1">
                    {companyProfile.annual_revenue_range || "N/A"}
                  </div>
                </div>
              </div>

              {companyProfile.funding_rounds.length > 0 ? (
                <div className="border border-border rounded-lg overflow-hidden">
                  <table className="w-full text-xs text-left">
                    <thead className="bg-surface-200 border-b border-border text-muted-foreground font-mono">
                      <tr>
                        <th className="p-3">ROUND</th>
                        <th className="p-3">AMOUNT</th>
                        <th className="p-3">DATE</th>
                        <th className="p-3">INVESTORS</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border font-mono">
                      {companyProfile.funding_rounds.map((f, i) => (
                        <tr key={i} className="hover:bg-surface-200/50">
                          <td className="p-3 font-semibold text-foreground">{f.round_name}</td>
                          <td className="p-3">{f.amount_usd ? formatCurrency(f.amount_usd) : "N/A"}</td>
                          <td className="p-3 text-muted-foreground">{f.round_date || "N/A"}</td>
                          <td className="p-3 font-sans">{f.investors.join(", ") || "Undisclosed"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-xs text-muted-foreground italic">No public venture funding rounds recorded.</p>
              )}
            </div>
          )}

          {/* TAB 3: LEADERSHIP (Company) */}
          {companyProfile && activeTab === "leadership" && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {companyProfile.leadership.map((exec, i) => (
                  <div key={i} className="bg-surface-200/50 border border-border p-4 rounded-lg flex items-center justify-between">
                    <div>
                      <h4 className="font-semibold text-sm text-foreground">{exec.name}</h4>
                      <p className="text-xs text-primary">{exec.title}</p>
                    </div>
                    {exec.linkedin && (
                      <a
                        href={exec.linkedin}
                        target="_blank"
                        rel="noreferrer"
                        className="btn btn-secondary text-xs px-2.5 py-1.5 flex items-center gap-1"
                      >
                        <ExternalLink className="h-3 w-3" />
                        LinkedIn
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 4: HIRING & JOBS (Company) */}
          {companyProfile && activeTab === "jobs" && (
            <div className="space-y-3">
              {companyProfile.active_jobs.length > 0 ? (
                companyProfile.active_jobs.map((job, idx) => (
                  <div key={idx} className="bg-surface-200/50 border border-border p-4 rounded-lg space-y-2">
                    <div className="flex items-center justify-between">
                      <h4 className="font-semibold text-sm text-foreground">{job.title}</h4>
                      <span className="text-xs text-muted-foreground font-mono">{job.location}</span>
                    </div>
                    <div className="flex flex-wrap items-center gap-1.5">
                      <span className="text-xs text-muted-foreground mr-1">Required:</span>
                      {job.required_technologies.map((t) => (
                        <span key={t} className="text-[10px] px-2 py-0.5 rounded bg-surface-300 font-mono text-foreground">
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-xs text-muted-foreground italic">No active hiring telemetry indexed for this company.</p>
              )}
            </div>
          )}

          {/* TAB: PERSON PROFILE */}
          {personProfile && activeTab === "profile" && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="bg-surface-200/50 border border-border p-4 rounded-lg">
                  <div className="text-xs font-mono text-muted-foreground">CURRENT ROLE & AFFILIATION</div>
                  <div className="text-base font-bold text-foreground mt-1">
                    {personProfile.current_title} @ {personProfile.current_company}
                  </div>
                  {personProfile.verified_work_email && (
                    <div className="text-xs text-primary font-mono mt-1">
                      {personProfile.verified_work_email} (Verified)
                    </div>
                  )}
                </div>
                <div className="bg-surface-200/50 border border-border p-4 rounded-lg">
                  <div className="text-xs font-mono text-muted-foreground">BUYER DECISION-MAKER RATING</div>
                  <div className="text-base font-bold text-foreground mt-1 flex items-center gap-2">
                    <Award className="h-4 w-4 text-warning" />
                    {(personProfile.decision_maker_score * 100).toFixed(0)}% Score
                    {personProfile.is_decision_maker && (
                      <span className="text-xs px-2 py-0.5 rounded bg-success/20 text-success font-mono font-medium">
                        QUALIFIED BUYER
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {personProfile.skills.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-xs font-mono text-muted-foreground uppercase">TECHNICAL SKILLS & DOMAIN EXPERTISE</h4>
                  <div className="flex flex-wrap gap-1.5">
                    {personProfile.skills.map((s) => (
                      <span key={s} className="text-xs px-2.5 py-1 rounded-md bg-surface-200 border border-border text-foreground font-mono">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB: WORK HISTORY (Person) */}
          {personProfile && activeTab === "history" && (
            <div className="space-y-3">
              {personProfile.work_history.map((w, idx) => (
                <div key={idx} className="bg-surface-200/50 border border-border p-4 rounded-lg flex items-start justify-between">
                  <div>
                    <h4 className="font-semibold text-sm text-foreground">{w.title}</h4>
                    <p className="text-xs text-primary">{w.company_name}</p>
                  </div>
                  <span className="text-xs font-mono text-muted-foreground">
                    {w.start_date || "N/A"} — {w.is_current ? "Present" : w.end_date || "N/A"}
                  </span>
                </div>
              ))}
            </div>
          )}

          {/* TAB: PROVENANCE AUDIT (Both) */}
          {activeTab === "evidence" && (
            <div className="space-y-3">
              <div className="border border-border rounded-lg overflow-hidden">
                <table className="w-full text-xs text-left">
                  <thead className="bg-surface-200 border-b border-border text-muted-foreground font-mono">
                    <tr>
                      <th className="p-3">CATEGORY</th>
                      <th className="p-3">CLAIM / OBSERVATION</th>
                      <th className="p-3">CLASSIFICATION</th>
                      <th className="p-3">CONFIDENCE</th>
                      <th className="p-3">SOURCE</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {activeProfile.evidence.map((ev, i) => (
                      <tr key={i} className="hover:bg-surface-200/50">
                        <td className="p-3 font-mono text-muted-foreground">{ev.data_category}</td>
                        <td className="p-3 font-medium text-foreground">{ev.claim}</td>
                        <td className="p-3 font-mono">
                          <span
                            className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${
                              ev.verification_classification === "VERIFIED"
                                ? "bg-success/20 text-success"
                                : "bg-warning/20 text-warning"
                            }`}
                          >
                            {ev.verification_classification}
                          </span>
                        </td>
                        <td className="p-3 font-mono text-muted-foreground">{(ev.confidence * 100).toFixed(0)}%</td>
                        <td className="p-3 truncate max-w-xs">
                          {ev.source_url ? (
                            <a href={ev.source_url} target="_blank" rel="noreferrer" className="text-primary hover:underline flex items-center gap-1">
                              <ExternalLink className="h-3 w-3 shrink-0" />
                              <span className="truncate">{ev.source_url}</span>
                            </a>
                          ) : (
                            <span className="text-muted-foreground">Crustdata REST API</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Confirmation Modal for Level 3 Deep Enrichment */}
      {showConfirmModal && deepCostEstimate && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-surface-100 border border-border p-6 rounded-xl shadow-xl max-w-md w-full space-y-4">
            <div className="flex items-center gap-3 text-warning">
              <Zap className="h-6 w-6" />
              <h3 className="text-lg font-bold text-foreground">Confirm Deep Real-Time Scrape</h3>
            </div>

            <p className="text-sm text-muted-foreground">
              Deep enrichment triggers real-time web crawlers to fetch live headcount trends, executive changes, and latest career signals.
            </p>

            <div className="bg-surface-200 border border-border p-3.5 rounded-lg space-y-2 text-xs font-mono">
              <div className="flex justify-between">
                <span className="text-muted-foreground">TARGET ENTITY:</span>
                <span className="font-semibold text-foreground">{deepCostEstimate.entity_name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">ESTIMATED CREDITS:</span>
                <span className="font-bold text-warning">{deepCostEstimate.estimated_credits.toFixed(1)} Credits</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">AVAILABLE BALANCE:</span>
                <span className="text-foreground">{deepCostEstimate.account_credits_available.toFixed(1)} Credits</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">MINIMUM SAFETY FLOOR:</span>
                <span className="text-foreground">{deepCostEstimate.safety_threshold.toFixed(1)} Credits</span>
              </div>
            </div>

            {deepCostEstimate.warning_message && (
              <p className="text-xs text-destructive font-medium">{deepCostEstimate.warning_message}</p>
            )}

            <div className="flex items-center gap-2 pt-2">
              <button
                onClick={() => setShowConfirmModal(false)}
                className="flex-1 btn btn-secondary text-xs py-2"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmDeepEnrichment}
                disabled={!deepCostEstimate.can_proceed || isEnriching}
                className="flex-1 btn btn-primary text-xs py-2 flex items-center justify-center gap-1.5"
              >
                {isEnriching ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Zap className="h-4 w-4" />}
                Confirm & Execute
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Search History Drawer/Section */}
      {searchHistory.length > 0 && (
        <div className="bg-surface-100 border border-border p-4 rounded-xl space-y-3">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
            <History className="h-4 w-4" />
            Recent Searches
          </h3>
          <div className="flex flex-wrap gap-2">
            {searchHistory.map((h) => (
              <button
                key={h.id}
                onClick={() => quickSearch(h.search_query)}
                className="px-2.5 py-1 bg-surface-200 hover:bg-surface-300 rounded text-xs font-mono text-foreground border border-border flex items-center gap-1.5"
              >
                <span>{h.search_query}</span>
                <span className="text-[10px] text-muted-foreground">({h.entity_type})</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
