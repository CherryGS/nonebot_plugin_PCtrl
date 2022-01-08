import functools
import inspect
import time
from typing import Dict, List

from nonebot import get_driver
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.adapters.cqhttp.event import MetaEvent
from nonebot.exception import IgnoredException
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor
from nonebot.permission import SUPERUSER
from nonebot.plugin import on_command, on_shell_command
from nonebot.rule import ArgumentParser
from nonebot.typing import T_State
from sqlalchemy import select
from sqlalchemy.sql.expression import update

from ..hook import db_init_finished
from ..models import ASession
from ..models.global_models import pluginsCfg
from .config import CoolenConf

_coolen_configs: Dict[str, int] = dict()  # 插件冷却设置
_coolen_now: Dict[str, int] = dict()  # 当前插件使用情况
_conf = CoolenConf(**get_driver().config.dict())

_reply = _conf.coolen_time_reply != None
_reply_time = _conf.coolen_time_reply if _reply else 0

# 通过装饰器实现handler级别的冷却
def coolen_async(times: int, spcing: bool = True, reply: bool = _reply):
    def decorater(func):
        lst = 0
        res = inspect.signature(func)

        async def _do(func, bot, event, reply, r):
            if reply:
                await _reply_coolen_time(
                    bot, event, func.__module__ + "." + func.__name__, lst + times - r
                )
            logger.warning(" {}.{} 冷却中...".format(func.__module__, func.__name__))

        @functools.wraps(func)
        async def wraps(*args, **kwargs):
            nonlocal lst
            r = time.time()
            if r - lst >= times:
                lst = r
                await func(*args, **kwargs)
            else:
                logger.warning(" {}.{} 冷却中...".format(func.__module__, func.__name__))

        if not spcing:
            return wraps

        @functools.wraps(func)
        async def wraps1(self, bot, event, state):
            nonlocal lst
            r = time.time()
            if r - lst >= times:
                lst = r
                await func(self, bot, event, state)
            else:
                await _do(func, bot, event, reply, r)

        @functools.wraps(func)
        async def wraps2(matcher, bot, event, state):
            nonlocal lst
            r = time.time()
            if r - lst >= times:
                lst = r
                await func(matcher, bot, event, state)
            else:
                await _do(func, bot, event, reply, r)

        @functools.wraps(func)
        async def wraps3(bot, event, state):
            nonlocal lst
            r = time.time()
            if r - lst >= times:
                lst = r
                await func(bot, event, state)
            else:
                await _do(func, bot, event, reply, r)

        return (
            wraps1
            if "self" in str(res)
            else (wraps2 if "matcher" in str(res) else wraps3)
        )

    return decorater


# 通过装饰器 patch matcher 实例的 run 函数实现 matcher 级别的冷却
def coolen_matcher(times, matcher: Matcher):
    matcher.run = coolen_async(times)(matcher.run)
    return matcher


async def is_exist(name) -> bool:
    stmt = select(pluginsCfg).where(pluginsCfg.plugin_name == name).limit(1)
    session = ASession()
    try:
        res = await session.execute(stmt)
        ok = bool(res.scalars().first())
    except:
        raise
    finally:
        await session.close()
    return ok


@coolen_async(_reply_time, False)
async def _reply_coolen_time(bot: Bot, event: Event, name: str, times: int):
    if not isinstance(event, MetaEvent):
        await bot.send(event, "{} 冷却中 , 还剩 {} 秒".format(name, int(times)))


@db_init_finished.add_hook
async def _load_coolen_time():
    """将插件冷却信息载入内存
    """
    global _coolen
    session = ASession()
    try:
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
    if _reply:
        await _reply_coolen_time(
            bot, event, name, _coolen_now[name] + _coolen_configs[name] - t
        )
    raise IgnoredException("")


_cmd1 = on_command("listcool", permission=SUPERUSER, priority=2)


@_cmd1.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global _coolen_configs
    msg = ""
    for i in _coolen_configs.items():
        msg += "插件名: {}  冷却时间: {} \n".format(i[0], i[1])
    await _cmd1.finish(msg)


_parser = ArgumentParser()
_parser.add_argument("-p")  # 插件名称
_parser.add_argument("-t")  # 修改时间

_cmd2 = on_shell_command("setcool", parser=_parser, permission=SUPERUSER, priority=2)


@_cmd2.handle()
async def _(bot: Bot, event: Event, state: T_State):
    args = state["args"]
    if isinstance(args, Exception):
        await _cmd2.finish("参数填写错误 , 请检查")
    name = args.p
    if not await is_exist(name):
        await _cmd2.finish("参数错误 , |{}| 不在插件列表中".format(name))

    times = args.t
    try:
        times = int(times)
    except ValueError:
        await _cmd2.finish("-t 参数未跟数字 , 请重新输入")

    stmt = select(pluginsCfg).where(pluginsCfg.plugin_name == name).limit(1)
    try:
        session = ASession()
        res: pluginsCfg = (await session.execute(stmt)).scalars().first()
        res.coolen_time = times
        await session.commit()
    except:
        raise
    finally:
        await session.close()

    await _load_coolen_time()
    await _cmd2.finish("修改冷却完成")
