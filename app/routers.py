from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Path,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import Url, Urls
from app.services import FileService
from databases.postgres_session import get_async_session

file_router = APIRouter()


@file_router.post("/upload", response_model=Url, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile,
    category: str = Form(...),
    related_id: int = Form(...),
    postgres_db: AsyncSession = Depends(get_async_session),
):
    try:
        file_service = FileService(postgres_db)
        file_url = await file_service.upload_file(
            file=file, category=category, related_id=related_id
        )
        return Url(file_url=file_url)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(err)
        )


@file_router.get(
    "/get_file_url", response_model=Urls | Url, status_code=status.HTTP_200_OK
)
async def get_file_url(
    category: str = Query(),
    related_id: int = Query(),
    postgres_db: AsyncSession = Depends(get_async_session),
):
    try:
        file_service = FileService(postgres_db)
        if category == "task-attachment":
            files_urls = await file_service.get_task_attachments(
                category=category, related_id=related_id
            )
            return Urls(urls=files_urls)
        else:
            file_url = await file_service.get_file_url(
                category=category, related_id=related_id
            )
            return Url(file_url=file_url)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@file_router.put("/update_file", status_code=status.HTTP_200_OK)
async def update_file(
    file: UploadFile,
    category: str = Form(...),
    url: str = Form(...),
    postgres_db: AsyncSession = Depends(get_async_session),
):
    try:
        file_service = FileService(postgres_db)
        return await file_service.update_file(file=file, category=category, url=url)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(err)
        )


@file_router.delete("/delete_file", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    category: str = Query(),
    url: str = Query(),
    postgres_db: AsyncSession = Depends(get_async_session),
):
    try:
        file_service = FileService(postgres_db)
        return await file_service.delete_file(category=category, url=url)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(err)
        )
