import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from routers.swas import create_snapshot
from routers.webhooks import send_summary


async def send_daily_summary_to_fuming():
    return await send_summary("fuming")


async def main():
    scheduler = AsyncIOScheduler(timezone="Asia/Singapore")

    scheduler.add_job(create_snapshot, "cron", hour=5, minute=0)
    scheduler.add_job(send_daily_summary_to_fuming, "cron", hour="8,20", minute=0)

    scheduler.start()
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
