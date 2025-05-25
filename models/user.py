from datetime import datetime, timezone

import bcrypt
from fastapi import HTTPException

from schemas import UserInDB, UserUpdate

from .database import Q, t_user


class User:
    def register(userinfo: UserUpdate):
        existing_user = t_user.get(Q.username == userinfo.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")

        return UserInDB(
            username=userinfo.username,
            email=userinfo.email,
            is_active=userinfo.is_active,
            hashed_password=bcrypt.hashpw(
                userinfo.password.encode(), bcrypt.gensalt()
            ).decode(),
            is_admin=False,
            updated_at=datetime.now(timezone.utc).isoformat(),
        ).model_dump()

    def authenticate(username: str, password: str):
        user = t_user.get(Q.username == username)
        if not user:
            raise HTTPException(status_code=400, detail="用户名错误")
        if not user["is_active"]:
            raise HTTPException(status_code=400, detail="用户未激活")
        if not bcrypt.checkpw(password.encode(), user["hashed_password"].encode()):
            raise HTTPException(status_code=400, detail="密码错误")

        return user

    def update(new_userinfo: UserUpdate, current_user: dict):
        if new_userinfo.username != current_user["username"]:
            existing_user = t_user.get(Q.username == new_userinfo.username)
            if existing_user:
                raise HTTPException(status_code=400, detail="用户名已存在")

        return UserInDB(
            username=new_userinfo.username,
            email=new_userinfo.email,
            is_active=new_userinfo.is_active,
            hashed_password=bcrypt.hashpw(
                new_userinfo.password.encode(), bcrypt.gensalt()
            ).decode(),
            is_admin=current_user["is_admin"],
            updated_at=datetime.now(timezone.utc).isoformat(),
        ).model_dump()

    def delete(username: str):
        return {"message": f"{username}账户已删除"}
