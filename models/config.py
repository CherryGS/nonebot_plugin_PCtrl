from pydantic import BaseSettings


class DBSettings(BaseSettings):

    db_addr: str
    db_name: str
    db_user: str
    db_passwd: str
    db_link: str = "sqlite+aiosqlite:///_my_plugins.db"
    debug: bool

    class Config:
        extra = "ignore"

