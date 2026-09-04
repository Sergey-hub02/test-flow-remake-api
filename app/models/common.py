from pydantic import BaseModel, Field
from typing import Literal


class Sorting(BaseModel):
    order_by: str = Field(default="created_at")
    order_dir: Literal["asc", "desc"] = Field(default="desc")


class Pagination(BaseModel):
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
