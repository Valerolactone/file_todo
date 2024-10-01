from pydantic import BaseModel, ConfigDict


class TunedModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Urls(TunedModel):
    urls: list[str]


class Url(TunedModel):
    file_url: str


class DeleteFile(BaseModel):
    category: str
    url: str
