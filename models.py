import json

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
        entry = await db.keys.find_first(where={"key": key})
        if entry:
            return json.loads(entry.data)
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
        entry = await db.cache.find_first(where={"key": key})
        if entry:
            return decode(entry.data)
        return None

    @staticmethod
    async def delete(key):
        await db.cache.delete(where={"key": key})

    async def get_data_from_short_link(self, short_link):
        return await self.get(f"short_link:{short_link}")

    async def save_data_as_short_link(self, data):
        short_link = generate_key()
        while await self.get_data_from_short_link(short_link):
            short_link = generate_key()
        await self.set(f"short_link:{short_link}", data)
        return short_link


async def get_config(name):
    return await KeysDB.get(name)
