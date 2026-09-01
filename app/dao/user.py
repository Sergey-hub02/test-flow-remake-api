from uuid import UUID

from sqlalchemy import (
    insert,
    ScalarResult,
    select,
    func,
    asc,
    desc,
    update,
    delete,
)
from sqlalchemy.orm import joinedload

from app.dao.base import BaseDAO
from app.models.user import UserPost, UserFilter, UserPut
from app.db.tables import User


class UserDAO(BaseDAO):
    __additional_columns = ("full_name",)

    @staticmethod
    def __check_column_exists(col: str) -> bool:
        return (
            col in User.__table__.columns or col in UserDAO.__additional_columns
        )

    async def save(self, user_fields: UserPost) -> User:
        user = (
            await self._db.execute(
                insert(User).values(user_fields.model_dump()).returning(User)
            )
        ).scalar_one()

        await self._db.commit()
        await self._db.refresh(user, attribute_names=["role"])

        return user

    async def find(
        self, user_filter: UserFilter
    ) -> tuple[int, ScalarResult[User]]:
        stmt = select(User).options(joinedload(User.role, innerjoin=True))
        count_stmt = select(func.count(User.id))

        if user_filter.full_name:
            condition = func.concat_ws(
                " ", User.last_name, User.first_name, User.second_name
            ).ilike(f"%{user_filter.full_name}%")

            stmt = stmt.where(condition)
            count_stmt = count_stmt.where(condition)
        if user_filter.birthday:
            condition = User.birthday == user_filter.birthday
            stmt = stmt.where(condition)
            count_stmt = count_stmt.where(condition)
        if user_filter.email:
            condition = User.email.ilike(f"%{user_filter.email}%")
            stmt = stmt.where(condition)
            count_stmt = count_stmt.where(condition)

        if not self.__check_column_exists(user_filter.order_by):
            raise NameError("Некорректное поле для сортировки!")

        sort_func = asc if user_filter.order_dir == "asc" else desc

        stmt = (
            stmt.order_by(sort_func(user_filter.order_by))
            .limit(user_filter.limit)
            .offset(user_filter.offset)
        )

        users = await self._db.scalars(stmt)
        users_count: int = (await self._db.execute(count_stmt)).scalar_one()

        return users_count, users

    async def find_by_id(self, user_id: UUID) -> User | None:
        return await self._db.scalar(
            select(User)
            .where(User.id == user_id)
            .options(joinedload(User.role, innerjoin=True))
        )

    async def update(self, user_id: UUID, user_fields: UserPut) -> User:
        update_fields = {
            k: v for k, v in user_fields.model_dump().items() if v is not None
        }

        if not update_fields:
            raise ValueError("Невозможно обновить данные пользователя!")

        user = (
            await self._db.execute(
                update(User)
                .values(update_fields)
                .where(User.id == user_id)
                .returning(User)
            )
        ).scalar_one()

        await self._db.commit()
        await self._db.refresh(user, attribute_names=["role"])

        return user

    async def delete(self, user_id: UUID) -> None:
        await self._db.execute(
            delete(User).where(User.id == user_id).returning(User)
        )
        await self._db.commit()
