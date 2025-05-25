from datetime import datetime, timezone

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=2, description="用户名")


class UserRegister(UserBase):
    password: str = Field(..., min_length=4, description="密码")


class UserUpdate(UserRegister):
    email: EmailStr | None = Field(default=None, description="邮箱地址")
    is_active: bool = Field(default=True, description="是否激活")


class UserResponse(UserBase):
    email: EmailStr | None = Field(default=None, description="邮箱地址")
    is_active: bool = Field(default=True, description="是否激活")
    is_admin: bool = Field(default=False, description="是否管理员")
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserInDB(UserResponse):
    hashed_password: str = Field(..., description="哈希密码")
