from pydantic import BaseSettings


class DBSettings(BaseSettings):

    db_link: str = ""
    debug: bool

    class Config:
        extra = "ignore"

