from anyutils import HookMaker, reg
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from .. import conf
from ..core import get_engine_type_by_name
from ..models import init

hook = HookMaker("After init_db")
reg.add("sqlite", conf.db_link, debug=conf.debug)
AEngine = reg.get("sqlite")
ASession = sessionmaker(AEngine, expire_on_commit=False, class_=AsyncSession)
flag = get_engine_type_by_name(AEngine.dialect.name)
(init(AEngine)).send(None)

from .ban import *
from .cool import *
from .init_db import *
