import os
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from database import Q, t_user
from utils import logger

log = logger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def jwt_decode(token: str):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms="HS256")
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception


def jwt_create_token(username: str):
    to_encode = {
        "sub": username,
        "exp": datetime.now() + timedelta(minutes=60),
    }
    return jwt.encode(to_encode, os.getenv("JWT_SECRET_KEY"), algorithm="HS256")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    username = jwt_decode(token)
    user = t_user.get(Q.username == username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
