from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from models import db, get_config
from utils import logger

router = APIRouter(tags=["Authorization"])
log = logger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


async def create_access_token(data: dict):
    jwt_config = await get_config("jwt_config")
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=jwt_config["expire_minutes"])
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, jwt_config["secret_key"], algorithm=jwt_config["algorithm"])


async def authenticate_user(username: str, password: str):
    user = await db.user.find_first(where={"username": username})
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


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


@router.post("/register", status_code=201)
async def user_register(username: str = Form(..., min_length=2), password: str = Form(..., min_length=4)):
    existing_user = await db.user.find_unique(where={"username": username})
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    new_user = await db.user.create({"username": username, "hashed_password": get_password_hash(password)})
    return {"id": new_user.id, "username": new_user.username}


@router.post("/token")
async def user_validate(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

    access_token = await create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


class User(BaseModel):
    id: int | None = None
    username: str
    password: str
    is_active: bool | None = None
    hashed_password: str | None = None


@router.get("/me")
async def user_info(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username, "is_active": current_user.is_active}


@router.post("/change-password")
async def change_password(old_password: str = Form(..., min_length=4), new_password: str = Form(..., min_length=4), current_user=Depends(get_current_user)):
    if not pwd_context.verify(old_password, current_user.hashed_password):
        raise HTTPException(400, "原密码错误")

    if old_password == new_password:
        raise HTTPException(400, "新旧密码不能相同")

    new_hashed_password = pwd_context.hash(new_password)

    return {"message": "密码修改成功", "sql": await db.user.update(where={"id": current_user.id}, data={"hashed_password": new_hashed_password})}
