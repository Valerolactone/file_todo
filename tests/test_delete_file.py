from unittest.mock import AsyncMock, MagicMock

from fastapi import status

from settings import settings


async def test_delete_file_success(
    async_client, mock_file_dal, mock_s3_client, mock_redis_client, mock_s3_bucket
):
    mock_file_dal.get_file_by_file_key.return_value = MagicMock(file_pk=1, related_id=1)

    response = await async_client.delete(
        "/delete_file",
        params={"category": "project-logo", "url": "http://example.com/test_file.png"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_s3_client.delete_object.assert_called_once_with(
        Bucket="todo-project-logo-bucket", Key="test_file.png"
    )

    combined_key = "project-logo:1"
    mock_redis_client.delete.assert_awaited_once_with(combined_key)

    assert mock_file_dal.delete_file.called


async def test_delete_file_invalid_category(async_client):
    response = await async_client.delete(
        "/delete_file",
        params={
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


async def test_delete_file_not_found(
    async_client,
    mock_file_dal,
    mock_s3_client,
    mock_redis_client,
):
    mock_file_dal.get_file_by_file_key.return_value = None

    response = await async_client.delete(
        "/delete_file",
        params={"category": "project-logo", "url": "http://example.com/test_file.png"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "No file found."


async def test_delete_file_s3_delete_error(
    async_client, mock_file_dal, mock_s3_client, mock_redis_client
):
    mock_file_dal.get_file_by_file_key.return_value = MagicMock(file_pk=1, related_id=1)
    mock_s3_client.delete_object = AsyncMock(side_effect=Exception("S3 deletion error"))

    response = await async_client.delete(
        "/delete_file",
        params={"category": "project-logo", "url": "http://example.com/test_file.png"},
    )

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json()["detail"] == "S3 deletion error"

    mock_file_dal.delete_file.assert_not_called()
    mock_redis_client.delete.assert_not_called()
