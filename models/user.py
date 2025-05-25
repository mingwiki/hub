from datetime import datetime, timezone

import bcrypt
from fastapi import HTTPException

from schemas import UserInDB, UserRegister, UserResponse, UserUpdate

from .database import Q, t_user


class User:

    def register(userinfo: UserRegister):
        existing_user = t_user.get(Q.username == userinfo.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")

        user = UserInDB(
            username=userinfo.username,
            hashed_password=bcrypt.hashpw(
                userinfo.password.encode(), bcrypt.gensalt()
            ).decode(),
        ).model_dump()
        t_user.insert(user)
        return user

    def authenticate(username: str, password: str):
        user = t_user.get(Q.username == username)
        if not user:
            raise HTTPException(status_code=400, detail="用户名错误")
        if not user["is_active"]:
            raise HTTPException(status_code=400, detail="用户未激活")
        if not bcrypt.checkpw(password.encode(), user["hashed_password"].encode()):
            raise HTTPException(status_code=400, detail="密码错误")

        return user

    def update(new_userinfo: UserUpdate, current_user: UserResponse):
        if new_userinfo.username != current_user["username"]:
            existing_user = t_user.get(Q.username == new_userinfo.username)
            if existing_user:
                raise HTTPException(status_code=400, detail="用户名已存在")

        user = UserInDB(
            username=new_userinfo.username,
            hashed_password=bcrypt.hashpw(
                new_userinfo.password.encode(), bcrypt.gensalt()
            ).decode(),
            email=new_userinfo.email,
            is_active=new_userinfo.is_active,
            is_admin=current_user["is_admin"],
        ).model_dump()
        t_user.update(user, Q.username == current_user["username"])
        return user

    def delete(username: str):
        return {"message": f"{username}账户已删除"}
