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
from app.services.mail import MailService

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


def get_minio_client() -> Minio:
    return Minio(
        endpoint=f"{settings.MINIO_HOST}:{settings.MINIO_S3_PORT}",
        access_key=settings.MINIO_ROOT_USER,
        secret_key=settings.MINIO_ROOT_PASSWORD,
        secure=False,
    )


def get_role_dao(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> RoleDAO:
    return RoleDAO(db)


def get_user_dao(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserDAO:
    return UserDAO(db)


def get_session_dao(
    redis: Annotated[Redis, Depends(get_redis_client)],
) -> SessionDAO:
    return SessionDAO(redis)


def get_s3_dao(
    minio_client: Annotated[Minio, Depends(get_minio_client)],
) -> S3DAO:
    return S3DAO(minio_client)


def get_user_service(
    role_dao: Annotated[RoleDAO, Depends(get_role_dao)],
    user_dao: Annotated[UserDAO, Depends(get_user_dao)],
    s3_dao: Annotated[S3DAO, Depends(get_s3_dao)],
) -> UserService:
    return UserService(role_dao=role_dao, user_dao=user_dao, s3_dao=s3_dao)


def get_auth_service(
    user_dao: Annotated[UserDAO, Depends(get_user_dao)],
    session_dao: Annotated[SessionDAO, Depends(get_session_dao)],
) -> AuthService:
    return AuthService(user_dao=user_dao, session_dao=session_dao)


def get_current_user(
    access_token: Annotated[str, Depends(oauth2_scheme)],
) -> TokenPayload:
    try:
        # TODO: добавить проверку токена в whitelist'е
        return decode_jwt(type="access", token=access_token).payload
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


def get_mail_client() -> FastMail:
    return FastMail(mail_settings)


def get_mail_service(
    mail_client: Annotated[FastMail, Depends(get_mail_client)],
) -> MailService:
    return MailService(mail_client)
