from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm.decl_api import declarative_base

Base = declarative_base()

from .plugin_models import PluginsCfg, PyPluginsCfg
from .user_models import PyUserPerm, UserPerm


async def init(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def dele(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
