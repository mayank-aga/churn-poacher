# The Churn Poacher — Troubleshooting & Operations Guide

This guide provides diagnostic procedures and recovery workflows for common operational anomalies in **The Churn Poacher**.

---

## 1. Quick Diagnostics Cheat Sheet

| Symptom | Primary Cause | Immediate Remediation |
| :--- | :--- | :--- |
| `POST /api/v1/orchestrator/run` returns 409 Conflict | Distributed lock held on target | Check if existing run is active or release Redis key `churn_poacher:lock:<target>` |
| `/api/v1/health/deep` returns 503 "unhealthy" | Database or Redis unreachable | Inspect container logs: `docker compose logs postgres redis` |
| Worker not processing queued jobs | Worker crashed or disconnected | Check worker heartbeat with `docker compose logs -f worker` |
| Export endpoint returns 403 Forbidden | User role is `ANALYST` or dossier is pending | Log in as `SALES_MANAGER` or approve dossier first |
| LLM calls failing or timing out | Upstream API outage or invalid key | Check logs for fallback: system automatically degrades to deterministic engine |

---

## 2. Deep Health Probe Inspection

The backend includes a comprehensive health diagnostic endpoint:

```bash
curl -i http://localhost:8000/api/v1/health/deep
```

### Expected Healthy Response (HTTP 200)
```json
{
  "status": "healthy",
  "database": {
    "status": "connected",
    "latency_ms": 1.42
  },
  "redis": {
    "status": "connected",
    "latency_ms": 0.85,
    "queue_length": 0
  },
  "worker": {
    "status": "active",
    "last_heartbeat_ago_seconds": 3.2
  },
  "llm_provider": {
    "configured": "auto",
    "active": "deterministic-fallback"
  }
}
```

If any critical service is degraded, the response code is HTTP 503, highlighting exactly which component failed and why.

---

## 3. Specific Issue Runbooks

### A. Database Connection Pool Exhaustion
**Error**: `TimeoutError: QueuePool limit of size 10 overflow 20 reached`

**Cause**: High volume of long-running queries or unclosed database sessions.

**Resolution**:
1. Check active database connections:
   ```sql
   SELECT count(*), state FROM pg_stat_activity GROUP BY state;
   ```
2. Increase pool limits in `.env`:
   ```bash
   DB_POOL_SIZE=25
   DB_MAX_OVERFLOW=50
   ```
3. Restart backend service:
   ```bash
   docker compose restart backend
   ```

---

### B. Redis Queue Stalls & Distributed Lock Contention
**Error**: `Target is currently locked by another active workflow`

**Cause**: A previous worker run crashed unexpectedly while holding a distributed lock before reaching its 5-minute TTL.

**Resolution**:
1. Inspect active Redis keys:
   ```bash
   docker compose exec redis redis-cli keys "churn_poacher:*"
   ```
2. Check lock keys:
   ```bash
   docker compose exec redis redis-cli get "churn_poacher:lock:all"
   ```
3. Delete stale lock if worker is no longer running:
   ```bash
   docker compose exec redis redis-cli del "churn_poacher:lock:all"
   ```

---

### C. Worker Heartbeat Stale or Offline
**Symptom**: `deep_health` reports worker status as `offline` or `stale`.

**Cause**: The background daemon process stopped or encountered an uncaught OS exception.

**Resolution**:
1. Inspect worker container logs:
   ```bash
   docker compose logs --tail=100 -f worker
   ```
2. Restart the worker:
   ```bash
   docker compose restart worker
   ```
3. Confirm fresh heartbeat registered in Redis:
   ```bash
   docker compose exec redis redis-cli get "churn_poacher:worker:heartbeat"
   ```

---

### D. LLM Rate Limits & Fallback
**Symptom**: `openai.RateLimitError` or `gemini.ResourceExhausted`.

**Behavior**:
The built-in multi-provider LLM manager (`app/core/llm/manager.py`) catches timeouts, rate limits, and authentication errors automatically. When an external LLM fails:
1. It attempts the next configured LLM provider in sequence.
2. If all cloud providers fail, it logs a warning and routes the request to `DeterministicFallbackProvider`.
3. The pipeline **continues without disruption**, producing accurate, rule-based financial calculations and migration blueprints.

To force a specific provider, set `LLM_PROVIDER=gemini` or `LLM_PROVIDER=openai` in `.env`.

---

## 4. Container Logs & Real-Time Monitoring

Inspect consolidated logs across all containers:
```bash
docker compose logs -f --tail=50
```

Inspect individual service logs:
```bash
docker compose logs -f backend
docker compose logs -f worker
docker compose logs -f frontend
docker compose logs -f postgres
```
