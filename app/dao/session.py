from redis.asyncio import Redis
from uuid import UUID

from app.models.auth import Token
from app.config import settings


class SessionDAO:
    __WL_PREFIX: str = "whitelist"
    __REFRESH_PREFIX: str = "refresh"
    __ONETIME_CODE_PREFIX: str = "onetimecode"
    __REFRESH_GRACE_PREFIX: str = "refresh_grace"

    __redis: Redis

    @staticmethod
    def __normalize_value(value: bytes | str | None) -> str | None:
        return value.decode() if isinstance(value, bytes) else value

    def __init__(self, redis: Redis):
        self.__redis = redis

    async def whitelist(self, token: Token) -> None:
        await self.__redis.set(
            f"{self.__WL_PREFIX}:{str(token.jti)}", value=1, exat=token.exp
        )

    async def add_refresh(self, token: Token) -> None:
        await self.__redis.set(
            f"{self.__REFRESH_PREFIX}:{str(token.payload.id)}:{token.payload.user_agent}",
            value=str(token.jti),
            exat=token.exp,
        )

    async def get_refresh(self, user_id: UUID, user_agent: str) -> str | None:
        return self.__normalize_value(
            await self.__redis.get(
                f"{self.__REFRESH_PREFIX}:{str(user_id)}:{user_agent}"
            )
        )

    async def del_refresh(self, user_id: UUID, user_agent: str) -> None:
        await self.__redis.delete(
            f"{self.__REFRESH_PREFIX}:{str(user_id)}:{user_agent}"
        )

    async def get_grace_pair(self, jti: UUID) -> str | None:
        return self.__normalize_value(
            await self.__redis.get(f"{self.__REFRESH_GRACE_PREFIX}:{jti}")
        )

    async def add_grace_pair(
        self, jti: UUID, access_token: str, refresh_token: str
    ) -> None:
        await self.__redis.set(
            f"{self.__REFRESH_GRACE_PREFIX}:{jti}",
            value=f"{access_token}:{refresh_token}",
            ex=settings.GRACE_PERIOD,
        )

    async def add_onetime_code(
        self, user_id: UUID, code: str, duration: int
    ) -> None:
        await self.__redis.set(
            f"{self.__ONETIME_CODE_PREFIX}:{code}",
            value=str(user_id),
            ex=duration,
        )

    async def get_user_onetime_code(self, code: str) -> UUID | None:
        user_id = await self.__redis.get(f"{self.__ONETIME_CODE_PREFIX}:{code}")

        return (
            UUID(user_id.decode())
            if isinstance(user_id, bytes)
            else UUID(user_id) if isinstance(user_id, str) else user_id
        )

    async def del_onetime_code(self, code: str) -> None:
        await self.__redis.delete(f"{self.__ONETIME_CODE_PREFIX}:{code}")
