from typing import List
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp import Event
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.plugin import on_command, on_shell_command
from nonebot.log import logger
from nonebot.message import run_preprocessor
from nonebot.typing import T_State
from sqlalchemy.sql.expression import update, Update
from ..models import ASession
from ..models.global_models import pluginsCfg
from nonebot.exception import IgnoredException
from nonebot.rule import ArgumentParser
from sqlalchemy import select
from ..hook import hook


async def is_start(name) -> bool:
    stmt = (
        select(pluginsCfg)
        .where(pluginsCfg.plugin_name == name)
        .where(pluginsCfg.is_start == True)
        .limit(1)
    )
    try:
        session = ASession()
        if await is_exist(name):
            res = await session.execute(stmt)
            ok = bool(res.scalars().first())
        else:
            ok = True
    except:
        raise
    finally:
        await session.close()
    return ok


async def is_exist(name) -> bool:
    stmt = select(pluginsCfg).where(pluginsCfg.plugin_name == name).limit(1)
    try:
        session = ASession()
        res = await session.execute(stmt)
        ok = bool(res.scalars().first())
    except:
        raise
    finally:
        await session.close()
    return ok


@run_preprocessor
async def _(matcher: Matcher, bot: Bot, event: Event, state: T_State):
    # ignore 掉全局关闭的插件 matcher
    logger.debug("--- ignore ---")
    name = matcher.plugin_name
    if not (await is_start(name)):
        logger.warning("插件 |{}| 被全局关闭".format(name))
        raise IgnoredException("")


# -----------------------------------------------------------------------------

_cmd1 = on_command("listplugins", priority=1, permission=SUPERUSER)


@_cmd1.handle()
async def _(bot: Bot, event: Event, state: T_State):
    # 输出插件信息
    tx = ""
    try:
        session = ASession()
        res: List[pluginsCfg] = (
            await session.execute(select(pluginsCfg))
        ).scalars().all()
        if res:
            for i in res:
                tx += "插件名: {}  启用状态: {} \n".format(i.plugin_name, i.is_start)
        else:
            tx = "空"
    except:
        raise
    finally:
        await session.close()
    await _cmd1.finish(tx)


# -----------------------------------------------------------------------------

_parser = ArgumentParser()
_parser.add_argument("-p")  # 插件名称 , 将其状态反向

_cmd2 = on_shell_command("setplugin", parser=_parser, permission=SUPERUSER, priority=1)


@_cmd2.handle()
async def _(bot: Bot, event: Event, state: T_State):
    # 改变插件状态
    args = state["args"]
    if isinstance(args, Exception):
        await _cmd2.finish("参数填写错误 , 请检查")
    name = args.p
    if not await is_exist(name):
        await _cmd2.finish("参数错误 , |{}| 不在插件列表中".format(name))

    session = ASession()

    stmt = select(pluginsCfg).where(pluginsCfg.plugin_name == name).limit(1)
    try:
        res = (await session.execute(stmt)).scalars().first()
        res.is_start ^= True
        await session.commit()
    except Exception as e:
        await session.rollback()
        await _cmd2.send("插件状态更改错误...")
        raise e
    finally:
        await session.close()

    await _cmd2.finish("插件状态更改完成~")
