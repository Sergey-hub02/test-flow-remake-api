from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Query,
    Response,
    Path,
    UploadFile,
)
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from pydantic import AfterValidator

from typing import Annotated
from uuid import UUID

from app.dependencies import get_user_service, get_current_user

from app.models.user import UserPost, UserGet, UserFilter, UserPut
from app.models.auth import TokenPayload

from app.services.user import UserService
from app.utils import check_image

router = APIRouter(tags=["users"])


@router.post("", response_model=UserGet)
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


@router.get("", response_model=list[UserGet])
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


@router.get("/me", response_model=UserGet)
async def get_me_user(
    user_service: Annotated[UserService, Depends(get_user_service)],
    user: Annotated[TokenPayload, Depends(get_current_user)],
) -> UserGet:
    try:
        user = await user_service.get_one(user.id)
        return UserGet.model_validate(user)
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail=str(e))
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
    user: Annotated[TokenPayload, Depends(get_current_user)],
) -> UserGet:
    if user.id != user_id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещён!")

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


@router.patch("/{user_id}/photo", response_model=UserGet)
async def upload_photo(
    user_id: Annotated[UUID, Path()],
    photo: Annotated[UploadFile, AfterValidator(check_image)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    user: Annotated[TokenPayload, Depends(get_current_user)],
) -> UserGet:
    if user.id != user_id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещён!")

    try:
        updated_user = await user_service.update_photo(
            user_id=user_id, photo=photo
        )

        return UserGet.model_validate(updated_user)
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(status_code=500, detail="Ошибка при запросе к БД!")


@router.delete("/{user_id}", response_model=UserGet)
async def delete_user(
    user_id: Annotated[UUID, Path()],
    user_service: Annotated[UserService, Depends(get_user_service)],
    user: Annotated[TokenPayload, Depends(get_current_user)],
) -> UserGet:
    if user.id != user_id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещён!")

    try:
        deleted_user = await user_service.remove(user_id)
        return UserGet.model_validate(deleted_user)
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(status_code=500, detail="Ошибка при запросе к БД!")
