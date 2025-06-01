import os
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from jose import JWTError, jwt


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
