from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi_mail import FastMail

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from redis.asyncio import Redis
from minio import Minio
from jwt import ExpiredSignatureError, DecodeError, PyJWTError

from app.db.conexion import AsyncSessionLocal

from app.dao.role import RoleDAO
from app.dao.user import UserDAO
from app.dao.session import SessionDAO
from app.dao.s3 import S3DAO

from app.models.auth import TokenPayload

from app.services.user import UserService
from app.services.auth import AuthService

from app.config import settings, mail_settings
from app.utils import decode_jwt

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login", refreshUrl="/api/v1/auth/refresh"
)


async def get_db_session():
    async with AsyncSessionLocal() as db:
        yield db


async def get_redis_client():
    async with Redis.from_url(settings.REDIS_URL) as redis_client:
        yield redis_client


async def get_minio_client() -> Minio:
    return Minio(
        endpoint=f"{settings.MINIO_HOST}:{settings.MINIO_S3_PORT}",
        access_key=settings.MINIO_ROOT_USER,
        secret_key=settings.MINIO_ROOT_PASSWORD,
        secure=False,
    )


async def get_user_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    minio_client: Annotated[Minio, Depends(get_minio_client)],
) -> UserService:
    role_dao = RoleDAO(db)
    user_dao = UserDAO(db)
    s3_dao = S3DAO(minio_client)

    return UserService(role_dao=role_dao, user_dao=user_dao, s3_dao=s3_dao)


async def get_auth_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    redis_client: Annotated[Redis, Depends(get_redis_client)],
) -> AuthService:
    user_dao = UserDAO(db)
    session_dao = SessionDAO(redis_client)

    return AuthService(user_dao=user_dao, session_dao=session_dao)


async def get_current_user(
    access_token: Annotated[str, Depends(oauth2_scheme)],
) -> TokenPayload:
    try:
        return decode_jwt(type="access", token=access_token)
    except ExpiredSignatureError as e:
        print(e)
        raise HTTPException(
            status_code=403, detail="Срок действия токена истёк!"
        )
    except DecodeError as e:
        print(e)
        raise HTTPException(status_code=403, detail="Невалидный токен!")
    except PyJWTError as e:
        print(e)
        raise HTTPException(
            status_code=403, detail="Ошибка при декодировании токена!"
        )


async def get_mail_client() -> FastMail:
    return FastMail(mail_settings)
