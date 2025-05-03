from datetime import datetime, timezone

import bcrypt
from fastapi import HTTPException

from database import Q, t_user


class User:
    @staticmethod
    def register(username: str, password: str):
        existing_user = t_user.get(Q.username == username)
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user = {
            "username": username,
            "hashed_password": hashed_password,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "is_admin": False,
            "is_active": True,
        }

        return {"id": t_user.insert(user), "user": user}

    @staticmethod
    def authenticate(username: str, password: str):
        user = t_user.get(Q.username == username)
        if not user:
            return None

        if not bcrypt.checkpw(password.encode(), user["hashed_password"].encode()):
            return None

        return user

    @staticmethod
    def change_password(old_password: str, new_password: str, current_user: dict):
        if not bcrypt.checkpw(
            old_password.encode(), current_user["hashed_password"].encode()
        ):
            raise HTTPException(400, "原密码错误")

        if old_password == new_password:
            raise HTTPException(400, "新旧密码不能相同")

        hashed_password = bcrypt.hashpw(
            new_password.encode(), bcrypt.gensalt()
        ).decode()
        t_user.update(
            {
                "hashed_password": hashed_password,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            doc_ids=[current_user.doc_id],
        )

        return {"message": "密码修改成功"}
