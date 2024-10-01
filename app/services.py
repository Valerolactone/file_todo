import json
import uuid
from urllib.parse import urlparse

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from databases.dals import FileDAL
from databases.models import File
from databases.redis_client import redis_client
from databases.s3_client import S3Client
from settings import settings


class FileService:
    def __init__(self, db_session: AsyncSession):
        self.s3_client = S3Client
        self.file_dal = FileDAL(db_session)

    def _validate_category(self, category: str):
        if category not in settings.allowed_categories:
            allowed_categories = ", ".join(settings.allowed_categories)
            raise ValueError(
                f"Invalid category. Allowed categories are: {allowed_categories}."
            )

    def _get_bucket_name(self, category: str) -> str:
        return f"TODO-{category}-bucket"

    async def _ensure_bucket_exists(self, bucket_name: str):
        try:
            await self.s3_client.head_bucket(Bucket=bucket_name)
        except self.s3_client.exceptions.NoSuchBucket:
            await self.s3_client.create_bucket(Bucket=bucket_name)

    async def _generate_presigned_url(
        self,
        bucket_name: str,
        file_key: str,
        expiration: int = settings.link_expiration_time,
    ) -> str:
        url = await self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": file_key},
            ExpiresIn=expiration,
        )
        return url

    def _extract_file_key_from_url(self, url: str) -> str:
        parsed_url = urlparse(url)
        file_key = parsed_url.path.split("/")[-1]
        return file_key

    async def _get_related_files(self, category: str, related_id: int) -> list[File]:
        self._validate_category(category)

        files = await self.file_dal.get_files_by_related_type_and_id(
            related_type=category, related_id=related_id
        )
        if files is None:
            raise ValueError("No file found.")

        return files

    async def upload_file(
        self, file: UploadFile, category: str, related_id: int
    ) -> str:
        self._validate_category(category)
        bucket_name = self._get_bucket_name(category)

        await self._ensure_bucket_exists(bucket_name)

        file_key = str(uuid.uuid4())
        try:
            await self.s3_client.upload_fileobj(file.file, bucket_name, file_key)
        except Exception as e:
            raise ValueError(f"Failed to upload file to S3: {str(e)}")

        new_file = await self.file_dal.create_file(
            file_key=file_key, related_type=category, related_id=related_id
        )

        file_url = await self._generate_presigned_url(bucket_name, file_key)
        redis = await redis_client.get_redis()

        combined_key = (
            f"{category}:{related_id}:{new_file.file_pk}"
            if category == "task_attachment"
            else f"{category}:{related_id}"
        )
        await redis.set(
            combined_key, json.dumps(file_url), ex=settings.link_expiration_time
        )
        return file_url

    async def get_task_attachments(self, related_id: int, category: str) -> list[str]:
        files = await self._get_related_files(category=category, related_id=related_id)
        bucket_name = self._get_bucket_name(category)
        redis = await redis_client.get_redis()

        cached_data = []
        for file in files:
            combined_key = f"{category}:{related_id}:{file.file_pk}"
            cached_attachment = await redis.get(combined_key)
            if not cached_attachment:
                file_url = await self._generate_presigned_url(
                    bucket_name, file.file_key
                )
                await redis.set(
                    combined_key,
                    json.dumps(file_url),
                    ex=settings.link_expiration_time,
                )
                cached_data.append(file_url)
            cached_data.append(json.loads(cached_attachment))

        return cached_data

    async def get_file_url(self, category: str, related_id: int) -> str:
        redis = await redis_client.get_redis()

        combined_key = f"{category}:{related_id}"
        cached_data = await redis.get(combined_key)
        if cached_data:
            return json.loads(cached_data)

        file = await self._get_related_files(category=category, related_id=related_id)
        bucket_name = self._get_bucket_name(category)
        file_url = await self._generate_presigned_url(bucket_name, file[0].file_key)

        await redis.set(
            combined_key, json.dumps(file_url), ex=settings.link_expiration_time
        )

        return file_url

    async def update_file(self, file: UploadFile, category: str, url: str):
        self._validate_category(category)
        bucket_name = self._get_bucket_name(category)
        file_key = self._extract_file_key_from_url(url)

        await self.s3_client.upload_fileobj(file.file, bucket_name, file_key)

    async def delete_file(self, category: str, url: str):
        self._validate_category(category)
        bucket_name = self._get_bucket_name(category)
        file_key = self._extract_file_key_from_url(url)

        await self.s3_client.delete_object(Bucket=bucket_name, Key=file_key)
        await self.file_dal.delete_file(file_key)

        redis = await redis_client.get_redis()
        file = await self.file_dal.get_file_by_file_key(file_key)
        combined_key = (
            f"{category}:{file.related_id}:{file.file_pk}"
            if category == "task_attachment"
            else f"{category}:{file.related_id}"
        )
        await redis.delete(combined_key)
