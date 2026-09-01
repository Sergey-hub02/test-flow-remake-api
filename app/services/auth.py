from pwdlib import PasswordHash

from app.dao.user import UserDAO
from app.dao.session import SessionDAO
from app.models.auth import Token, TokenPayload
from app.utils import generate_jwt, decode_jwt


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
