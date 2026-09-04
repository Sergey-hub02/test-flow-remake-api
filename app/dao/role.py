from sqlalchemy import select
from uuid import UUID

from app.dao.base import BaseDAO
from app.db.tables import Role


class RoleDAO(BaseDAO):
    async def find_by_id(self, role_id: UUID) -> Role | None:
        return await self._db.scalar(select(Role).where(Role.id == role_id))

    async def find_by_code(self, code: str) -> Role | None:
        return await self._db.scalar(select(Role).where(Role.code == code))
