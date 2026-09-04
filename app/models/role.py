from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class RoleBase(BaseModel):
    name: str = Field()
    code: str = Field()
    description: Optional[str] = Field(default=None)


class RoleGet(RoleBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field()
    created_at: datetime = Field()
    updated_at: datetime = Field()
