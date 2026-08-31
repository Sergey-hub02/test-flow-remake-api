from sqlalchemy.ext.asyncio import AsyncSession


class BaseDAO:
    _db: AsyncSession

    def __init__(self, db: AsyncSession):
        self._db = db
