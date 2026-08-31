from sqlalchemy import insert

from app.dao.base import BaseDAO
from app.models.user import UserPost
from app.db.tables import User


class UserDAO(BaseDAO):
    async def save(self, user_fields: UserPost) -> User:
        user = (
            await self._db.execute(
                insert(User).values(user_fields.model_dump()).returning(User)
            )
        ).scalar_one()

        await self._db.commit()
        await self._db.refresh(user, attribute_names=["role"])

        return user
