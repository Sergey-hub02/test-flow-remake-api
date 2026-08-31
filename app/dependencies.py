from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.db.conexion import AsyncSessionLocal
from app.dao.role import RoleDAO
from app.dao.user import UserDAO
from app.services.user import UserService


async def get_db_session():
    async with AsyncSessionLocal() as db:
        yield db


async def get_user_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserService:
    role_dao = RoleDAO(db)
    user_dao = UserDAO(db)

    return UserService(role_dao=role_dao, user_dao=user_dao)
