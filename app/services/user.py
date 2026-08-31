from sqlalchemy import ScalarResult
from sqlalchemy.exc import NoResultFound
from pwdlib import PasswordHash

from app.dao.role import RoleDAO
from app.dao.user import UserDAO
from app.models.user import UserPost, UserFilter
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
