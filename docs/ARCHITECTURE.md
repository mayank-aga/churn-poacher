# The Churn Poacher: System Architecture

## 1. Executive Summary

**The Churn Poacher** is an autonomous B2B competitive intelligence and customer takeout platform. It bridges the gap between public vendor dissatisfaction (outages, unexpected price spikes, feature deprecations) and targeted competitive displacement by synthesizing verified financial delta models, zero-code OpenTelemetry migration blueprints, and executive outreach collateral within minutes.

---

## 2. Platform Architecture Diagram

```
                             ┌─────────────────────────────────┐
                             │       CENTRAL ORCHESTRATOR      │
                             │  State Machine & Distributed RQ │
                             └────────────────┬────────────────┘
                                              │
             ┌───────────────────────┬────────┴──────────────┬───────────────────────┐
             │                       │                       │                       │
             ▼                       ▼                       ▼                       ▼
    ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
    │  Listener Agent │────▶│  Profiler Agent │────▶│ FinOps & Arch   │────▶│ Copywriter Agent│
    │  (Reddit, HN,   │     │  (Entity Match, │     │ (Delta Matrix,  │     │ (Executive Brief│
    │   Status RSS)   │     │   Tech Stack)   │     │  OTel Blueprint)│     │  Evidence Guard)│
    └─────────────────┘     └─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                                                     │
                                                                                     ▼
                                                                            ┌─────────────────┐
                                                                            │ Human Approval  │
                                                                            │ Governance Gate │
                                                                            └────────┬────────┘
                                                                                     │
                                                                                     ▼
                                                                            ┌─────────────────┐
                                                                            │ Deposition Pack │
                                                                            │ (Export Unlock) │
                                                                            └─────────────────┘
```

---

## 3. Core Component Subsystems

### A. Central Orchestrator & Persistent Worker
- **State Machine**: Governs workflow lifecycle across 12 distinct states (`PENDING`, `LISTENER_RUNNING`, `PROFILER_RUNNING`, `QUALIFICATION_REVIEW`, `FINOPS_RUNNING`, `ARCHITECT_RUNNING`, `COPYWRITER_RUNNING`, `DRAFT_PENDING_APPROVAL`, `APPROVED`, `REJECTED`, `COMPLETED`, `FAILED`).
- **Distributed Redis Queue**: Asynchronous, persistent task execution via `WorkflowTaskQueue` using Redis lists with distributed locking (`churn_poacher:lock:{target_id}`) preventing concurrent duplicate runs.
- **Heartbeat & Resiliency**: Background worker daemon emits 15-second heartbeats (`churn_poacher:worker:heartbeat`) for automated observability and self-healing.
- **Step-Level Observability**: Complete timing, payload traces, and error history captured per step in `workflow_executions.step_history`.

### B. Listener Agent
- **Adapters**:
  - Live Datadog Status RSS parsing (`status.datadoghq.com`).
  - Live Hacker News Algolia Search API (`hn.algolia.com`).
  - Graceful Reddit API adapter (PRAW credentials or fallback).
  - Explicitly labeled synthetic test generator.
- **Signal Classifier**: Keyword and regex classifier categorizing signals into `PRICING_SHOCK`, `OUTAGE_DOWNTIME`, `MIGRATION_INTENT`, `FEATURE_DEPRECATION`, with sentiment and urgency scoring (0.0 to 1.0).
- **Deduplicator**: Content fingerprinting using SHA-256 preventing redundant ingestions.

### C. Profiler Agent
- **Entity Resolution**: Domain and company name extraction from raw unstructured complaints.
- **Verification Engine**: DNS MX/TXT records and GitHub repository scans for Datadog agents and container orchestration.
- **5-Dimension ICP Scorer**:
  1. Role Authority (VP Eng, CTO, Head of Infra, DevOps Lead)
  2. Company Size (Ideal: 50–1000 employees)
  3. Technology Match (Kubernetes, AWS/GCP, APM, traces)
  4. Distress Acuteness (Surprise bill, active outage)
  5. Challenger Fit (Suitability for SigNoz / Grafana)
- **Qualification Gate**: Automatically drops non-commercial hobbyists and students (`icp_score < 0.70`).

### D. FinOps & Architecture Migration Agent
- **Pricing Catalog**: Live verified public pricing matrix for Datadog, SigNoz Cloud, SigNoz OSS, Grafana Cloud, and Grafana OSS.
- **Scenario Analyzer**: Low, Base, and High volume telemetry modeling with sensitivity analysis identifying top cost levers.
- **OpenTelemetry Blueprint Generator**: Generates drop-in `otel-collector-config.yaml` utilizing port `8126` native Datadog trace receiver for zero-code service cutover.
- **7-Stage Migration Timeline**: 60-day phased migration plan with continuous dual-shipping and instant zero-loss rollback playbooks.

### E. Copywriter Agent & Evidence Guard
- **Personalized Collateral**: Executive email variations (Concise, Technical-Commercial), 3-step LinkedIn sequences, technical pitch, value proposition summaries, and 7-point objection matrices.
- **Evidence Guard**: Anti-hallucination audit engine ensuring 100% of claims are either `VERIFIED` with source citations or flagged. Detects and rejects forbidden marketing buzzwords ("10x faster", "unlimited savings").
- **Human-in-the-Loop Approval Gate**: Generated collateral remains in `DRAFT_PENDING_APPROVAL`. Export is cryptographically blocked (HTTP 403 Forbidden) until approved by a Sales Manager or Administrator.

### F. Multi-Provider LLM Abstraction
- Unified provider interface in `app/core/llm/` supporting:
  - **Google Gemini** (`gemini-1.5-flash`, `gemini-1.5-pro`)
  - **OpenAI** (`gpt-4o-mini`, `gpt-4o`)
  - **Anthropic Claude** (`claude-3-5-sonnet-20241022`, `claude-3-haiku-20240307`)
  - **Deterministic Fallback Engine**: Guaranteed zero-latency, zero-hallucination execution for offline environments and automated test suites.
