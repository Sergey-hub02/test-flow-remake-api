from pydantic import BaseModel, Field, EmailStr, ConfigDict

from typing import Optional
from datetime import date, datetime
from uuid import UUID

from app.models.role import RoleGet
from app.models.common import Sorting, Pagination


class UserBase(BaseModel):
    last_name: str = Field()
    first_name: str = Field()
    second_name: Optional[str] = Field(default=None)
    birthday: date = Field()
    email: EmailStr = Field()


class UserPost(UserBase):
    password: str = Field(min_length=6)
    role_id: Optional[UUID] = Field(default=None)


class UserGet(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field()
    photo: Optional[str] = Field(default=None)
    role: RoleGet = Field()
    created_at: datetime = Field()
    updated_at: datetime = Field()


class UserFilter(Sorting, Pagination):
    full_name: Optional[str] = Field(default=None)
    birthday: Optional[date] = Field(default=None)
    email: Optional[str] = Field(default=None)


class UserPut(BaseModel):
    last_name: Optional[str] = Field(default=None)
    first_name: Optional[str] = Field(default=None)
    second_name: Optional[str] = Field(default=None)
    birthday: Optional[date] = Field(default=None)
