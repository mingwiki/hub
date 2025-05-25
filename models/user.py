from datetime import datetime, timezone

import bcrypt
from fastapi import HTTPException

from schemas import UserInDB, UserInfo, UserRegister

from .database import Q, t_user


class User:

    def register(userinfo: UserRegister):
        existing_user = t_user.get(Q.username == userinfo.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")

        return UserInDB(
            username=userinfo.username,
            email=userinfo.email,
            hashed_password=bcrypt.hashpw(
                userinfo.password.encode(), bcrypt.gensalt()
            ).decode(),
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

    def update(new_userinfo: UserInfo, current_user: dict):
        if new_userinfo.username != current_user["username"]:
            existing_user = t_user.get(Q.username == new_userinfo.username)
            if existing_user:
                raise HTTPException(status_code=400, detail="用户名已存在")

        return UserInDB(
            username=new_userinfo.username or current_user["username"],
            email=new_userinfo.email or current_user["email"],
            is_active=new_userinfo.is_active or current_user["is_active"],
            is_admin=current_user["is_admin"],
            updated_at=datetime.now(timezone.utc).isoformat(),
            hashed_password=bcrypt.hashpw(
                new_userinfo.password.encode(), bcrypt.gensalt()
            ).decode(),
        ).model_dump()

    def delete(username: str):
        return {"message": f"{username}账户已删除"}
