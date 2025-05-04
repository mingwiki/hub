from datetime import datetime, timezone

import bcrypt
from fastapi import HTTPException

from database import Q, t_user
from schemas import UserCreate, UserInfo, UserUpdate


class User:
    def register(userinfo: UserCreate):
        existing_user = t_user.get(Q.username == userinfo.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")

        user = UserInfo(
            username=userinfo.username,
            hashed_password=bcrypt.hashpw(
                userinfo.password.encode(), bcrypt.gensalt()
            ).decode(),
        ).model_dump()
        return {"id": t_user.insert(user), "user": user}

    def authenticate(username: str, password: str):
        user = t_user.get(Q.username == username)
        if not user:
            raise HTTPException(status_code=400, detail="用户名错误")
        if not user["is_active"]:
            raise HTTPException(status_code=400, detail="用户未激活")
        if not bcrypt.checkpw(password.encode(), user["hashed_password"].encode()):
            raise HTTPException(status_code=400, detail="密码错误")

        return user

    def change_password(old_password: str, new_password: str, current_user: dict):
        if not bcrypt.checkpw(
            old_password.encode(), current_user["hashed_password"].encode()
        ):
            raise HTTPException(400, "原密码错误")

        if old_password == new_password:
            raise HTTPException(400, "新旧密码不能相同")

        return {
            "message": "密码修改成功",
            "q": t_user.update(
                {
                    "hashed_password": bcrypt.hashpw(
                        new_password.encode(), bcrypt.gensalt()
                    ).decode(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
                doc_ids=[current_user.doc_id],
            ),
        }

    def update(userinfo: UserUpdate, current_user: dict):
        if userinfo.username != current_user["username"]:
            existing_user = t_user.get(Q.username == userinfo.username)
            if existing_user:
                raise HTTPException(status_code=400, detail="用户名已存在")
        return {
            "message": "用户信息已更新",
            "q": t_user.update(
                {
                    **userinfo.model_dump(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
                doc_ids=[current_user.doc_id],
            ),
        }

    def delete(username: str):
        return {"message": "用户已删除", "q": t_user.remove(Q.username == username)}
