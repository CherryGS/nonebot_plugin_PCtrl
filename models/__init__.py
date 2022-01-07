from nonebot import get_driver
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.decl_api import declarative_base
from .config import DBSettings
from nonebot.log import logger

_driver = get_driver()
_conf = DBSettings(**_driver.config.dict())

__all__ = []
Base = declarative_base()

AEngine: AsyncEngine = None

_link = "sqlite+aiosqlite:///_my_admin.db"
if not _conf.plugin_pctrl_db:
    logger.warning("未配置数据库链接 , 尝试使用 AsyncEngine")
    if not _conf.AEngine:
        logger.warning("未检测到 AsyncEngine , 使用默认数据库链接 {}".format(_link))
    else:
        AEngine = _conf.AEngine
        logger.warning("检测到传入 AsyncEngine , 使用 AsyncEngine 启动")
else:
    _link = _conf.plugin_pctrl_db
    logger.warning("检测到数据库链接 , 使用配置启动 ({})".format(_link))

if not AEngine:
    AEngine = create_async_engine(
        _link, pool_recycle=3600, echo=_conf.debug, future=True,
    )

ASession: sessionmaker = None
ASession = sessionmaker(AEngine, expire_on_commit=False, class_=AsyncSession)

from .global_models import *


@_driver.on_startup
async def _():
    async with AEngine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

