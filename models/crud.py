import pickle
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from utils import generate_key, logger

from .db import Cache, Keys, SessionLocal, Webhooks

log = logger(__name__)


class KeysDB:
    @staticmethod
    async def set(key, data):
        async with SessionLocal() as session:
            async with session.begin():
                stmt = select(Keys).where(Keys.key == key)
                entry = (await session.execute(stmt)).scalars().first()
                if entry:
                    entry.data = data
                else:
                    session.add(Keys(key=key, data=data))

    @staticmethod
    async def get(key):
        async with SessionLocal() as session:
            stmt = select(Keys.data).where(Keys.key == key)
            return (await session.execute(stmt)).scalar()

    @staticmethod
    async def delete(key):
        async with SessionLocal() as session:
            async with session.begin():
                await session.execute(Keys.__table__.delete().where(Keys.key == key))


class CacheDB:
    @staticmethod
    async def set(key, data):
        serialized_data = pickle.dumps(data)
        async with SessionLocal() as session:
            async with session.begin():
                stmt = select(Cache).where(Cache.key == key)
                entry = (await session.execute(stmt)).scalars().first()
                if entry:
                    entry.data = serialized_data
                else:
                    session.add(Cache(key=key, data=serialized_data))

    @staticmethod
    async def get(key):
        async with SessionLocal() as session:
            stmt = select(Cache.data).where(Cache.key == key)
            result = (await session.execute(stmt)).scalar()
            return pickle.loads(result) if result else None

    @staticmethod
    async def delete(key):
        async with SessionLocal() as session:
            async with session.begin():
                await session.execute(Cache.__table__.delete().where(Cache.key == key))

    @staticmethod
    async def delete_x_days_ago_old_items(days):
        cutoff_date = datetime.now() - timedelta(days=days)
        async with SessionLocal() as session:
            async with session.begin():
                await session.execute(
                    Cache.__table__.delete().where(Cache.access_at < cutoff_date)
                )

    async def get_short_link_data(self, short_link):
        return await self.get(f"short_link:{short_link}")

    async def save_short_link_data(self, data):
        short_link = generate_key()
        while await self.get_short_link_data(short_link):
            short_link = generate_key()
        await self.set(f"short_link:{short_link}", data)
        return short_link


class WebhooksDB:
    @staticmethod
    async def save_entry(data):
        async with SessionLocal() as session:
            async with session.begin():
                key = generate_key(64)
                while await session.get(Webhooks, key):
                    key = generate_key(64)
                session.add(Webhooks(key=key, data=data))
                return key

    @staticmethod
    async def get_unsent_entries():
        async with SessionLocal() as session:
            stmt = select(Webhooks).where(Webhooks.sent_at.is_(None))
            return (await session.execute(stmt)).scalars().all()

    @staticmethod
    async def mark_as_sent(key):
        async with SessionLocal() as session:
            async with session.begin():
                await session.execute(
                    Webhooks.__table__.update()
                    .where(Webhooks.key == key)
                    .values(sent_at=datetime.now())
                )


async def get_config(name):
    return await KeysDB.get(name)
