from typing import Union

from pydantic import BaseModel, ConfigDict


class TunedModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Urls(TunedModel):
    urls: Union[str, list[str]]
