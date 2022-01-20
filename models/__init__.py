from typing import Literal
from anyutils import reg, BsModel
from nonebot import get_driver
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.decl_api import declarative_base

from .. import conf

Base = declarative_base()

driver = get_driver()

reg.add("sqlite", conf.db_link, debug=conf.debug)

AEngine = reg.get("sqlite")
flag: Literal["sqlite", "postgresql"] = AEngine.dialect.name

ASession = sessionmaker(AEngine, expire_on_commit=False, class_=AsyncSession)

from .plugin_models import PluginsCfg, PyPluginsCfg
from .user_models import PyUserPerm, UserPerm


@driver.on_startup
async def _():
    async with AEngine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
