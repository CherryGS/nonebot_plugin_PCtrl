from pydantic import BaseSettings


class CoolenConf(BaseSettings):
    coolen_time_reply: int

    class Config:
        extra = "ignore"
