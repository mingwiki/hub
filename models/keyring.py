import json
from datetime import datetime, timezone

from fastapi import HTTPException
from tortoise import fields
from tortoise.exceptions import DoesNotExist
from tortoise.models import Model


class Keyring(Model):
    key = fields.CharField(max_length=255, unique=True, pk=True)
    val = fields.TextField()
    created_at = fields.DatetimeField(default=datetime.now(timezone.utc))
    updated_at = fields.DatetimeField(default=datetime.now(timezone.utc), auto_now=True)

    class Meta:
        table = "keyring"

    def get_val(self):
        return json.loads(self.val) if self.val else None

    def set_val(self, data):
        self.val = json.dumps(data)


class KeyringHandler:
    async def set(self, key: str, data: dict):
        try:
            existing_key = await Keyring.get(key=key)
            existing_key.set_val(data)
            await existing_key.save()
        except DoesNotExist:
            new_key = await Keyring.create(key=key)
            new_key.set_val(data)
            await new_key.save()

    async def get(self, key: str) -> dict:
        try:
            entry = await Keyring.get(key=key)
            return entry.get_val() if entry else None
        except DoesNotExist:
            return None

    async def delete(self, key: str):
        try:
            entry = await Keyring.get(key=key)
            await entry.delete()
        except DoesNotExist:
            raise HTTPException(status_code=404, detail=f"Key '{key}' not found")
