from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from models import Q, t_user
from schemas import UserInDB
from utils import jwt_decode, logger

log = logger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    username = jwt_decode(token)
    user = t_user.get(Q.username == username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
