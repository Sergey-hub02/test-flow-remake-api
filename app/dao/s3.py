from fastapi import UploadFile
from minio import Minio


class S3DAO:
    __minio: Minio

    def __init__(self, minio: Minio):
        self.__minio = minio

    def upload(self, bucket: str, file: UploadFile) -> None:
        self.__minio.put_object(
            bucket_name=bucket,
            object_name=str(file.filename),
            data=file.file,
            length=file.size if file.size is not None else 0,
            content_type=str(file.content_type),
        )

    def get(self, bucket: str, object_name: str):
        return self.__minio.presigned_get_object(
            bucket_name=bucket,
            object_name=object_name,
        )
