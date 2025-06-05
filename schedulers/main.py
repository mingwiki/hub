import asyncio
import logging
import sys

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from apps.swas import create_snapshot

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s]-%(levelname)s-%(name)s-%(funcName)s()-L%(lineno)d ==> %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


async def main():
    scheduler = AsyncIOScheduler(timezone="Asia/Singapore")

    try:
        scheduler.add_job(create_snapshot, "cron", hour=5, minute=0)
        scheduler.start()
        while True:
            await asyncio.sleep(1)
    finally:
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
