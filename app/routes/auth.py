from fastapi import APIRouter, Depends, Header, HTTPException, Path, Body
from fastapi.security import OAuth2PasswordRequestForm

from typing import Annotated
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from pydantic import EmailStr
from redis import RedisError

from app.services.auth import AuthService, NewPasswordFields
from app.services.user import UserService
from app.models.user import UserPost, UserGet
from app.dependencies import get_auth_service, get_user_service

from app.utils import (
    ExpiredOnetimeCodeError,
    UnmatchingPasswordsError,
    OldPasswordError,
)

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=dict[str, str])
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    user_agent: Annotated[str, Header()],
) -> dict[str, str]:
    try:
        access_token, refresh_token = await auth_service.login(
            email=form_data.username,
            password=form_data.password,
            user_agent=user_agent,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(status_code=500, detail="Ошибка при запросе к БД!")
    except RedisError as e:
        print(e)
        raise HTTPException(
            status_code=500, detail="Ошибка при запросе к Redis!"
        )


@router.post("/refresh/{refresh_token}", response_model=dict[str, str])
async def refresh(
    refresh_token: Annotated[str, Path()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> dict[str, str]:
    try:
        new_access_token, new_refresh_token = await auth_service.refresh(
            refresh_token
        )

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(status_code=500, detail="Ошибка при запросе к БД!")
    except RedisError as e:
        print(e)
        raise HTTPException(
            status_code=500, detail="Ошибка при запросе к Redis!"
        )


@router.post("/register", response_model=dict[str, str])
async def register(
    user_fields: Annotated[UserPost, Body()],
    user_service: Annotated[UserService, Depends(get_user_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    user_agent: Annotated[str, Header()],
) -> dict[str, str]:
    try:
        user = await user_service.create(user_fields)

        access_token, refresh_token = await auth_service.login(
            email=user.email,
            password=user_fields.password,
            user_agent=user_agent,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(status_code=500, detail="Ошибка при запросе к БД!")
    except RedisError as e:
        print(e)
        raise HTTPException(
            status_code=500, detail="Ошибка при запросе к Redis!"
        )


@router.post("/forgot")
async def send_onetime_code(
    email: Annotated[EmailStr, Body(embed=True)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> dict[str, str]:
    try:
        await auth_service.generate_onetime_code(email)
        # TODO: отправка кода на почту
        return {
            "message": "На указанную почту будет выслана ссылка для сброса пароля. Время действия ссылки - 2 минуты!"
        }
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(status_code=500, detail="Ошибка при запросе к БД!")
    except RedisError as e:
        print(e)
        raise HTTPException(
            status_code=500, detail="Ошибка при запросе к Redis!"
        )


@router.patch("/change_password/{onetime_code}", response_model=UserGet)
async def change_password(
    onetime_code: Annotated[str, Path()],
    password_fields: Annotated[NewPasswordFields, Body()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserGet:
    try:
        updated_user = await auth_service.change_user_password(
            onetime_code=onetime_code,
            password_fields=password_fields,
        )

        return UserGet.model_validate(updated_user)
    except ExpiredOnetimeCodeError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except UnmatchingPasswordsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except OldPasswordError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(status_code=500, detail="Ошибка при запросе к БД!")
    except RedisError as e:
        print(e)
        raise HTTPException(
            status_code=500, detail="Ошибка при запросе к Redis!"
        )
