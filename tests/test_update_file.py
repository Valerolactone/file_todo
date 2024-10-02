from unittest.mock import AsyncMock, MagicMock

from fastapi import status

from settings import settings


async def test_update_file_success(
    async_client,
    mock_file_dal,
    mock_s3_client,
    mock_redis_client,
    mock_file,
):
    mock_s3_client.upload_fileobj = AsyncMock()

    response = await async_client.put(
        "/update_file",
        files={"file": (mock_file.filename, mock_file.file, mock_file.content_type)},
        data={"category": "project-logo", "url": "http://example.com/test_file.png"},
    )

    assert response.status_code == status.HTTP_200_OK
    mock_s3_client.upload_fileobj.assert_called_once()


async def test_update_file_invalid_category(
    async_client, mock_file_dal, mock_s3_client, mock_redis_client, mock_file
):
    response = await async_client.put(
        "/update_file",
        files={"file": (mock_file.filename, mock_file.file, mock_file.content_type)},
        data={
            "category": "invalid-category",
            "url": "http://example.com/test_file.png",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    allowed_categories = ", ".join(settings.allowed_categories)
    assert (
        response.json()["detail"]
        == f"Invalid category. Allowed categories are: {allowed_categories}."
    )


async def test_update_file_s3_upload_error(
    async_client, mock_file_dal, mock_s3_client, mock_redis_client, mock_file
):
    mock_s3_client.upload_fileobj = AsyncMock(side_effect=Exception("S3 update error"))

    response = await async_client.put(
        "/update_file",
        files={"file": (mock_file.filename, mock_file.file, mock_file.content_type)},
        data={"category": "project-logo", "url": "http://example.com/test_file.png"},
    )

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json()["detail"] == "S3 update error"
