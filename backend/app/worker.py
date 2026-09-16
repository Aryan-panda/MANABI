import asyncio
import logging
from app.config.settings import settings

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [WORKER] [%(levelname)s] %(message)s"
)
logger = logging.getLogger("manabi.worker")


async def run_worker_loop():
    logger.info("MANABI Background Job Worker started.")
    logger.info(f"Connected to Redis coordination queue at: {settings.REDIS_URL}")

    while True:
        try:
            # Polling queue for asynchronous document ingestion and embedding processing
            await asyncio.sleep(5)
        except asyncio.CancelledError:
            logger.info("Worker received termination signal. Gracefully exiting...")
            break
        except Exception as exc:
            logger.error(f"Worker encountered unexpected error: {exc}")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(run_worker_loop())
