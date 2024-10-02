import json
from unittest.mock import MagicMock

from fastapi import status

from settings import settings


async def test_get_task_attachments(
    async_client, mock_file_dal, mock_s3_client, mock_redis_client, mock_s3_bucket
):
    mock_file_dal.get_files_by_related_type_and_id.return_value = [
        MagicMock(file_key='file_key_1', file_pk=1)
    ]
    mock_redis_client.get.return_value = None
    mock_s3_client.generate_presigned_url.return_value = "presigned_url_1"

    response = await async_client.get(
        "/get_file_url", params={"category": "task-attachment", "related_id": 1}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"urls": ["presigned_url_1"]}

    combined_key = "task-attachment:1:1"
    mock_redis_client.set.assert_called_once_with(
        combined_key, json.dumps("presigned_url_1"), ex=settings.link_expiration_time
    )


async def test_get_single_file_url(
    async_client, mock_file_dal, mock_s3_client, mock_redis_client, mock_s3_bucket
):
    mock_file_dal.get_files_by_related_type_and_id.return_value = [
        MagicMock(file_key='file_key_1', file_pk=1)
    ]
    mock_redis_client.get.return_value = None
    mock_s3_client.generate_presigned_url.return_value = "presigned_url_1"

    response = await async_client.get(
        "/get_file_url", params={"category": "project-logo", "related_id": 1}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"file_url": "presigned_url_1"}

    combined_key = "project-logo:1"
    mock_redis_client.set.assert_called_once_with(
        combined_key, json.dumps("presigned_url_1"), ex=settings.link_expiration_time
    )


async def test_get_file_url_invalid_category(async_client):
    response = await async_client.get(
        "/get_file_url", params={"category": "invalid-category", "related_id": 1}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    allowed_categories = ", ".join(settings.allowed_categories)
    assert (
        response.json()["detail"]
        == f"Invalid category. Allowed categories are: {allowed_categories}."
    )


async def test_get_file_url_no_file_found(async_client, mock_file_dal):
    mock_file_dal.get_files_by_related_type_and_id.side_effect = ValueError(
        "No file found."
    )

    response = await async_client.get(
        "/get_file_url", params={"category": "task-attachment", "related_id": 1}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "No file found."
