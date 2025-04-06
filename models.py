import json

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from prisma import Prisma
from schemas import User
from utils import decode, encode, generate_key, logger

log = logger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
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


async def get_current_user(token: str = Depends(oauth2_scheme)):
    jwt_config = await get_config("jwt_config")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, jwt_config["secret_key"], algorithms=[jwt_config["algorithm"]])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await db.user.find_unique(where={"username": username})
    if user is None:
        raise credentials_exception
    return user


class UserDB:
    async def register(self, username: str, password: str):
        existing_user = await db.user.find_unique(where={"username": username})

        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")

        new_user = await db.user.create({"username": username, "hashed_password": pwd_context.hash(password)})
        return {"id": new_user.id, "username": new_user.username}

    async def authenticate(self, username: str, password: str):
        user = await db.user.find_unique(where={"username": username})
        if not user or not pwd_context.verify(password, user.hashed_password):
            return None
        return user

    async def change_password(self, old_password: str, new_password: str, current_user: User):
        if not pwd_context.verify(old_password, current_user.hashed_password):
            raise HTTPException(400, "原密码错误")

        if old_password == new_password:
            raise HTTPException(400, "新旧密码不能相同")

        return {
            "message": "密码修改成功",
            "sql": await db.user.update(where={"id": current_user.id}, data={"hashed_password": pwd_context.hash(new_password)}),
        }
