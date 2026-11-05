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
- [ ] **Phase 4: Profiler Agent** (Entity resolution, tech stack verification, ICP scoring, anti-hallucination guardrails)
- [ ] **Phase 5: FinOps & Architect Agent** (Datadog vs. SigNoz/Grafana Delta Matrix, OTel migration blueprints, dual-shipping YAMLs)
- [ ] **Phase 6: Copywriter Agent** (Context-aware outreach drafts, value propositions, human-in-the-loop review)
- [ ] **Phase 7: Central Orchestration** (Agent state machine, retry policies, deduplication, JSON schema validation)
- [ ] **Phase 8: Frontend Dashboard** (Next.js, Tailwind CSS, Recharts, Dossier viewer, real-time monitors)
- [ ] **Phase 9: End-to-End Integration & Testing** (Integration tests, scenario tests, live/demo runs)
- [ ] **Phase 10: Docker Deployment & Documentation** (Docker Compose, production runbooks, user guide)

---

## Phase 3: Listener Agent Architecture

```
[ Datadog Statuspage ] ──┐
[ Hacker News Algolia] ──┼──▶ [ Normalizer ] ──▶ [ Classifier ] ──▶ [ Deduplicator ] ──▶ [ SQLite/PostgreSQL ]
[ Reddit API (OAuth) ] ──┤     (Common Schema)    (Sentiment, Cat,      (SHA-256 Finger-    (`signals` Table)
[ Synthetic Generator] ──┘                         Urgency, Relevance)   print Matching)   + Execution Logs
```

### 1. Ingestion Sources & Required Credentials

| Source | Endpoint / Integration | Required Credentials | Behavior if Missing |
| :--- | :--- | :--- | :--- |
| **Datadog Status** | Statuspage API & Incident History RSS | **None (Public)** | Fetches live active & resolved incidents. Categories as `VENDOR_INCIDENT`. |
| **Hacker News** | Algolia HN Search API | **None (Public)** | Searches for keywords (`datadog pricing`, `datadog bill`, etc.). |
| **Reddit** | Official Reddit OAuth Script App | `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET` | Disables gracefully with `status: "DISABLED_NO_CREDS"`. No rate limit violations. |
| **Synthetic Generator** | In-Memory Realistic Datadog Scenarios | **None** | Generates high-conviction pricing/outage/migration scenarios with `is_synthetic=True`. |

### 2. Distinguishing Real vs. Synthetic Signals
- Every synthetic signal strictly has `is_synthetic = True` and `source = "SYNTHETIC"`.
- Real-world signals have `is_synthetic = False` and preserve original canonical URLs (`status.datadoghq.com/...`, `news.ycombinator.com/...`, `reddit.com/...`).
- API metric endpoints explicitly distinguish `real_signals_count` and `synthetic_signals_count`.

### 3. How to Trigger and Test Ingestion

#### Running Ingestion via REST API:
```bash
# Trigger an ingestion cycle (including synthetic signals)
curl -X POST "http://localhost:8000/api/v1/listener/run" \
     -H "Content-Type: application/json" \
     -d '{"include_synthetic": true, "max_items_per_source": 10}'

# Check adapter availability & execution status
curl "http://localhost:8000/api/v1/listener/status"

# View quantitative metrics & counts
curl "http://localhost:8000/api/v1/listener/metrics"
```

#### Running Tests:
```powershell
cd backend
.\.venv\Scripts\pytest.exe -v
```

---

## Local Development Quickstart

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
pytest
uvicorn app.main:app --reload --port 8000
```
Interactive API Documentation: `http://localhost:8000/docs`
