# The Churn Poacher — Database Backup & Disaster Recovery Guide

This guide details backup, restore, and disaster recovery procedures for **The Churn Poacher** database layer.

---

## 1. Production PostgreSQL Backups

### Automated Daily Logical Dump (`pg_dump`)

To take an atomic, compressed snapshot of the production database:

```bash
# Set timestamp and backup file path
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="/backups/churn_poacher_${BACKUP_DATE}.dump"

# Run pg_dump inside the docker container
docker compose exec -t postgres pg_dump \
  -U postgres \
  -d churn_poacher \
  -F c \
  -b \
  -v \
  -f "${BACKUP_FILE}"
```

### Scripted Automated Backup (Cron)
Add a crontab entry on the host machine to execute nightly at 02:00 UTC and retain 14 days of backups:

```bash
0 2 * * * docker compose -f /path/to/churn-poacher/docker-compose.yml exec -T postgres pg_dump -U postgres -d churn_poacher -F c -b -f /backups/churn_poacher_$(date +\%F).dump && find /backups -type f -name "churn_poacher_*.dump" -mtime +14 -delete
```

---

## 2. PostgreSQL Restore Procedures

### Restoring from Compressed Dump (`.dump`)

1. **Stop ingestion and worker traffic**:
   ```bash
   docker compose stop backend worker
   ```

2. **Drop existing connections and restore database**:
   ```bash
   # Terminate active sessions
   docker compose exec -T postgres psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'churn_poacher' AND pid <> pg_backend_pid();"

   # Drop and recreate clean target database
   docker compose exec -T postgres psql -U postgres -c "DROP DATABASE churn_poacher;"
   docker compose exec -T postgres psql -U postgres -c "CREATE DATABASE churn_poacher;"

   # Restore schema and data using pg_restore
   docker compose exec -T postgres pg_restore \
     -U postgres \
     -d churn_poacher \
     -v \
     /backups/churn_poacher_2026-11-06.dump
   ```

3. **Run database migrations to ensure schema freshness**:
   ```bash
   docker compose run --rm backend alembic upgrade head
   ```

4. **Restart backend and background worker**:
   ```bash
   docker compose start backend worker
   ```

5. **Verify system health**:
   ```bash
   curl -s http://localhost:8000/api/v1/health/deep | jq .
   ```

---

## 3. Development / Local SQLite Backup

For local testing or development environments using SQLite:

```bash
# SQLite atomic backup using the online backup command
sqlite3 churn_poacher.db ".backup 'churn_poacher_backup_$(date +%Y%m%d).db'"
```

To restore SQLite:
```bash
cp churn_poacher_backup_20261106.db churn_poacher.db
```

---

## 4. Disaster Recovery & Verification Checklist

Perform a test restore monthly in a staging environment:

- [ ] Verify that backup file size is greater than 0 bytes and matches expected growth trends.
- [ ] Restore dump file into an isolated test PostgreSQL container.
- [ ] Verify row counts in key tables:
  ```sql
  SELECT count(*) FROM signals;
  SELECT count(*) FROM companies;
  SELECT count(*) FROM deposition_dossiers;
  SELECT count(*) FROM users;
  ```
- [ ] Confirm Alembic migration version matches current code:
  ```bash
  alembic current
  ```
- [ ] Run health check: verify deep probe returns `"status": "healthy"`.
