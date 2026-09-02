from pwdlib import PasswordHash
from sqlalchemy.exc import NoResultFound

from app.dao.user import UserDAO
from app.dao.session import SessionDAO

from app.models.auth import Token, TokenPayload, NewPasswordFields
from app.db.tables import User

from app.utils import (
    generate_jwt,
    decode_jwt,
    generate_random_code,
    UnmatchingPasswordsError,
    OldPasswordError,
    ExpiredOnetimeCodeError,
)

from app.config import settings


class AuthService:
    __user_dao: UserDAO
    __session_dao: SessionDAO
    __hasher: PasswordHash = PasswordHash.recommended()

    def __init__(self, user_dao: UserDAO, session_dao: SessionDAO):
        self.__user_dao = user_dao
        self.__session_dao = session_dao

    async def __generate_tokens(
        self, payload: TokenPayload
    ) -> tuple[Token, Token]:
        access_token = generate_jwt(type="access", payload=payload)
        refresh_token = generate_jwt(type="refresh", payload=payload)

        await self.__session_dao.whitelist(access_token)
        await self.__session_dao.add_refresh(refresh_token)

        return access_token, refresh_token

    async def login(
        self, email: str, password: str, user_agent: str
    ) -> tuple[str, str]:
        user = await self.__user_dao.find_by_email(email)

        if not user or not self.__hasher.verify(password, user.password):
            raise PermissionError("Неправильный email или пароль!")

        payload = TokenPayload(
            id=user.id,
            email=user.email,
            role=user.role.code,
            user_agent=user_agent,
        )
        access_token, refresh_token = await self.__generate_tokens(payload)

        return access_token.content, refresh_token.content

    async def refresh(self, refresh_token: str) -> tuple[str, str]:
        payload = decode_jwt(type="refresh", token=refresh_token)

        if not await self.__session_dao.get_refresh(
            user_id=payload.id, user_agent=payload.user_agent
        ):
            raise PermissionError("Не удалось определить обладателя токена!")

        await self.__session_dao.del_refresh(
            user_id=payload.id, user_agent=payload.user_agent
        )

        new_access_token, new_refresh_token = await self.__generate_tokens(
            payload
        )
        return new_access_token.content, new_refresh_token.content

    async def generate_onetime_code(self, email: str) -> str:
        user = await self.__user_dao.find_by_email(email)

        if not user:
            raise NoResultFound(
                "Не удалось найти пользователя по указанному email!"
            )

        onetime_code = generate_random_code(settings.ONETIME_CODE_LENGTH)

        await self.__session_dao.add_onetime_code(
            user_id=user.id,
            code=onetime_code,
            duration=settings.ONETIME_CODE_DURATION,
        )

        return onetime_code

    async def change_user_password(
        self, onetime_code: str, password_fields: NewPasswordFields
    ) -> User:
        user_id = await self.__session_dao.get_user_onetime_code(onetime_code)

        if not user_id:
            raise ExpiredOnetimeCodeError(
                "Неправильная ссылка или её срок действия истёк!"
            )

        user = await self.__user_dao.find_by_id(user_id)

        if not user:
            raise NoResultFound("Не удалось найти пользователя!")

        if password_fields.password != password_fields.repeated_password:
            raise UnmatchingPasswordsError("Пароли не совпадают!")

        if self.__hasher.verify(password_fields.password, user.password):
            raise OldPasswordError("Пароль совпадает с текущим!")

        updated_user = await self.__user_dao.update_password(
            user_id=user.id,
            password=self.__hasher.hash(password_fields.password),
        )
        await self.__session_dao.del_onetime_code(onetime_code)

        return updated_user
