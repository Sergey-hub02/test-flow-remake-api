from redis.asyncio import Redis
from uuid import UUID

from app.models.auth import Token


class SessionDAO:
    __WL_PREFIX: str = "whitelist"
    __REFRESH_PREFIX: str = "refresh"

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
