from nonebot import get_driver
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .config import DBSettings

_driver = get_driver()
_conf = DBSettings(**_driver.config.dict())
Base = declarative_base()

AEngine: AsyncEngine = None
ASession: sessionmaker = None

_link = ""
if not _conf.db_link:
    _link = "postgresql+asyncpg://{}:{}@{}/{}".format(
        _conf.db_user, _conf.db_passwd, _conf.db_addr, _conf.db_name
    )
else:
    _link = _conf.db_link

AEngine = create_async_engine(_link, pool_recycle=3600, echo=_conf.debug, future=True,)
ASession = sessionmaker(AEngine, expire_on_commit=False, class_=AsyncSession)

from .global_models import *


@_driver.on_startup
async def _():
    async with AEngine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

