# The Churn Poacher
### AI-Powered Competitive Intelligence & Customer Acquisition System

**The Churn Poacher** is a multi-agent AI system that detects when customers experience severe pain with their existing enterprise software vendors (outages, unexpected price spikes, deprecations) and converts those signals into actionable, high-conviction migration opportunities.

**First ICP Target**: Datadog $\to$ SigNoz / Grafana

---

## Architecture Overview

```
                                      ┌────────────────────────────────┐
                                      │       CENTRAL ORCHESTRATOR     │
                                      └────────────────┬───────────────┘
                                                       │
         ┌────────────────────────┬────────────────────┼───────────────────┬────────────────────────┐
         │                        │                    │                   │                        │
         ▼                        ▼                    ▼                   ▼                        ▼
┌──────────────────┐    ┌──────────────────┐  ┌─────────────────┐  ┌──────────────────┐   ┌──────────────────┐
│  LISTENER AGENT  │───▶│  PROFILER AGENT  │─▶│ FINOPS & ARCH   │─▶│ COPYWRITER AGENT │──▶│ DEPOSITION PACK  │
│  (Reddit, HN,    │    │  (Entity Match,  │  │ (Delta Matrix,  │  │ (Tailored Exec   │   │ (Actionable      │
│   Status, X)     │    │   Tech Stack)    │  │  Migration Arch)│  │  Outreach Draft) │   │  Dossier)        │
└──────────────────┘    └──────────────────┘  └─────────────────┘  └──────────────────┘   └──────────────────┘
```

---

## 10-Phase Implementation Roadmap

- [x] **Phase 1: Project Structure & Environment Setup** (Modular layout, Pydantic settings, health check API, test harness)
- [x] **Phase 2: Database & Backend Foundation** (SQLAlchemy models, Async DB sessions, CRUD repositories, REST API v1)
- [x] **Phase 3: Listener Agent** (Datadog Status & HN Live Adapters, Reddit OAuth Graceful Fallback, Synthetic Generator, Normalization, Classification, Deduplication)
- [x] **Phase 4: Profiler Agent** (Entity resolution, DNS verification, GitHub/Job technology profiling, explainable 5-dimension ICP scoring, strict anti-hallucination evidence validation)
- [x] **Phase 5: FinOps & Architect Agent** (Datadog vs. SigNoz/Grafana Delta Matrix, 5 platforms, Low/Base/High scenarios, sensitivity ranking, OpenTelemetry dual-shipping YAML generator, 7-phase migration plan, rollback strategy, DepositionDossier persistence)
- [x] **Phase 6: Copywriter Agent** (Context-aware outreach drafts, executive emails, LinkedIn sequences, technical pitch, value prop, objection matrix, evidence guard, human-in-the-loop review)
- [ ] **Phase 7: Central Orchestration** (Agent state machine, retry policies, deduplication, JSON schema validation)
- [ ] **Phase 8: Frontend Dashboard** (Next.js, Tailwind CSS, Recharts, Dossier viewer, real-time monitors)
- [ ] **Phase 9: End-to-End Integration & Testing** (Integration tests, scenario tests, live/demo runs)
- [ ] **Phase 10: Docker Deployment & Documentation** (Docker Compose, production runbooks, user guide)

---

## Phase 5: FinOps & Architect Agent

### 1. Part A: FinOps Intelligence Engine
- **Supported Platforms**:
  1. Datadog (Enterprise Hosts, APM, Custom Metrics, Log Ingestion & Retention)
  2. SigNoz Cloud (Zero per-node tax, pure usage-based ingestion)
  3. SigNoz Self-Hosted (Free OSS Community Edition + AWS compute/storage)
  4. Grafana Cloud (Active series metrics, logs, traces)
  5. Grafana OSS (Mimir, Loki, Tempo self-hosted stack)
- **Granular Scenarios**:
  - `LOW`: Conservative telemetry scale (-35%)
  - `BASE`: Standard derived baseline based on company size and infrastructure footprint
  - `HIGH`: Heavy custom metrics expansion (+50%)
- **Calculations**:
  - Itemized monthly & annual platform expenditures
  - Annual savings and savings percentage
  - Estimated migration cost & payback period in months
  - 3-Year Total Cost of Ownership (TCO) across all target platforms
  - Sensitivity analysis identifying highest-variance telemetry levers

### 2. Part B: Architecture Migration Engine
- **Current Architecture Assessment**: Audits application services, Kubernetes environments, and ingestion methods, labeling components as `VERIFIED`, `INFERRED`, or `UNKNOWN`.
- **OpenTelemetry Dual-Shipping Configuration**: Produces validated, production-grade `otel-collector-config.yaml` with native Datadog trace receiver (`:8126`) and dual-shipping pipeline multiplexing.
- **7-Phase Takeout Roadmap**:
  - Phase 1: Telemetry Discovery & Footprint Audit (Days 1–3)
  - Phase 2: Parallel OpenTelemetry Collector Deployment (Days 4–7)
  - Phase 3: Dual-Shipping & Data Parity Validation (Days 8–14)
  - Phase 4: Performance & Dashboard Cost Verification (Days 15–21)
  - Phase 5: Gradual Traffic Cutover / Canary Waves (Days 22–30)
  - Phase 6: Datadog Dependency Reduction (Days 31–45)
  - Phase 7: Final Decommissioning & Contract Termination (Days 46–60)
