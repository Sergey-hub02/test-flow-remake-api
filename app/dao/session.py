from redis.asyncio import Redis
from uuid import UUID

from app.models.auth import Token


class SessionDAO:
    __WL_PREFIX: str = "whitelist"
    __REFRESH_PREFIX: str = "refresh"
    __ONETIME_CODE_PREFIX: str = "onetimecode"

    __redis: Redis

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
        jti = await self.__redis.get(
            f"{self.__REFRESH_PREFIX}:{str(user_id)}:{user_agent}"
        )
        return jti.decode() if isinstance(jti, bytes) else jti

    async def del_refresh(self, user_id: UUID, user_agent: str) -> None:
        await self.__redis.delete(
            f"{self.__REFRESH_PREFIX}:{str(user_id)}:{user_agent}"
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
