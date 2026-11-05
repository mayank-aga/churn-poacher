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
- [ ] **Phase 6: Copywriter Agent** (Context-aware outreach drafts, value propositions, human-in-the-loop review)
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

## Automated Test Execution

```powershell
cd backend
.\.venv\Scripts\pytest.exe -v
```
All **51 automated tests** passing 100% green across all components.
