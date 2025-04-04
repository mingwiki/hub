import json
from datetime import datetime, timedelta

from prisma import Prisma
from utils import decode, encode, generate_key, logger

log = logger(__name__)

db = Prisma()


class KeysDB:
    @staticmethod
    async def set(key, data):
        await db.keys.upsert(
            where={"key": key},
            data={
                "create": {"key": key, "data": data},
                "update": {"data": data},
            },
        )

    @staticmethod
    async def get(key):
        entry = await db.keys.find_unique(where={"key": key})
        if entry:
            await db.keys.update(
                where={"key": key},
                data={"access_at": datetime.now()},
            )
            return entry.data
        return None

    @staticmethod
    async def delete(key):
        await db.keys.delete(where={"key": key})


class CacheDB:
    @staticmethod
    async def set(key, data):
        b64_data = encode(data)
        await db.cache.upsert(
            where={"key": key},
            data={
                "create": {"key": key, "data": b64_data},
                "update": {"data": b64_data},
            },
        )

    @staticmethod
    async def get(key):
        entry = await db.cache.find_unique(where={"key": key})
        if entry:
            await db.cache.update(
                where={"key": key},
                data={"access_at": datetime.now()},
            )
            return decode(entry.data)
        return None

    @staticmethod
    async def delete(key):
        await db.cache.delete(where={"key": key})

    @staticmethod
    async def delete_x_days_ago_old_items(days):
        cutoff_date = datetime.now() - timedelta(days=days)
        await db.cache.delete_many(where={"access_at": {"lt": cutoff_date}})

    async def get_short_link_data(self, short_link):
        return await self.get(f"short_link:{short_link}")

    async def save_short_link_data(self, data):
        short_link = generate_key()
        while await self.get_short_link_data(short_link):
            short_link = generate_key()
        await self.set(f"short_link:{short_link}", data)
        return short_link


async def get_config(name):
    return await KeysDB.get(name)
