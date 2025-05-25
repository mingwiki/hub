from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from models import User, get_current_user, jwt_create_token
from schemas import UserInfo, UserUpdate
from utils import atimer

router = APIRouter(tags=["User Info"], prefix="/user")


@router.post("/register", status_code=201, response_model=UserInfo)
@atimer
async def user_register(userinfo: UserUpdate = Form(...)):
    return User.register(userinfo)


@router.post("/token")
@atimer
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


@router.get("/me", response_model=UserInfo)
@atimer
async def get_user_info(current_user=Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserInfo)
@atimer
async def update_user_info(
    new_userinfo: UserUpdate = Form(...),
    current_user=Depends(get_current_user),
):
    return User.update(new_userinfo, current_user)


@router.delete("/me")
@atimer
async def delete_user_info(
    username: str = Form(...),
    current_user=Depends(get_current_user),
):
    if username != current_user["username"]:
        raise HTTPException(status_code=403, detail="Permission denied")
    return User.delete(username)
