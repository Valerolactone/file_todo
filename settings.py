from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    aws_s3_endpoint: str = Field(..., env="AWS_S3_ENDPOINT")
    aws_access_key: str = Field(..., env="AWS_ACCESS_KEY")
    aws_secret_key: str = Field(..., env="AWS_SECRET_KEY")
    aws_region: str = Field(..., env="AWS_REGION")
    link_expiration_time: int = Field(..., env="LINK_EXPIRATION_TIME")

    db_user: str = Field(..., env="DB_USER")
    db_password: str = Field(..., env="DB_PASSWORD")
    db_name: str = Field(..., env="DB_NAME")
    db_port: int = Field(..., env="DB_PORT")
    db_host: str = Field(..., env="DB_HOST")

    redis_host: str = Field("file_todo_redis", env="REDIS_HOST")
    redis_port: int = Field(..., env="REDIS_PORT")

    debug: bool = Field(False, env="DEBUG")

    allowed_categories: set[str] = Field(
        {"user_photo", "project_logo", "task_attachment"}, env="ALLOWED_CATEGORIES"
    )

    model_config = SettingsConfigDict(env_file="./.env")


settings = Settings()
