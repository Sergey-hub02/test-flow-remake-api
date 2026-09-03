from fastapi import UploadFile
from minio import Minio


class S3DAO:
    __minio: Minio
    __photo_bucket: str = "photo"

    def __init__(self, minio: Minio):
        self.__minio = minio

    async def upload_photo(self, photo: UploadFile) -> None:
        self.__minio.put_object(
            self.__photo_bucket,
            str(photo.filename),
            photo.file,
            length=photo.size if photo.size is not None else 0,
            content_type=str(photo.content_type),
            metadata={"filename": str(photo.filename)},
        )
