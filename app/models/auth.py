from pydantic import BaseModel, Field, EmailStr
from uuid import UUID
from typing import Literal

type JWTType = Literal["access", "refresh"]


class TokenPayload(BaseModel):
    id: UUID = Field()
    email: EmailStr = Field()
    role: str = Field()
    user_agent: str = Field()


class Token(BaseModel):
    type: JWTType = Field()
    content: str = Field()
    jti: UUID = Field()
    exp: int = Field()
    iat: int = Field()
    payload: TokenPayload = Field()


class NewPasswordFields(BaseModel):
    password: str = Field(min_length=6)
    repeated_password: str = Field(min_length=6)


class NewEmailFields(BaseModel):
    email: EmailStr = Field()
    password: str = Field()
    repeated_password: str = Field()
