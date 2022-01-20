from typing import List

from anyutils import HookMaker
from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent, MetaEvent
from nonebot.exception import IgnoredException
from nonebot.log import logger
from nonebot.message import event_preprocessor
from nonebot.params import State
from nonebot.plugin import export
from nonebot.plugin.plugin import plugins
from nonebot.typing import T_State

from .config import PluginCfg, conf, default_perm, gbname, my
from .method import *

driver = get_driver()
is_init = False

export = export()
export.ignore_global_control = True

post_db_init = HookMaker("数据库初始化后")


@event_preprocessor
async def _(bot: Bot, event: Event, state: T_State = State()):
    """忽略掉初始化完成之前的事件"""
    global is_init
    if not is_init and not isinstance(event, MetaEvent):
        logger.warning("插件数据库初始化未完成 , 事件 {} 被忽略".format(event))
        raise IgnoredException("")


async def init_db():
    """
    初始化插件信息

    有配置文件的 , 配置文件会覆盖数据库

    没有配置文件的不会覆盖
    """
    cfg = await load_config()
    now1 = dict()
    now2 = dict()
    for i in plugins.keys():
        if i not in cfg:
            now2[i] = PluginCfg()
        elif cfg[i].ignore_global_control == False:
            now1[i] = cfg[i]

    await del_left_plugin(set(now1.keys()) | set(now2.keys()))

    for i in now1.keys():
        now1[i] = PyPluginsCfg(**now1[i].dict(), plugin_name=i)
    for i in now2.keys():
        now2[i] = PyPluginsCfg(**now2[i].dict(), plugin_name=i)
    await init_plugins(set(now1.values()))
    await init_plugins(set(now2.values()), False)
    logger.success(
        "插件信息初始化成功 , 初始化了 {} 个插件".format(len(now1.values()) + len(now2.values()))
    )


@driver.on_bot_connect
async def _(bot):
    global is_init
    if not is_init:
        await init_db()
        await post_db_init.run_hook()
        is_init = True
        await clean_perms()


from .plugin import *


# temp
@event_preprocessor
async def _(bot: Bot, event: GroupMessageEvent, state: T_State = State()):
    if isinstance(event, GroupMessageEvent):
        if event.group_id == 130404690:
            raise IgnoredException("")
