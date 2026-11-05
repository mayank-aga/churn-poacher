"""
Tests for Background Worker Task Queue and Health Probes.
Verifies distributed locks, task enqueueing, and observability probes.
"""

import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.worker.queue import WorkflowTaskQueue
from app.worker.worker import BackgroundWorker


@pytest.mark.asyncio
async def test_workflow_task_queue_distributed_locking():
    # Test distributed lock acquisition and release
    target_id = "test-company-lock-id"

    # In local testing without active Redis, acquire_lock returns True
    locked = await WorkflowTaskQueue.acquire_lock(target_id, ttl_seconds=60)
    assert locked is True

    await WorkflowTaskQueue.release_lock(target_id)


@pytest.mark.asyncio
async def test_worker_graceful_shutdown():
    worker = BackgroundWorker()
    worker.stop()
    assert worker._running is False


@pytest.mark.asyncio
async def test_deep_health_probe_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/v1/health/deep")
        assert res.status_code == 200
        data = res.json()
        assert "status" in data
        assert "checks" in data
        assert "database" in data["checks"]
        assert data["checks"]["database"]["status"] == "healthy"
        assert "llm_providers" in data["checks"]
