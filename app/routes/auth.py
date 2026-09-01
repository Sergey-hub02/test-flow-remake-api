from fastapi import APIRouter, Depends, Header, HTTPException, Path
from fastapi.security import OAuth2PasswordRequestForm

from typing import Annotated
from sqlalchemy.exc import SQLAlchemyError

from app.services.auth import AuthService
from app.dependencies import get_auth_service

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
