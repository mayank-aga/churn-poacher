# The Churn Poacher — Environment Variables Reference

This document provides a comprehensive dictionary of all configuration parameters for **The Churn Poacher** backend, background workers, and frontend.

Configuration is handled by Pydantic's `BaseSettings` (`app/core/config.py`) and Next.js public environment variables. Variables can be supplied via a `.env` file or directly through the container / deployment environment.

---

## 1. Core Server & Security

| Variable | Type | Default | Production Requirement | Description |
| :--- | :--- | :--- | :--- | :--- |
| `ENVIRONMENT` | `string` | `development` | `production` | Operational environment mode (`development`, `staging`, `production`, `test`). |
| `DEBUG` | `boolean` | `false` | `false` | Enables verbose debug logging and traceback exposure. Must be `false` in production. |
| `SECRET_KEY` | `string` | `churn-poacher-super-secret-key-change-in-production` | **Required** (Random 64+ char) | Cryptographic key used for HS256 JWT signature generation and token verification. |
| `ENABLE_AUTH` | `boolean` | `true` | `true` | Enforces JWT authentication and RBAC permissions on protected endpoints (`/approve`, `/export`). |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `integer` | `1440` (24h) | Optional | Duration in minutes before issued JWT tokens expire. |

---

## 2. Database (PostgreSQL / SQLite)

| Variable | Type | Default | Production Requirement | Description |
| :--- | :--- | :--- | :--- | :--- |
| `DATABASE_URL` | `string` | `sqlite+aiosqlite:///./churn_poacher.db` | **Required** | Async database connection string. In production, set to `postgresql+asyncpg://<user>:<password>@<host>:<port>/<dbname>`. |
| `DB_POOL_SIZE` | `integer` | `10` | `10`–`50` | Size of the persistent connection pool maintained by SQLAlchemy / asyncpg. |
| `DB_MAX_OVERFLOW` | `integer` | `20` | `10`–`30` | Maximum additional temporary connections permitted during peak traffic spikes. |
| `POSTGRES_DB` | `string` | `churn_poacher` | Required for Docker | Database name created in the official PostgreSQL container. |
| `POSTGRES_USER` | `string` | `postgres` | Required for Docker | Database master user. |
| `POSTGRES_PASSWORD` | `string` | `postgres` | **Required** (Strong pass) | Database password for the master user. |
| `POSTGRES_PORT` | `integer` | `5432` | `5432` | Host/container port for PostgreSQL. |

---

## 3. Redis & Worker Queue

| Variable | Type | Default | Production Requirement | Description |
| :--- | :--- | :--- | :--- | :--- |
| `REDIS_URL` | `string` | `redis://localhost:6379/0` | **Required** | Redis connection URI for the task queue (`churn_poacher:workflow_queue`) and distributed locks. |
| `REDIS_PORT` | `integer` | `6379` | `6379` | Port for Redis service in Docker Compose. |
| `WORKER_CONCURRENCY` | `integer` | `4` | `2`–`8` | Number of concurrent pipeline tasks processed per worker node. |

---

## 4. Multi-Provider LLM Configuration

The system implements a resilient multi-provider LLM abstraction (`app/core/llm/`). If no API keys are provided or all providers fail, the system falls back seamlessly to the deterministic rule-based engine.

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `LLM_PROVIDER` | `string` | `auto` | Preferred provider: `auto`, `openai`, `gemini`, `anthropic`, or `fallback`. When `auto`, selects first available provider with configured keys. |
| `OPENAI_API_KEY` | `string` | `""` | API key for OpenAI (`gpt-4o-mini`, `gpt-4o`). |
| `OPENAI_MODEL` | `string` | `gpt-4o-mini` | Model identifier for OpenAI calls. |
| `GEMINI_API_KEY` | `string` | `""` | API key for Google Gemini (`gemini-1.5-flash`, `gemini-1.5-pro`). |
| `GEMINI_MODEL` | `string` | `gemini-1.5-flash` | Model identifier for Google Gemini calls. |
| `ANTHROPIC_API_KEY` | `string` | `""` | API key for Anthropic Claude (`claude-3-5-sonnet-20241022`). |
| `ANTHROPIC_MODEL` | `string` | `claude-3-5-sonnet-20241022` | Model identifier for Anthropic Claude calls. |

---

## 5. Intelligence Sources & Social Connectors

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `HACKER_NEWS_API_BASE` | `string` | `https://hn.algolia.com/api/v1` | Base URL for Algolia Hacker News search API. |
| `DATADOG_STATUS_PAGE_URL`| `string` | `https://status.datadoghq.com/api/v2/summary.json` | Datadog Statuspage.io API summary endpoint. |
| `REDDIT_CLIENT_ID` | `string` | `""` | Reddit OAuth2 Client ID for monitoring r/devops, r/sysadmin, etc. |
| `REDDIT_CLIENT_SECRET` | `string` | `""` | Reddit OAuth2 Client Secret. |
| `REDDIT_USER_AGENT` | `string` | `ChurnPoacherBot/1.0.0` | Reddit User-Agent identification string. |
| `TWITTER_BEARER_TOKEN` | `string` | `""` | X / Twitter API v2 Bearer Token for public dissatisfaction monitoring. |

---

## 6. Enrichment & Firmographics APIs

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `CLEARBIT_API_KEY` | `string` | `""` | API key for Clearbit Company Enrichment (domain, employee count, tech stack). |
| `APOLLO_API_KEY` | `string` | `""` | API key for Apollo.io B2B decision-maker and company verification. |
| `GITHUB_TOKEN` | `string` | `""` | GitHub Personal Access Token for public repo tech stack profiling. |

---

## 7. Frontend Client Configuration

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `NEXT_PUBLIC_API_URL` | `string` | `http://localhost:8000` | Backend API URL reachable by the client browser / Next.js SSR server. |
| `PORT` | `integer` | `3000` | HTTP port on which Next.js listens. |
