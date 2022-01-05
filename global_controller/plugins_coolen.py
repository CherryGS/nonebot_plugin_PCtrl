import functools
import inspect
import time
from typing import Dict, List

from nonebot.adapters.cqhttp import Bot, Event
from nonebot.exception import IgnoredException
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor
from nonebot.plugin import on_message
from nonebot.typing import T_State
from sqlalchemy import select

from ..hook import db_init_finished
from ..models import ASession
from ..models.global_models import pluginsCfg

_coolen_configs: Dict[str, int] = dict()
_coolen_now: Dict[str, int] = dict()


@db_init_finished.add_hook
async def _load_coolen_time():
    """将插件冷却信息载入内存
    """
    global _coolen
    try:
        session = ASession()
        res: List[pluginsCfg] = (
            await session.execute(select(pluginsCfg))
        ).scalars().all()
        for i in res:
            _coolen_configs[i.plugin_name] = i.coolen_time
        logger.success("插件全局冷却初始化成功")
        logger.debug(_coolen_configs)
    except:
        raise
    finally:
        await session.close()


@run_preprocessor
async def _(matcher: Matcher, bot: Bot, event: Event, state: T_State):
    """全局插件级别冷却

    Args:
        matcher (Matcher): [description]
        bot (Bot): [description]
        event (Event): [description]
        state (T_State): [description]

    Raises:
        IgnoredException: [description]
    """
    name = matcher.plugin_name
    if name not in _coolen_configs.keys() or _coolen_configs[name] == 0:
        return
    t = time.time()
    if name not in _coolen_now.keys() or _coolen_now[name] + _coolen_configs[name] <= t:
        _coolen_now[name] = t
        return
    logger.warning(
        "插件 {} 在冷却中 , 还剩 {} 秒".format(
            name, _coolen_now[name] + _coolen_configs[name] - t
        )
    )
    raise IgnoredException("")


# 通过装饰器实现handler级别的冷却
def coolen_async(times: int):
    def decorater(func):
        lst = 0
        res = inspect.signature(func)

        @functools.wraps(func)
        async def wraps1(bot, event, state):
            nonlocal lst
            r = time.time()
            if r - lst >= times:
                lst = r
                return await func(bot, event, state)
            else:
                logger.warning(" {}.{} 冷却中...".format(func.__module__, func.__name__))

        @functools.wraps(func)
        async def wraps2(self, bot, event, state):
            nonlocal lst
            r = time.time()
            if r - lst >= times:
                lst = r
                return await func(self, bot, event, state)
            else:
                logger.warning(" {}.{} 冷却中...".format(func.__module__, func.__name__))

        return wraps1 if "self" not in str(res) else wraps2

    return decorater


# 通过装饰器 patch matcher 实例的 run 函数可以实现 matcher 级别的冷却
def coolen_matcher(times, matcher: Matcher):
    matcher.run = coolen_async(times)(matcher.run)
    return matcher
