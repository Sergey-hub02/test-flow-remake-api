from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Path,
    Body,
    BackgroundTasks,
)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_mail import FastMail, MessageSchema, MessageType, NameEmail

from typing import Annotated
from urllib.parse import urlunparse

from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from pydantic import EmailStr
from redis import RedisError

from app.services.auth import AuthService, NewPasswordFields, NewEmailFields
from app.services.user import UserService

from app.models.user import UserPost, UserGet
from app.models.auth import TokenPayload

from app.dependencies import (
    get_auth_service,
    get_user_service,
    get_current_user,
    get_mail_client,
)

from app.utils import (
    ExpiredOnetimeCodeError,
    UnmatchingPasswordsError,
    OldPasswordError,
    MatchingEmailError,
)

from app.config import settings

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

        # TODO: отправка сообщения на почту

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

        # TODO: отправка сообщения на почту

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
    mail_client: Annotated[FastMail, Depends(get_mail_client)],
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    try:
        onetime_code = await auth_service.generate_onetime_code(email)

        template_params = {
            "email": email,
            "reset_url": urlunparse(
                (
                    "http",
                    f"{settings.FRONT_HOST}:{settings.FRONT_PORT}",
                    "/auth/change_password",
                    "",
                    f"onetime_code={onetime_code}",
                    "",
                )
            ),
        }

        message = MessageSchema(
            subject="TestFlow: Сброс пароля",
            recipients=[NameEmail("", email)],
            template_body=template_params,
            subtype=MessageType.html,
        )

        background_tasks.add_task(
            mail_client.send_message, message, template_name="onetime_code.html"
        )

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

        # TODO: отправка сообщения на почту

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


@router.patch("/change_email", response_model=UserGet)
async def change_email(
    email_fields: Annotated[NewEmailFields, Body()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    user: Annotated[TokenPayload, Depends(get_current_user)],
) -> UserGet:
    try:
        updated_user = await auth_service.change_user_email(
            user_id=user.id, email_fields=email_fields
        )

        # TODO: отправка сообщения на почту

        return UserGet.model_validate(updated_user)
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UnmatchingPasswordsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except MatchingEmailError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(status_code=500, detail="Ошибка при запросе к БД!")
    except RedisError as e:
        print(e)
        raise HTTPException(
            status_code=500, detail="Ошибка при запросе к Redis!"
        )
