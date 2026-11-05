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
- [ ] **Phase 5: FinOps & Architect Agent** (Datadog vs. SigNoz/Grafana Delta Matrix, OTel migration blueprints, dual-shipping YAMLs)
- [ ] **Phase 6: Copywriter Agent** (Context-aware outreach drafts, value propositions, human-in-the-loop review)
- [ ] **Phase 7: Central Orchestration** (Agent state machine, retry policies, deduplication, JSON schema validation)
- [ ] **Phase 8: Frontend Dashboard** (Next.js, Tailwind CSS, Recharts, Dossier viewer, real-time monitors)
- [ ] **Phase 9: End-to-End Integration & Testing** (Integration tests, scenario tests, live/demo runs)
- [ ] **Phase 10: Docker Deployment & Documentation** (Docker Compose, production runbooks, user guide)

---

## Phase 4: Profiler Agent Architecture

```
[ Listener Signal (status='NEW') ]
               │
               ▼
   [ Entity Resolver ] ──────────────▶ Anonymous / Unverified? ──▶ [ Signal.status = 'UNRESOLVED' ]
   (Explicit Company / Domain)                                      (No Fabrication, Preserved)
               │ (Candidate Identified)
               ▼
   [ Domain Verifier ] ──────────────▶ Public DNS Checks (A, CNAME, MX)
               │
               ▼
 [ Technology Profiler ] ────────────▶ Public GitHub Repos + Job Postings Telemetry
               │
               ▼
   [ Evidence Validator ] ───────────▶ Strict Classification: VERIFIED vs INFERRED vs UNKNOWN
               │
               ▼
     [ Explainable ICP Scorer ] ─────▶ 5 Dimensions (Size: 20%, Infra: 20%, Tech: 25%, DD: 20%, Distress: 15%)
                                       Separate Scores: ICP Fit, Identity Conf, Technology Conf
               │
               ▼
    [ Qualification State ] ─────────▶ ACCEPTED / REVIEW_REQUIRED / REJECTED
                                       (High ICP Fit NEVER overrides weak identity evidence!)
```

### 1. Explainable ICP Scoring Model

The Profiler Agent evaluates 5 distinct weighted dimensions (0.0 to 1.0):

1. **Company Size Suitability (20%)**: Optimal sweet spot is 50–1000 employees with high telemetry spend and agility to migrate.
2. **Infrastructure Maturity (20%)**: Cloud-native footprint (Kubernetes, AWS/GCP, multi-node clusters).
3. **Technology Footprint (25%)**: OpenTelemetry, APM, microservices, distributed tracing readiness.
4. **Datadog Usage Evidence (20%)**: Concrete verified or inferred evidence of active Datadog production telemetry.
5. **Migration Intent or Pain Urgency (15%)**: Signal distress rating and urgency level from price shocks or outages.

### 2. Separate Confidence Dimensions
- **ICP Fit Score**: Attractiveness as a potential takeout customer.
- **Identity Confidence**: Confidence that the author/signal belongs to the identified corporate entity.
- **Technology Confidence**: Confidence that the company runs Datadog in production.

### 3. Qualification Gates
- **`ACCEPTED`**: `identity_confidence >= 0.70` AND `icp_fit_score >= 0.65` AND `technology_confidence >= 0.60`.
- **`REVIEW_REQUIRED`**: Promising infrastructure or pain, but requires human identity verification before outreach.
- **`REJECTED`**: Micro-hobbyists, students, or non-commercial projects.

---

## REST API Profiler Endpoints

```bash
# Trigger batch profiling over new listener signals
curl -X POST "http://localhost:8000/api/v1/profiler/run" \
     -H "Content-Type: application/json" \
     -d '{"max_signals": 10}'

# Check profiler operational status and queue counts
curl "http://localhost:8000/api/v1/profiler/status"

# List enriched companies (filter by qualification status or minimum ICP score)
curl "http://localhost:8000/api/v1/profiler/companies?status=ACCEPTED&min_icp_score=0.70"

# Fetch complete company intelligence dossier by ID
curl "http://localhost:8000/api/v1/profiler/companies/{company_id}"

# Retrieve aggregated qualification metrics
curl "http://localhost:8000/api/v1/profiler/metrics"
```

---

## Local Test Execution

```powershell
cd backend
.\.venv\Scripts\pytest.exe -v
```
All **38 automated tests** passing across unit, source, listener, and profiler test suites.
