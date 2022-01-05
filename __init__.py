from types import new_class
from typing import List
from nonebot import get_driver
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import Event, MetaEvent
from nonebot.exception import IgnoredException
from nonebot.log import logger
from nonebot.message import event_preprocessor
from nonebot.plugin import export, plugins
from nonebot.typing import T_State
from sqlalchemy import select
from sqlalchemy.sql.expression import update
import asyncio

from .hook import db_init_finished
from .models import ASession
from .models.global_models import pluginsCfg

_driver = get_driver()
_is_init = False

_export = export()
_export.ignore_global_control = True


@event_preprocessor
async def _(bot: Bot, event: Event, state: T_State):
    """忽略掉初始化完成之前的事件(除元事件)

    Args:
        bot (Bot): [description]
        event (Event): [description]
        state (T_State): [description]

    Raises:
        IgnoredException: [description]
    """
    global _is_init
    if not _is_init and not isinstance(event, MetaEvent):
        logger.warning("插件数据库初始化未完成 , 事件 {} 被忽略".format(event))
        raise IgnoredException("")


async def init_plugins(session, now_plugins):

    db_plugins: List[pluginsCfg] = (
        await session.execute(select(pluginsCfg))
    ).scalars().all()

    num = len(db_plugins)

    for i in db_plugins:
        if i.plugin_name not in now_plugins.keys():
            num -= 1
            await session.delete(i)

    name = [_.plugin_name for _ in db_plugins]

    for i in now_plugins.keys():
        if i not in name:
            num += 1
            session.add(pluginsCfg(plugin_name=i))

    await session.commit()
    return num


async def update_coolen_time(session, np: dict):
    v_lis = []
    for i in np.items():
        if i[1].export.coolen_time:
            v_lis.append([i[0], i[1].export.coolen_time])
    t_lis = [
        session.execute(
            update(pluginsCfg)
            .where(pluginsCfg.plugin_name == i[0])
            .values(coolen_time=i[1])
        )
        for i in v_lis
    ]
    await asyncio.gather(*t_lis)


async def init_db():
    # 初始化插件信息
    now_plugins = dict()
    for i in plugins.items():
        if not i[1].export.ignore_global_control:
            now_plugins[i[0]] = i[1]
    try:
        session = ASession()
        num = await init_plugins(session, now_plugins)
        await update_coolen_time(session, now_plugins)
        await session.commit()
        logger.success("插件信息初始化成功 , 初始化了 {} 个插件".format(num))
    except:
        raise
    finally:
        await session.close()


@_driver.on_bot_connect
async def _(bot: Bot = None):
    global _is_init
    if not _is_init:
        try:
            await init_db()
            await db_init_finished.run_hook()
            _is_init = True
        except:
            raise


from .global_controller import *

# temp
@event_preprocessor
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    if isinstance(event, GroupMessageEvent):
        if event.group_id == 130404690:
            raise IgnoredException("")
