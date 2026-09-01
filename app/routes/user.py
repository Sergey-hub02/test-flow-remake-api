from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Query,
    Response,
    Path,
)
from sqlalchemy.exc import NoResultFound, SQLAlchemyError

from typing import Annotated
from uuid import UUID

from app.dependencies import get_user_service
from app.models.user import UserPost, UserGet, UserFilter, UserPut
from app.services.user import UserService

router = APIRouter(tags=["users"])


@router.post("/", response_model=UserGet)
async def create_user(
    user_fields: Annotated[UserPost, Body()],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserGet:
    try:
        user = await user_service.create(user_fields)
        return UserGet.model_validate(user)
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(status_code=500, detail="Ошибка при запросе к БД!")


@router.get("/", response_model=list[UserGet])
async def get_users(
    user_filter: Annotated[UserFilter, Query()],
    user_service: Annotated[UserService, Depends(get_user_service)],
    response: Response,
) -> list[UserGet]:
    try:
        users_count, users = await user_service.get(user_filter)
        response.headers["X-Total-Count"] = str(users_count)
        return [UserGet.model_validate(user) for user in users]
    except NameError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(status_code=500, detail="Ошибка при запросе к БД!")


@router.get("/{user_id}", response_model=UserGet)
async def get_user(
    user_id: Annotated[UUID, Path()],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserGet:
    try:
        user = await user_service.get_one(user_id)
        return UserGet.model_validate(user)
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(status_code=500, detail="Ошибка при запросе к БД!")


@router.put("/{user_id}", response_model=UserGet)
async def update_user(
    user_id: Annotated[UUID, Path()],
    user_fields: Annotated[UserPut, Body()],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserGet:
    try:
        updated_user = await user_service.update(user_id, user_fields)
        return UserGet.model_validate(updated_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(status_code=500, detail="Ошибка при запросе к БД!")


@router.delete("/{user_id}", response_model=UserGet)
async def delete_user(
    user_id: Annotated[UUID, Path()],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserGet:
    try:
        deleted_user = await user_service.remove(user_id)
        return UserGet.model_validate(deleted_user)
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(status_code=500, detail="Ошибка при запросе к БД!")
