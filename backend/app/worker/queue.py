"""
Redis-Backed Workflow Task Queue.
Provides distributed task enqueueing, distributed locking, and task status tracking.
"""

import json
import time
from typing import Optional, Dict, Any
import redis.asyncio as aioredis

from app.core.config import settings
from app.core.logging import logger

WORKFLOW_QUEUE_KEY = "churn_poacher:workflow_queue"
TASK_PREFIX = "churn_poacher:task:"
LOCK_PREFIX = "churn_poacher:lock:"


class WorkflowTaskQueue:
    """Manages enqueueing and distributed locking of pipeline tasks via Redis."""

    @classmethod
    async def get_redis_client(cls) -> Optional[aioredis.Redis]:
        """Returns connected Redis client or None if unreachable."""
        try:
            client = aioredis.from_url(settings.REDIS_URL, socket_timeout=2.0)
            await client.ping()
            return client
        except Exception as e:
            logger.debug(f"Redis not reachable at {settings.REDIS_URL}: {e}")
            return None

    @classmethod
    async def acquire_lock(cls, target_id: str, ttl_seconds: int = 300) -> bool:
        """Acquires a distributed lock to prevent duplicate concurrent execution on the same target."""
        r = await cls.get_redis_client()
        if not r:
            return True  # Redis not active, allow execution (fallback mode)

        lock_key = f"{LOCK_PREFIX}{target_id}"
        acquired = await r.set(lock_key, "locked", ex=ttl_seconds, nx=True)
        await r.aclose()
        return bool(acquired)

    @classmethod
    async def release_lock(cls, target_id: str) -> None:
        """Releases the distributed lock for a target ID."""
        r = await cls.get_redis_client()
        if not r:
            return

        lock_key = f"{LOCK_PREFIX}{target_id}"
        await r.delete(lock_key)
        await r.aclose()

    @classmethod
    async def enqueue(
        cls,
        workflow_id: str,
        timeout_seconds: int = 60,
        retry_count: int = 0,
    ) -> bool:
        """Enqueues a workflow ID onto the persistent Redis task queue."""
        r = await cls.get_redis_client()
        if not r:
            logger.warning("Redis unavailable; cannot enqueue to background worker queue.")
            return False

        task_payload = {
            "workflow_id": workflow_id,
            "timeout_seconds": timeout_seconds,
            "retry_count": retry_count,
            "enqueued_at": time.time(),
        }

        # Store task metadata and push to queue
        await r.set(f"{TASK_PREFIX}{workflow_id}", json.dumps(task_payload), ex=86400)
        await r.rpush(WORKFLOW_QUEUE_KEY, json.dumps(task_payload))
        await r.aclose()
        logger.info(f"Enqueued workflow {workflow_id} to Redis queue {WORKFLOW_QUEUE_KEY}")
        return True

    @classmethod
    async def get_queue_depth(cls) -> int:
        """Returns current number of pending tasks in queue."""
        r = await cls.get_redis_client()
        if not r:
            return 0
        depth = await r.llen(WORKFLOW_QUEUE_KEY)
        await r.aclose()
        return depth
