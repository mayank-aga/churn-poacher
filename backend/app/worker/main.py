"""
Worker CLI Entrypoint.
Runs the persistent background worker with graceful OS signal handling (SIGTERM, SIGINT).
"""

import asyncio
import signal
import sys

from app.core.logging import setup_logging, logger
from app.worker.worker import BackgroundWorker


def main():
    setup_logging()
    logger.info("Booting Churn Poacher background worker daemon...")

    worker = BackgroundWorker()

    # Handle signals for graceful container shutdown
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def handle_signal(sig, frame):
        logger.info(f"Received signal {sig}. Requesting worker stop...")
        worker.stop()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        loop.run_until_complete(worker.run())
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received.")
    finally:
        loop.close()
        logger.info("Worker process terminated.")


if __name__ == "__main__":
    main()
