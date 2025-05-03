from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from models import User, get_current_user, jwt_create_token
from utils import logger

router = APIRouter(tags=["Authorization"])
log = logger(__name__)


@router.post("/register", status_code=201)
async def user_register(
    username: str = Form(..., min_length=2), password: str = Form(..., min_length=4)
):
    return User.register(username, password)


@router.post("/token")
async def user_login(form_data: OAuth2PasswordRequestForm = Depends()):
    current_user = User.authenticate(form_data.username, form_data.password)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误"
        )

    access_token = jwt_create_token(current_user["username"])
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
async def user_info(current_user=Depends(get_current_user)):
    current_user.pop("hashed_password", None)
    return current_user


@router.put("/me")
async def update_user_info(
    old_password: str = Form(..., min_length=4),
    new_password: str = Form(..., min_length=4),
    current_user: dict = Depends(get_current_user),
):
    return User.change_password(old_password, new_password, current_user)
