from sqlalchemy import ScalarResult
from sqlalchemy.exc import NoResultFound

from pwdlib import PasswordHash
from uuid import UUID

from app.dao.role import RoleDAO
from app.dao.user import UserDAO
from app.models.user import UserPost, UserFilter, UserPut
from app.db.tables import Role, User


class UserService:
    __role_dao: RoleDAO
    __user_dao: UserDAO
    __hasher: PasswordHash = PasswordHash.recommended()

    def __init__(self, role_dao: RoleDAO, user_dao: UserDAO):
        self.__role_dao = role_dao
        self.__user_dao = user_dao

    async def create(self, user_fields: UserPost) -> User:
        role: Role | None = await self.__role_dao.find_by_code("student")

        if not role:
            raise NoResultFound("Не удалось определить роль пользователя!")

        user_dict = user_fields.model_dump()
        user_dict["password"] = self.__hasher.hash(user_fields.password)
        user_dict["role_id"] = role.id

        return await self.__user_dao.save(UserPost(**user_dict))

    async def get(self, user_filter: UserFilter) -> tuple[int, ScalarResult[User]]:
        return await self.__user_dao.find(user_filter)

    async def get_one(self, user_id: UUID) -> User:
        user = await self.__user_dao.find_by_id(user_id)

        if not user:
            raise NoResultFound("Не удалось найти пользователя!")

        return user

    async def update(self, user_id: UUID, user_fields: UserPut) -> User:
        user = await self.__user_dao.find_by_id(user_id)

        if not user:
            raise NoResultFound("Не удалось найти пользователя!")

        return await self.__user_dao.update(user_id, user_fields)

    async def remove(self, user_id: UUID) -> User:
        user = await self.__user_dao.find_by_id(user_id)

        if not user:
            raise NoResultFound("Не удалось найти пользователя!")

        await self.__user_dao.delete(user_id)
        return user
