from datetime import datetime, timezone

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=2, description="用户名")
    email: EmailStr | None = Field(default=None, description="邮箱地址")
    is_active: bool = Field(default=True, description="是否激活")


class UserUpdate(UserBase):
    password: str = Field(..., min_length=4, description="密码")


class UserResponse(UserBase):
    is_admin: bool = Field(default=False, description="是否管理员")
    updated_at: str = Field(default=datetime.now(timezone.utc).isoformat())


class UserInfo(UserResponse):
    hashed_password: str = Field(..., description="哈希密码")
