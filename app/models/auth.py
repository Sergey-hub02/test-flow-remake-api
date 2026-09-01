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
