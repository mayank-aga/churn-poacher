"""
Persistent Background Task Worker.
Processes enqueued workflow tasks from Redis, manages timeouts,
handles partial recoveries, tracks heartbeats, and ensures graceful shutdown.
"""

import asyncio
import json
import signal
import time
from typing import Optional
import redis.asyncio as aioredis
from sqlalchemy import select

from app.core.config import settings
from app.core.logging import logger
from app.db.session import AsyncSessionLocal
from app.models.workflow import WorkflowExecution
from app.agents.orchestrator.pipeline import PipelineRunner
from app.worker.queue import WORKFLOW_QUEUE_KEY, WorkflowTaskQueue


class BackgroundWorker:
    """Production background worker consuming from Redis task queue."""

    def __init__(self, poll_interval: float = 1.0):
        self.poll_interval = poll_interval
        self._running = False
        self._active_task: Optional[asyncio.Task] = None
        self._redis: Optional[aioredis.Redis] = None

    async def connect_redis(self) -> bool:
        try:
            self._redis = aioredis.from_url(settings.REDIS_URL, socket_timeout=5.0)
            await self._redis.ping()
            return True
        except Exception as e:
            logger.warning(f"Worker unable to connect to Redis at {settings.REDIS_URL}: {e}")
            return False

    async def _emit_heartbeat(self):
        """Emits periodic worker heartbeat to Redis for health checks."""
        while self._running:
            try:
                if self._redis:
                    await self._redis.set("churn_poacher:worker:heartbeat", str(time.time()), ex=60)
            except Exception as e:
                logger.debug(f"Heartbeat emit error: {e}")
            await asyncio.sleep(settings.WORKER_HEARTBEAT_INTERVAL)

    async def process_task(self, raw_payload: str) -> None:
        """Processes a single workflow task with timeout and database persistence."""
        try:
            task = json.loads(raw_payload)
            workflow_id = task["workflow_id"]
            timeout_seconds = task.get("timeout_seconds", 60)
        except Exception as e:
            logger.error(f"Malformed task payload: {raw_payload}: {e}")
            return

        logger.info(f"Worker picked up workflow task {workflow_id}")

        async with AsyncSessionLocal() as db:
            try:
                res = await db.execute(
                    select(WorkflowExecution).where(WorkflowExecution.id == workflow_id)
                )
                workflow = res.scalar_one_or_none()
                if not workflow:
                    logger.error(f"Workflow {workflow_id} not found in database")
                    return

                # Execute pipeline through PipelineRunner
                await PipelineRunner.execute_workflow(
                    workflow=workflow,
                    db=db,
                    timeout_seconds=timeout_seconds,
                )
                logger.info(f"Worker completed workflow task {workflow_id} with status {workflow.status}")

            except Exception as e:
                logger.error(f"Error processing workflow {workflow_id}: {e}", exc_info=True)
            finally:
                # Release distributed lock
                if workflow and workflow.company_id:
                    await WorkflowTaskQueue.release_lock(workflow.company_id)
                if workflow and workflow.signal_id:
                    await WorkflowTaskQueue.release_lock(workflow.signal_id)

    async def run(self, max_tasks: Optional[int] = None) -> None:
        """Main worker loop. Continually pops tasks from Redis and executes them."""
        connected = await self.connect_redis()
        if not connected:
            logger.error("Worker failed to connect to Redis. Exiting worker loop.")
            return

        self._running = True
        heartbeat_task = asyncio.create_task(self._emit_heartbeat())
        tasks_processed = 0

        logger.info(f"Churn Poacher Background Worker started. Listening on {WORKFLOW_QUEUE_KEY}...")

        try:
            while self._running:
                try:
                    # Non-blocking pop with timeout
                    item = await self._redis.blpop([WORKFLOW_QUEUE_KEY], timeout=int(self.poll_interval))
                    if item:
                        _, raw_payload = item
                        await self.process_task(raw_payload)
                        tasks_processed += 1
                        if max_tasks and tasks_processed >= max_tasks:
                            logger.info(f"Reached max tasks limit ({max_tasks}). Stopping worker.")
                            break
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Worker loop error: {e}")
                    await asyncio.sleep(1.0)
        finally:
            self._running = False
            heartbeat_task.cancel()
            if self._redis:
                await self._redis.aclose()
            logger.info("Background Worker shut down cleanly.")

    def stop(self) -> None:
        """Signals worker to stop gracefully after current task completes."""
        logger.info("Initiating graceful worker shutdown...")
        self._running = False
