from pydantic import BaseSettings, validator
from pydantic.typing import NoneType


class CoolenConf(BaseSettings):
    coolen_time_reply: int

    class Config:
        extra = "ignore"
