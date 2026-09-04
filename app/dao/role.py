from sqlalchemy import select

from app.dao.base import BaseDAO
from app.db.tables import Role


class RoleDAO(BaseDAO):
    async def find_by_code(self, code: str) -> Role | None:
        return await self._db.scalar(select(Role).where(Role.code == code))
