from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent, MetaEvent
from nonebot.exception import IgnoredException
from nonebot.log import logger
from nonebot.message import event_preprocessor
from nonebot.params import State
from nonebot.plugin.plugin import plugins
from nonebot.typing import T_State

from .. import all_cfg
from ..methods import init_plugins_to_db
from . import AEngine, ASession, flag, hook

driver = get_driver()
is_init = False


@event_preprocessor
async def _(bot: Bot, event: Event, state: T_State = State()):
    """忽略掉初始化完成之前的事件"""
    global is_init
    if not is_init and not isinstance(event, MetaEvent):
        logger.warning(f"插件数据库初始化未完成 , 事件 {event} 被忽略")
        raise IgnoredException("插件数据库初始化未完成")


async def init_db():
    """
    初始化插件信息

    有配置文件的 , 配置文件会覆盖数据库

    没有配置文件的不会覆盖
    """
    plugins_name: set[str] = set(plugins.keys()) - all_cfg.basic.ignore_global_control
    async with ASession() as session:
        res = await init_plugins_to_db(flag, session, plugins_name, all_cfg.plugins)
    if res:
        logger.warning(f"有{len(res)}个配置文件未被使用,其配置文件插件名为{str(res)}")
    logger.success(f"插件信息初始化成功 , 初始化了 {len(plugins_name)} 个插件")


@driver.on_bot_connect
async def _(bot):
    global is_init
    if not is_init:
        await init_db()
        await hook.run_async_func()
        is_init = True


# temp
@event_preprocessor
async def _(bot: Bot, event: GroupMessageEvent, state: T_State = State()):
    if isinstance(event, GroupMessageEvent):
        if event.group_id == 130404690:
            raise IgnoredException("")
