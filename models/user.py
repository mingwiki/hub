from datetime import datetime, timezone

import bcrypt
from fastapi import HTTPException
from tortoise import fields
from tortoise.exceptions import DoesNotExist
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=255, unique=True)
    email = fields.CharField(max_length=255, null=True)
    hashed_password = fields.CharField(max_length=255)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(default=datetime.now(timezone.utc))
    updated_at = fields.DatetimeField(auto_now=True)

    # Helper functions for User model
    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), self.hashed_password.encode())

    def set_password(self, password: str):
        self.hashed_password = bcrypt.hashpw(
            password.encode(), bcrypt.gensalt()
        ).decode()

    class Meta:
        table = "users"


class UserHandler:
    @staticmethod
    async def register(username: str, password: str):
        existing_user = await User.filter(username=username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")

        new_user = User(username=username)
        new_user.set_password(password)
        await new_user.save()

        return {"id": new_user.id, "username": new_user.username}

    @staticmethod
    async def authenticate(username: str, password: str):
        try:
            user = await User.get(username=username)
            if not user.check_password(password):
                return None
            return user
        except DoesNotExist:
            return None

    @staticmethod
    async def change_password(old_password: str, new_password: str, current_user: User):
        if not current_user.check_password(old_password):
            raise HTTPException(400, "原密码错误")

        if old_password == new_password:
            raise HTTPException(400, "新旧密码不能相同")

        current_user.set_password(new_password)
        await current_user.save()

        return {"message": "密码修改成功"}
