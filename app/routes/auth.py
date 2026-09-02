from fastapi import APIRouter, Depends, Header, HTTPException, Path, Body
from fastapi.security import OAuth2PasswordRequestForm

from typing import Annotated
from sqlalchemy.exc import SQLAlchemyError, NoResultFound

from app.services.auth import AuthService
from app.services.user import UserService
from app.models.user import UserPost
from app.dependencies import get_auth_service, get_user_service

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
