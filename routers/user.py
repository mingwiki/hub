from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from models import User, get_current_user, jwt_create_token
from schemas import UserUpdate
from utils import logger

router = APIRouter(tags=["User Info"], prefix="/user")
log = logger(__name__)


@router.post("/register", status_code=201)
async def user_register(userinfo: UserUpdate = Form(...)):
    return User.register(userinfo)


@router.post("/token")
async def user_login(form_data: OAuth2PasswordRequestForm = Depends()):
    current_user = User.authenticate(form_data.username, form_data.password)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误"
        )

    return {
        "access_token": jwt_create_token(current_user["username"]),
        "token_type": "bearer",
    }


@router.get("/me")
async def get_user_info(current_user=Depends(get_current_user)):
    current_user.pop("hashed_password")
    return current_user


@router.put("/me")
async def update_user_info(
    userinfo: UserUpdate = Form(...),
    current_user=Depends(get_current_user),
):
    return User.update(userinfo, current_user)


@router.delete("/me")
async def delete_user_info(
    username: str = Form(...),
    current_user=Depends(get_current_user),
):
    if username != current_user["username"]:
        raise HTTPException(status_code=403, detail="Permission denied")
    return User.delete(username)
