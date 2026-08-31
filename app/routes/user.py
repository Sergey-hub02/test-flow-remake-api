from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from typing import Annotated

from app.dependencies import get_user_service
from app.models.user import UserPost, UserGet
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
