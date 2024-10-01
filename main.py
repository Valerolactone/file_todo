import uvicorn
from fastapi import APIRouter, FastAPI

from app.routers import file_router
from databases.redis_client import redis_client
from databases.s3_client import s3_client

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    await s3_client.init_s3_client()
    await redis_client.init_redis()


@app.on_event("shutdown")
async def shutdown_event():
    await s3_client.close_s3_client()
    await redis_client.close_redis()


main_api_router = APIRouter()

main_api_router.include_router(file_router, tags=["file"])
app.include_router(main_api_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
