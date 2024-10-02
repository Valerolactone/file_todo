from unittest.mock import AsyncMock

from fastapi import status

from settings import settings


async def test_upload_file_success(
    async_client, mock_s3_client, mock_file_dal, mock_redis_client, mock_file
):
    mock_s3_client.upload_fileobj = AsyncMock()
    mock_s3_client.generate_presigned_url.return_value = "presigned_url_1"

    response = await async_client.post(
        "/upload",
        files={"file": (mock_file.filename, mock_file.file, mock_file.content_type)},
        data={"category": "user-photo", "related_id": 1},
    )

    assert response.status_code == status.HTTP_201_CREATED
    mock_s3_client.upload_fileobj.assert_called_once()
    mock_file_dal.create_file.assert_called_once()
    mock_redis_client.set.assert_called_once()


async def test_upload_file_invalid_category(
    async_client, mock_file_dal, mock_s3_client, mock_redis_client, mock_file
):
    response = await async_client.post(
        "/upload",
        files={"file": (mock_file.filename, mock_file.file, mock_file.content_type)},
        data={"category": "invalid-category", "related_id": 1},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    allowed_categories = ", ".join(settings.allowed_categories)
    assert (
        response.json()["detail"]
        == f"Invalid category. Allowed categories are: {allowed_categories}."
    )


async def test_upload_file_s3_error(
    async_client, mock_file_dal, mock_s3_client, mock_redis_client, mock_file
):
    mock_s3_client.upload_fileobj = AsyncMock(side_effect=Exception("S3 upload error"))

    response = await async_client.post(
        "/upload",
        files={"file": (mock_file.filename, mock_file.file, mock_file.content_type)},
        data={"category": "user-photo", "related_id": 1},
    )

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json()["detail"] == "S3 upload error"
