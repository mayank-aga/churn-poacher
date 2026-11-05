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
- [ ] **Phase 2: Database & Backend Foundation** (SQLAlchemy models, Alembic migrations, CRUD repositories)
- [ ] **Phase 3: Listener Agent** (Reddit API, HN Algolia, Datadog Status Page, Sentiment/Urgency classification)
- [ ] **Phase 4: Profiler Agent** (Entity resolution, tech stack verification, ICP scoring, anti-hallucination guardrails)
- [ ] **Phase 5: FinOps & Architect Agent** (Datadog vs. SigNoz/Grafana Delta Matrix, OTel migration blueprints, dual-shipping YAMLs)
- [ ] **Phase 6: Copywriter Agent** (Context-aware outreach drafts, value propositions, human-in-the-loop review)
- [ ] **Phase 7: Central Orchestration** (Agent state machine, retry policies, deduplication, JSON schema validation)
- [ ] **Phase 8: Frontend Dashboard** (Next.js, Tailwind CSS, Recharts, Dossier viewer, real-time monitors)
- [ ] **Phase 9: End-to-End Integration & Testing** (Integration tests, scenario tests, live/demo runs)
- [ ] **Phase 10: Docker Deployment & Documentation** (Docker Compose, production runbooks, user guide)

---

## Getting Started

### Backend Setup
```bash
cd backend
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
pytest
uvicorn app.main:app --reload --port 8000
```
API Documentation will be accessible at: `http://localhost:8000/docs`