- **Rollback Playbook**: Zero-loss rollback strategy with parallel pipeline isolation.

---

## REST API FinOps & Architecture Endpoints

```bash
# Generate financial analysis for an identified company
curl -X POST "http://localhost:8000/api/v1/finops/run/{company_id}"

# Generate OpenTelemetry migration blueprint and collector YAML
curl -X POST "http://localhost:8000/api/v1/architecture/run/{company_id}?target_backend=SigNoz Cloud"

# Generate and persist complete Deposition Dossier in SQLite
curl -X POST "http://localhost:8000/api/v1/finops/dossier/{company_id}"

# Retrieve stored financial report or migration blueprint
curl "http://localhost:8000/api/v1/finops/{company_id}"
curl "http://localhost:8000/api/v1/architecture/{company_id}"

# Inspect published pricing catalog with verification dates & source URLs
curl "http://localhost:8000/api/v1/finops/pricing"

# Retrieve aggregate financial metrics across all dossiers
curl "http://localhost:8000/api/v1/finops/metrics"
```

---

## Phase 6: Copywriter Agent

The Copywriter Agent translates the intelligence generated by the Listener, Profiler, and FinOps/Architect agents into personalized, evidence-grounded B2B sales collateral without generic cold spam or creepy tracking tropes.

### 1. Key Modules & Collateral Outputs
- **Executive Email Generator** (`executive_email.py`):
  - *Variant 1 (Executive Concise)*: Targeted at CTOs & VPs of Engineering. High impact, 3 subject lines with distinct hooks, preheader, projected savings ($ and %), and low-friction 15-minute architecture review CTA.
  - *Variant 2 (Technical-Commercial)*: Targeted at Heads of Infrastructure & FinOps Leads. Granular cost breakdown (APM host tax vs. ingestion-only), OpenTelemetry port `:8126` Datadog compatibility receiver, and dual-shipping POC proposal.
- **LinkedIn Multi-Touch Writer** (`linkedin_writer.py`):
  - *Touch 1*: Connection request strictly under 300 characters, engineering peer tone.
  - *Touch 2*: Post-connection value-add sharing architectural benchmarks and OTel patterns.
  - *Touch 3*: Technical-commercial follow-up sharing financial delta and parallel testing blueprint.
- **Technical Migration Pitch** (`technical_pitch.py`):
  - In-depth architectural brief: Datadog proprietary agent vs. CNCF OpenTelemetry Collector.
  - Zero-code migration via port `:8126` native Datadog trace receiver (no application code refactor).
  - Dual-shipping validation and PromQL alert/dashboard parity mapping.
- **Value Proposition Brief** (`value_proposition.py`):
  - 1-page financial business case comparing Datadog baseline to target challenger (BASE scenario).
  - The "Datadog Tax" decomposition: Host tax, custom metrics multiplication, and log retention fees.
  - TCO calculation: Net 1st-year ROI after migration costs, payback period in months, and 3-year cumulative savings.
- **Enterprise Objection Handler** (`objection_handler.py`):
  - Pre-arms teams with talking points and technical proofs for 7 standard enterprise objections: Engineering Bandwidth, Downtime Risk, Contract Lock-in, Historical Data Loss, Self-Hosted Maintenance, "Datadog Works Fine", and Rollback Safety.
- **Evidence Guard & Anti-Hallucination Layer** (`evidence_guard.py`):
  - Enforces strict estimation labeling ("estimated", "projected", "modeled") when numbers derive from inferred profiles.
  - Scans for and flags forbidden marketing buzzwords (`game-changing`, `revolutionary`, `rockstar`, `10x engineer`, etc.).
  - Blocks fabricated email addresses or invented personal identities.
  - Generates an `EvidenceAuditReport` with a quantitative `hallucination_risk_score`.

### 2. Human-in-the-Loop Governance & Gated Export
All generated outreach collateral is persisted into `DepositionDossier.outreach_drafts` in a default status of `DRAFT_PENDING_APPROVAL`.
- **Strict Export Gate**: The `/copywriter/{dossier_id}/export` endpoint **strictly prohibits export** (returning HTTP 403 Forbidden) unless the dossier has been explicitly reviewed and approved via `/copywriter/{dossier_id}/approve`.
- Never automatically sends unsolicited emails or messages.

```bash
# Generate outreach package and attach to dossier
curl -X POST "http://localhost:8000/api/v1/copywriter/run/{company_id}?target_challenger=SigNoz Cloud"

# Retrieve generated drafts
curl "http://localhost:8000/api/v1/copywriter/{company_id}"

# Attempt export BEFORE approval (returns 403 Forbidden)
curl -X POST "http://localhost:8000/api/v1/copywriter/{dossier_id}/export"

# Approve draft
curl -X PATCH "http://localhost:8000/api/v1/copywriter/{dossier_id}/approve"

# Export approved package as markdown/JSON bundle (succeeds with 200 OK)
curl -X POST "http://localhost:8000/api/v1/copywriter/{dossier_id}/export"

# Reject draft with feedback reason
curl -X PATCH "http://localhost:8000/api/v1/copywriter/{dossier_id}/reject" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Revise tone for enterprise compliance team"}'

# View copywriting & governance metrics
curl "http://localhost:8000/api/v1/copywriter/metrics"
```

---

## Automated Test Execution

```powershell
cd backend
.\.venv\Scripts\pytest.exe -v
```
All **61 automated tests** passing 100% green across all components and agents.
