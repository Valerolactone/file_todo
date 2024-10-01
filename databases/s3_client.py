import aioboto3
from botocore.config import Config

from settings import settings


class S3Client:
    def __init__(self):
        self._s3_client = None

    async def init_s3_client(self):
        session = aioboto3.Session(
            aws_access_key_id=settings.aws_access_key,
            aws_secret_access_key=settings.aws_secret_key,
            region_name=settings.aws_region,
        )
        async with session.client(
            "s3",
            endpoint_url=settings.aws_s3_endpoint,
            config=Config(signature_version="s3v4"),
        ) as client:
            self._s3_client = client

    def get_s3_client(self):
        if self._s3_client is None:
            raise Exception("S3 client is not initialized.")
        return self._s3_client

    async def close_s3_client(self):
        if self._s3_client:
            await self._s3_client.close()


s3_client = S3Client()
