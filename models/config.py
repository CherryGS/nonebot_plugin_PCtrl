from typing import Optional
from pydantic import BaseSettings
from sqlalchemy.ext.asyncio.engine import AsyncEngine

__all__ = []


class DBSettings(BaseSettings):

    plugin_pctrl_db: str = ""
    debug: bool = False
    AEngine: Optional[AsyncEngine] = None

    class Config:
        extra = "ignore"
