import jwt
import secrets
import string

from fastapi import UploadFile
from datetime import datetime, timedelta
from uuid import uuid4, UUID

from app.models.auth import Token, TokenPayload, JWTType
from app.config import settings


class ExpiredOnetimeCodeError(Exception):
    pass


class UnmatchingPasswordsError(Exception):
    pass


class OldPasswordError(Exception):
    pass


class MatchingEmailError(Exception):
    pass


def generate_jwt(type: JWTType, payload: TokenPayload) -> Token:
    secret = settings.ACCESS_PK if type == "access" else settings.REFRESH_PK
    exp_time = datetime.now() + (
        timedelta(minutes=15) if type == "access" else timedelta(weeks=4)
    )
    issued_at = datetime.now()
    jwt_id = uuid4()

    token_data = payload.model_dump()

    for k, v in token_data.items():
        if isinstance(v, UUID):
            token_data[k] = str(v)

    token_data["exp"] = exp_time
    token_data["iat"] = issued_at
    token_data["jti"] = str(jwt_id)

    content = jwt.encode(token_data, key=secret, algorithm=settings.ENC_ALGO)

    return Token(
        type=type,
        content=content,
        jti=jwt_id,
        exp=int(exp_time.timestamp()),
        iat=int(issued_at.timestamp()),
        payload=payload,
    )


def decode_jwt(type: JWTType, token: str) -> TokenPayload:
    secret = settings.ACCESS_PK if type == "access" else settings.REFRESH_PK
    payload = jwt.decode(token, key=secret, algorithms=[settings.ENC_ALGO])

    return TokenPayload(
        id=UUID(payload["id"]),
        email=payload["email"],
        role=payload["role"],
        user_agent=payload["user_agent"],
    )


def generate_random_code(length: int) -> str:
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


def check_image(image: UploadFile) -> UploadFile:
    size = image.size if image.size is not None else 0
    content_type = image.content_type if image.content_type is not None else ""

    if not content_type.startswith("image/"):
        raise ValueError("Файл должен быть изображением!")

    if size > settings.MAX_IMAGE_FILE_SIZE:
        raise ValueError(
            f"Размер файла не должен превышать {settings.MAX_IMAGE_FILE_SIZE / 1024**2} МБ!"
        )

    return image
