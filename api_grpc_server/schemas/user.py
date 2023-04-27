import uuid
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, validator

from models.user import SocialNetworksEnum, UserRole


class UserLoginDto(BaseModel):
    email: EmailStr
    password: str


class UserCreateDto(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str


class UserUpdateDto(BaseModel):
    first_name: str
    last_name: str


class UserDataInToken(BaseModel):
    id: UUID
    email: str
    role: UserRole

    class Config:
        orm_mode = True
        use_enum_values = True


class UserShort(UserDataInToken):
    email: str
    first_name: str
    last_name: str


class UserResponse(UserShort):
    is_active: bool
    created_at: datetime


class UserInDb(UserShort):
    is_active: bool
    created_at: datetime


class UserUpdateRoleDto(BaseModel):
    user_id: UUID
    role: UserRole

    class Config:
        use_enum_values = True


class SocialCreateDto(BaseModel):
    user_id: UUID
    social_id: str
    social_name: SocialNetworksEnum
    full_prov_data: str | None = None


class SocialUpdateDto(BaseModel):
    social_name: str
    full_prov_data: str | None = None
