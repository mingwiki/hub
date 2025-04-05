from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from models import db
from utils import logger

router = APIRouter(tags=["Authorization"])
log = logger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "helloworld"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def authenticate_user(username: str, password: str):
    user = await db.user.find_first(where={"username": username})
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await db.user.find_unique(where={"username": username})
    if user is None:
        raise credentials_exception
    return user


class UserLogin(BaseModel):
    username: str
    password: str


@router.post("/register", status_code=201)
async def user_register(user: UserLogin):
    existing_user = await db.user.find_unique(where={"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    new_user = await db.user.create({"username": user.username, "hashed_password": get_password_hash(user.password)})
    return {"id": new_user.id, "username": new_user.username}


@router.post("/token")
async def user_validate(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


class User(UserLogin):
    id: int | None = None
    is_active: bool | None = None
    hashed_password: str | None = None


@router.get("/me")
async def user_info(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username, "is_active": current_user.is_active}


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str


@router.post("/change-password")
async def change_password(req: PasswordChangeRequest, current_user=Depends(get_current_user)):
    if not pwd_context.verify(req.old_password, current_user.hashed_password):
        raise HTTPException(400, "原密码错误")

    if req.old_password == req.new_password:
        raise HTTPException(400, "新旧密码不能相同")

    new_hashed_password = pwd_context.hash(req.new_password)

    return {"message": "密码修改成功", "sql": await db.user.update(where={"id": current_user.id}, data={"hashed_password": new_hashed_password})}
