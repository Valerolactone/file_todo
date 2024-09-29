from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import Urls
from app.services import FileService
from databases.postgres_session import get_async_session

file_router = APIRouter()


@file_router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile,
    category: str,
    related_id: int,
    postgres_db: AsyncSession = Depends(get_async_session),
):
    try:
        file_service = FileService(postgres_db)
        return await file_service.upload_file(
            file=file, category=category, related_id=related_id
        )
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@file_router.get("/get_file_url", response_model=Urls, status_code=status.HTTP_200_OK)
async def get_file_url(
    category: str,
    related_id: int,
    postgres_db: AsyncSession = Depends(get_async_session),
):
    try:
        file_service = FileService(postgres_db)
        return await file_service.get_file_urls(
            category=category, related_id=related_id
        )
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@file_router.put("/update_file", status_code=status.HTTP_200_OK)
async def update_file(
    file: UploadFile,
    category: str,
    url: str,
    postgres_db: AsyncSession = Depends(get_async_session),
):
    try:
        file_service = FileService(postgres_db)
        return await file_service.update_file(file=file, category=category, url=url)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@file_router.delete("/delete_file", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    category: str, url: str, postgres_db: AsyncSession = Depends(get_async_session)
):
    try:
        file_service = FileService(postgres_db)
        return await file_service.delete_file(category=category, url=url)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
