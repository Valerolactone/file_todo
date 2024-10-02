import io
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest
from fastapi import UploadFile
from httpx import ASGITransport, AsyncClient

from databases.redis_client import redis_client
from databases.s3_client import s3_client
from main import app


@pytest.fixture
async def mock_s3_client():
    mock_client = AsyncMock()

    with patch.object(
        s3_client, 'init_s3_client', new_callable=AsyncMock
    ) as mock_init, patch.object(
        s3_client, 'close_s3_client', new_callable=AsyncMock
    ) as mock_close, patch.object(
        s3_client, 'get_s3_client', new_callable=AsyncMock
    ) as mock_get_s3:
        mock_get_s3.return_value = mock_client

        await s3_client.init_s3_client()

        yield mock_client

        await s3_client.close_s3_client()

        mock_init.assert_called_once()
        mock_close.assert_called_once()


@pytest.fixture
async def mock_s3_bucket(mock_s3_client):
    mock_s3_client.create_bucket.return_value = {
        "ResponseMetadata": {"HTTPStatusCode": 200}
    }

    mock_s3_client.head_bucket.return_value = {
        "ResponseMetadata": {"HTTPStatusCode": 200}
    }

    mock_s3_client.delete_object.return_value = {
        "ResponseMetadata": {"HTTPStatusCode": 204}
    }

    await mock_s3_client.create_bucket(Bucket="todo-project-logo-bucket")
    await mock_s3_client.create_bucket(Bucket="todo-user-photo-bucket")
    await mock_s3_client.create_bucket(Bucket="todo-task-attachment-bucket")

    expected_calls = [
        call(Bucket="todo-project-logo-bucket"),
        call(Bucket="todo-user-photo-bucket"),
        call(Bucket="todo-task-attachment-bucket"),
    ]

    mock_s3_client.create_bucket.assert_has_calls(expected_calls)


@pytest.fixture
def mock_postgres_session(mocker):
    return mocker.patch(
        "databases.postgres_session.get_async_session", new_callable=AsyncMock
    )


@pytest.fixture
def mock_file_dal(mocker):
    mock_file_dal = mocker.patch("app.services.FileDAL", autospec=True)
    return mock_file_dal.return_value


@pytest.fixture
async def mock_redis_client():
    mock_client = AsyncMock()

    with patch.object(
        redis_client, 'init_redis', new_callable=AsyncMock
    ) as mock_init, patch.object(
        redis_client, 'close_redis', new_callable=AsyncMock
    ) as mock_close, patch.object(
        redis_client, 'get_redis', new_callable=AsyncMock
    ) as mock_get_redis:
        mock_get_redis.return_value = mock_client

        await redis_client.init_redis()

        yield mock_client

        await redis_client.close_redis()

        mock_init.assert_called_once()
        mock_close.assert_called_once()


@pytest.fixture
def mock_file():
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test.png"
    mock_file.content_type = "image/png"
    mock_file.file = io.BytesIO(b"mock file content")
    return mock_file


@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
