from fastapi import APIRouter, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm

from dependencies import get_current_user
from schemas import UserRegister, UserResponse, UserUpdate
from services import User
from utils import atimer

router = APIRouter(tags=["User Info"], prefix="/user")


@router.post("/register", status_code=201, response_model=UserResponse)
@atimer
async def user_register(userinfo: UserRegister = Form(...)):
    return User.register(userinfo)


@router.post("/token")
@atimer
async def user_login(form_data: OAuth2PasswordRequestForm = Depends()):
    return User.authenticate(form_data.username, form_data.password)


@router.get("/me", response_model=UserResponse)
@atimer
async def get_user_info(current_user=Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
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
    return User.delete(username, current_user)
