from typing import List, Type


from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent, MessageEvent
from nonebot.exception import IgnoredException
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor
from nonebot.permission import SUPERUSER
from nonebot.plugin import on_command, on_shell_command
from nonebot.rule import ArgumentParser
from nonebot.typing import T_State
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.expression import delete

from ..models import ASession
from ..models.global_models import PluginsBan, PluginsCfg
from .core import *

__all__ = []


@run_preprocessor
async def _(matcher: Matcher, bot: Bot, event: MessageEvent, state: T_State):
    # ignore掉全局被ban的人/群的matcher
    logger.debug("--- ban ---")
    handle_qq = int(event.user_id)
    name = matcher.plugin_name
    if not name:
        return

    if await check_plugin_ban(0, handle_qq, name):
        logger.warning("QQ号:{}被全局ban".format(handle_qq))
        raise IgnoredException("")

    if isinstance(event, GroupMessageEvent):
        handle_gr = event.group_id
        if await check_plugin_ban(1, handle_gr, name):
            logger.warning("群号:{}被全局ban".format(handle_gr))
            raise IgnoredException("")


parser = ArgumentParser()
parser.add_argument("-u")  # 个人 qq 号
parser.add_argument("-g")  # 群号
parser.add_argument("-p")  # 插件名

cmd1 = on_shell_command("ban", parser=parser, permission=SUPERUSER)


async def _BanParser(matcher: Type[Matcher], args, event: Event):
    if isinstance(args, Exception):
        await matcher.finish("参数填写错误 , 请检查")

    if args.u and args.g:
        await matcher.finish("个人和群只能选择一个")

    if not args.u and not args.g:
        if not isinstance(event, GroupMessageEvent):
            await matcher.finish("个人和群必须选择一个")
        else:
            args.g = event.group_id

        if not await check_plugin_exist(args.p):
            await matcher.finish("参数错误 , |{}| 不在插件列表中".format(args.p))

    ban_type = 0
    handle: int
    name = args.p

    if args.g:
        ban_type = 1
        handle = int(args.g)
    else:
        ban_type = 0
        handle = int(args.u)

    return ban_type, handle, name


@cmd1.handle()
async def _(bot: Bot, event: Event, state: T_State):
    # ban 人/群
    ban_type, handle, name = await _BanParser(cmd1, state["args"], event)
    global _ban_settings

    try:
        await set_plugin_ban(ban_type, handle, name)
        await cmd1.finish("ban执行成功")
    except SQLAlchemyError as e:
        await cmd1.send("向数据库中添加ban时出现异常\n 异常信息 : \n {}".format(e))
        raise e


cmd2 = on_shell_command("unban", parser=parser, permission=SUPERUSER)


@cmd2.handle()
async def _(bot: Bot, event: Event, state: T_State):
    # unban 人/群
    ban_type, handle, name = await _BanParser(cmd2, state["args"], event)

    if await check_plugin_ban(ban_type, handle, name):
        try:
            await del_plugin_ban(ban_type, handle, name)
            await cmd2.finish("unban执行成功")
        except Exception as e:
            await cmd1.send("unban时出现异常\n 异常信息 : \n {}".format(e))
            raise
    else:
        await cmd2.finish("该人/群未被ban插件 |{}|".format(name))


cmd3 = on_command("listban", permission=SUPERUSER)


@cmd3.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global _ban_settings
    msg = ""
    session = ASession()
    try:
        res = await list_plugin_ban()
        if res:
            for i in res:
                msg += (
                    str(i.handle)
                    + (" 群" if i.ban_type else " QQ")
                    + "被 ban 了插件 "
                    + i.plugin_name
                    + "\n"
                )
        else:
            msg = "空"
    except Exception as e:
        await cmd3.send(str(e))
        raise
    finally:
        await session.close()
    await cmd3.finish(msg)
