from fastapi import APIRouter, Path, Depends
from fastapi.responses import RedirectResponse

from typing import Annotated

from app.dao.s3 import S3DAO
from app.dependencies import get_s3_dao

router = APIRouter(tags=["storage"])


# noinspection PathParameterInspection
@router.get("/{bucket_name}/{object_name:path}", response_class=RedirectResponse)
def download_file(
    bucket_name: Annotated[str, Path()],
    object_name: Annotated[str, Path()],
    s3_dao: Annotated[S3DAO, Depends(get_s3_dao)],
) -> str:
    return s3_dao.get(bucket=bucket_name, object_name=object_name)
