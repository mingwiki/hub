import json
import pickle
from datetime import datetime, timedelta

from piccolo.columns import JSON, Bytea, Serial, Timestamp, Varchar
from piccolo.table import Table

from piccolo_conf import DB
from utils import generate_key, logger

log = logger(__name__)


class BaseModel(Table):
    id = Serial(primary_key=True)
    created_at = Timestamp(
        default=datetime.now,
        index=True,
    )

    class Meta:
        schema = "public"
        database = DB


class Cache(Table):
    key = Varchar(length=255, primary_key=True)
    data = Bytea()
    access_time = Timestamp(
        auto_update=True,
        null=True,
        index=True,
    )
    created_at = Timestamp(
        default=datetime.now,
        index=True,
    )

    class Meta:
        schema = "public"
        database = DB


class Keys(BaseModel):
    key = Varchar(length=255, unique=True)
    data = JSON()
    access_time = Timestamp(
        auto_update=True,
        null=True,
        index=True,
    )


class Webhooks(BaseModel):
    key = Varchar(length=255, unique=True)
    data = JSON()
    sent_at = Timestamp(
        null=True,
        index=True,
        default=None,
    )


async def create_tables():
    await Keys.create_table(if_not_exists=True)
    await Cache.create_table(if_not_exists=True)
    await Webhooks.create_table(if_not_exists=True)


class KeysDB:
    @staticmethod
    async def set(key, data):
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                log.error(f"Invalid JSON data for key {key}: {data}")
                return
        return await Keys.insert(Keys(key=key, data=data)).on_conflict(
            target=Keys.key,
            action="DO UPDATE",
            values=[Keys.data],
        )

    @staticmethod
    async def get(key):
        result = await Keys.select().where(Keys.key == key).first()
        if not result:
            return None
        data = result["data"]
        if isinstance(data, str):
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                log.error(f"Failed to parse JSON data for key {key}: {data}")
                return None
        return data

    @staticmethod
    async def delete(key):
        return await Keys.delete().where(Keys.key == key)


class SqliteCache:
    @staticmethod
    async def set(key, data):
        serialized_data = pickle.dumps(data)
        return await Cache.insert(Cache(key=key, data=serialized_data)).on_conflict(
            target=Cache.key,
            action="DO UPDATE",
            values=[Cache.data],
        )

    @staticmethod
    async def get(key):
        result = await Cache.select().where(Cache.key == key).first()
        if not result:
            return None
        return pickle.loads(result["data"])

    @staticmethod
    async def delete(key):
        return await Cache.delete().where(Cache.key == key)

    @staticmethod
    async def delete_x_days_ago_old_items(days):
        cutoff_date = datetime.now() - timedelta(days=days)
        return await Cache.delete().where(Cache.access_time < cutoff_date)

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
        key = generate_key(64)
        while await Webhooks.select().where(Webhooks.key == key).first():
            key = generate_key(64)
        return await Webhooks.insert(Webhooks(key=key, data=data)).on_conflict(
            target=Webhooks.key,
            action="DO UPDATE",
            values=[Webhooks.data],
        )

    @staticmethod
    async def get_unsent_entries():
        return await Webhooks.select().where(Webhooks.sent_at.is_null())

    @staticmethod
    async def mark_as_sent(key):
        return await Webhooks.update({Webhooks.sent_at: datetime.now()}).where(
            Webhooks.key == key
        )
