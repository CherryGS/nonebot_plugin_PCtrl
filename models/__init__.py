from anyutils import RegEngine as reg
from nonebot import get_driver
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.decl_api import declarative_base

from .config import DBSettings

driver = get_driver()
conf = DBSettings(**driver.config.dict())
Base = declarative_base()

reg.add(__name__, conf.plugin_pctrl_db)

AEngine = reg.get(__name__)

ASession = sessionmaker(AEngine, expire_on_commit=False, class_=AsyncSession)

from .global_models import (
    PluginsBan,
    PluginsCfg,
    PluginsCooling,
    PyPluginsCfg,
    PyPluginsBan,
    PyPluginsCooling,
)


@driver.on_startup
async def _():
    async with AEngine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
