import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from models import db
from routers.swas import create_snapshot


async def main():
    scheduler = AsyncIOScheduler(timezone="Asia/Singapore")
    await db.connect()

    scheduler.add_job(create_snapshot, "cron", hour=5, minute=0)

    scheduler.start()
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
