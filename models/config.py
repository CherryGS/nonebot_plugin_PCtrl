from pydantic import BaseSettings

__all__ = []


class DBSettings(BaseSettings):

    plugin_pctrl_db: str = "sqlite+aiosqlite:///_my_admin.db"
    debug: bool = False

    class Config:
        extra = "ignore"
