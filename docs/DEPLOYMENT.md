# The Churn Poacher: Deployment Guide

This guide details how to build, configure, and deploy The Churn Poacher using Docker, Docker Compose, and production infrastructure.

---

## 1. Prerequisites

- **Docker Engine**: Version 24.0.0 or higher
- **Docker Compose**: Version 2.20.0 or higher
- **System Memory**: Minimum 4 GB RAM recommended
- **Ports Required**:
  - `3000`: Next.js Frontend Dashboard
  - `8000`: FastAPI Backend REST API
  - `5432`: PostgreSQL Database (optional if using external managed RDS/Cloud SQL)
  - `6379`: Redis (optional if using external ElastiCache/MemoryStore)

---

## 2. Quickstart with Docker Compose

### Step 1: Clone and Configure Environment

```bash
git clone https://github.com/your-org/churn-poacher.git
cd churn-poacher

# Copy environment template
cp .env.example .env

# Generate a strong SECRET_KEY
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
```

Configure your LLM credentials in `.env` (at least one provider recommended):
```env
GEMINI_API_KEY=your-gemini-api-key
# OR
OPENAI_API_KEY=your-openai-api-key
# OR
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### Step 2: Build and Launch Services

```bash
docker compose up -d --build
```

### Step 3: Verify Container Health

```bash
docker compose ps
```

Expected healthy output:
```
NAME                      IMAGE                   STATUS                  PORTS
churn_poacher_postgres    postgres:16-alpine      Up (healthy)            0.0.0.0:5432->5432/tcp
churn_poacher_redis       redis:7-alpine          Up (healthy)            0.0.0.0:6379->6379/tcp
churn_poacher_backend     churn-poacher-backend   Up (healthy)            0.0.0.0:8000->8000/tcp
churn_poacher_worker      churn-poacher-worker    Up                      
churn_poacher_frontend    churn-poacher-frontend  Up                      0.0.0.0:3000->3000/tcp
```

### Step 4: Run Initial Database Migrations & Bootstrap Seed

```bash
# Execute Alembic migrations inside the backend container
docker compose exec backend alembic upgrade head

# Seed default administrator and sales manager accounts
docker compose exec backend curl -X POST "http://localhost:8000/api/v1/auth/seed-defaults"
```

Default credentials created:
- **Administrator**: `admin@churnpoacher.local` (Password: `AdminPass123!`)
- **Sales Manager**: `sales@churnpoacher.local` (Password: `SalesPass123!`)
- **Analyst**: `analyst@churnpoacher.local` (Password: `AnalystPass123!`)

*IMPORTANT: Change these passwords immediately in production.*

---

## 3. Production Hardening Checklist

1. **Change Default Passwords**:
   - Update `POSTGRES_PASSWORD` and `SECRET_KEY` in `.env`.
   - Never use default credentials in public networks.
2. **Enable Authentication**:
   - Set `ENABLE_AUTH=true` in `.env` to enforce Bearer token verification across API endpoints.
3. **CORS Restrictions**:
   - Restrict `CORS_ORIGINS` to your production frontend domain (e.g. `https://app.churnpoacher.com`).
4. **TLS / Reverse Proxy**:
   - Terminate SSL using Nginx, Cloudflare, AWS ALB, or Traefik with HTTP Strict Transport Security (HSTS).
5. **Database Storage**:
   - Ensure the Docker volume `postgres_data` is mounted to redundant EBS/persistent block storage with automated snapshots.

---

## 4. Local Development Without Docker

If developing locally without containers:

```powershell
# 1. Backend Setup
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start API server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Start background worker (in separate terminal)
python -m app.worker.main

# 2. Frontend Setup
cd ..\frontend
npm install
npm run dev
```

Visit the dashboard at `http://localhost:3000`.
