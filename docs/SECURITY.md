# The Churn Poacher — Security & Safety Model

This document outlines the security architecture, role-based access control (RBAC), and safety guarantees implemented in **The Churn Poacher**.

---

## 1. Safety Core: Strict Human-in-the-Loop Constraint

The Churn Poacher operates under a non-negotiable architectural safety principle:

> **No autonomous outreach or infrastructure alteration is EVER executed without explicit, authenticated human approval.**

1. **Zero Autonomous Outbound Messaging**: The system never sends cold emails, posts LinkedIn messages, or contacts prospects automatically. The Copywriter Agent only produces draft collateral stored inside a `Dossier`.
2. **Export Gatekeeper**: The `/api/v1/copywriter/{id}/export` endpoint returns HTTP 403 / 400 if the dossier is in `DRAFT_PENDING_APPROVAL` status. Collateral cannot be exported or copied to CRM/sales engagement platforms without an authenticated user with `SALES_MANAGER` or `ADMINISTRATOR` privileges signing off via `/api/v1/copywriter/{id}/approve`.
3. **No Migration Execution**: The Architecture Agent produces technical migration blueprints, OpenTelemetry collector configuration snippets, and step-by-step risk matrices. The system has zero write access to customer cloud providers, clusters, or Datadog accounts.

---

## 2. Authentication & Credential Management

### Password Hashing
- User passwords are encrypted using **PBKDF2-HMAC-SHA256** with 100,000 iterations and a unique 16-byte cryptographic salt per user (`app/core/security.py`).
- No plaintext passwords are ever persisted in logs or database tables.

### JWT Bearer Tokens
- Sessions use JSON Web Tokens (JWT) signed with **HS256** using the `SECRET_KEY` environment variable.
- Tokens encode the user's `sub` (user ID), `email`, `role`, and expiration timestamp (`exp`).
- Default token expiration is 24 hours (`ACCESS_TOKEN_EXPIRE_MINUTES=1440`).

---

## 3. Role-Based Access Control (RBAC) Matrix

Users belong to one of three hierarchical roles:

| Action / Capability | `ANALYST` | `SALES_MANAGER` | `ADMINISTRATOR` |
| :--- | :---: | :---: | :---: |
| View System Dashboard & Signals | Yes | Yes | Yes |
| Trigger Ingestion & Profiling Runs | Yes | Yes | Yes |
| Inspect Company Profiles & FinOps Matrices | Yes | Yes | Yes |
| View Migration Blueprints & Draft Collateral | Yes | Yes | Yes |
| **Approve Migration Dossier (`/approve`)** | **Denied (403)** | **Allowed (200)** | **Allowed (200)** |
| **Reject Dossier (`/reject`)** | **Denied (403)** | **Allowed (200)** | **Allowed (200)** |
| **Export Outbound Sales Collateral (`/export`)** | **Denied (403)** | **Allowed (200)** | **Allowed (200)** |
| Manage User Accounts & System Configuration | Denied (403) | Denied (403) | **Allowed (200)** |

### Dependency Injection Enforcement
Endpoints enforce role permissions cleanly via FastAPI dependencies:
```python
@router.post("/copywriter/{dossier_id}/approve")
async def approve_dossier(
    dossier_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["SALES_MANAGER", "ADMINISTRATOR"]))
):
    ...
```

---

## 4. API & Data Protection

- **Parameterized Database Queries**: All database interactions use SQLAlchemy ORM with asyncpg / aiosqlite, preventing SQL injection vulnerabilities.
- **Strict Pydantic Type Validation**: All inbound JSON payloads are strictly validated against Pydantic models before execution.
- **CORS Protection**: Configured via FastAPI `CORSMiddleware` with explicit origin controls.
- **Secret Isolation**: All credentials (DB passwords, Redis URLs, LLM API keys) are supplied exclusively via environment variables. Default dummy credentials in `.env.example` are blocked in production checks.

---

## 5. Secret Rotation Procedures

In the event of key rotation or compromise:
1. **`SECRET_KEY` Rotation**:
   - Update `SECRET_KEY` in environment / container secrets manager.
   - Restart the backend instances: `docker compose restart backend worker`.
   - Existing active JWT tokens will immediately be invalidated, requiring users to log in again.
2. **Database Password Rotation**:
   - Update password in PostgreSQL: `ALTER USER postgres WITH PASSWORD 'new_password';`.
   - Update `DATABASE_URL` and `POSTGRES_PASSWORD` in `.env` or secrets vault.
   - Restart backend and worker services.
3. **LLM Provider API Keys**:
   - Generate new keys in the respective provider console (OpenAI, Google Cloud, Anthropic).
   - Update `OPENAI_API_KEY`, `GEMINI_API_KEY`, or `ANTHROPIC_API_KEY`.
   - Zero downtime: worker and backend seamlessly pick up new keys upon restart.
