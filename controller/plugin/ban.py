from nonebot.adapters.onebot.v11 import (
    Bot,
    Event,
    GroupMessageEvent,
    PrivateMessageEvent,
)
from nonebot.exception import IgnoredException, ParserExit
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor
from nonebot.params import ShellCommandArgs, State
from nonebot.permission import SUPERUSER
from nonebot.plugin import on_shell_command
from nonebot.rule import ArgumentParser
from nonebot.typing import T_State

from .. import all_cfg
from ..methods import *
from ..methods.exception import NoConfigError
from . import AEngine, ASession, flag
from .sender import sender


@run_preprocessor
async def _(matcher: Matcher, event: Event):
    async with ASession() as session:
        if matcher.plugin_name == None:
            raise TypeError("插件名为空")
        if not await check_plugin_exist(session, matcher.plugin_name):
            logger.debug(f"plugin {matcher.plugin_name} not found.")
            return
        try:
            if isinstance(event, PrivateMessageEvent):
                if await check_ban(
                    session, GLOBAL_SPACE, event.user_id, matcher.plugin_name
                ):
                    logger.warning(f"ban QQ{event.user_id} 插件{matcher.plugin_name}")
                    raise IgnoredException("ban")
            elif isinstance(event, GroupMessageEvent):
                if await check_ban(
                    session, event.group_id, event.user_id, matcher.plugin_name
                ):
                    logger.warning(
                        f"ban 群{event.group_id} QQ{event.user_id} 插件{matcher.plugin_name}"
                    )
                    raise IgnoredException("ban")
        except NoConfigError:
            if all_cfg.basic.default_ban:
                raise IgnoredException("ban")


@sender.when_raise("参数错误")
async def _parser(args):
    space = (
        GLOBAL_SPACE
        if isinstance(args.g, ParserExit)
        else None
        if args.g == None
        else int(args.g)
    )
    handle = (
        GLOBAL_HANDLE
        if isinstance(args.u, ParserExit)
        else None
        if args.u == None
        else int(args.u)
    )
    name = (
        GLOBAL_PLUGIN_NAME
        if isinstance(args.p, ParserExit)
        else None
        if args.p == None
        else args.p
    )
    return space, handle, name


@sender.when_raise("参数错误")
async def _nxt_parser(space, handle, name):
    space = space if space is not None else GLOBAL_SPACE
    handle = handle if handle is not None else GLOBAL_HANDLE
    name = name if name is not None else GLOBAL_PLUGIN_NAME
    return space, handle, name


parser = ArgumentParser()
parser.add_argument("-u")  # qq 号
parser.add_argument("-g")  # 群号
parser.add_argument("-p")  # 插件名

cmd0 = on_shell_command("unban", parser=parser, priority=1, permission=SUPERUSER)


@cmd0.handle()
@sender.when_raise()
async def _(bot: Bot, event: Event, state: T_State = State(), args=ShellCommandArgs()):
    space, handle, name = await _parser(args)
    space, handle, name = await _nxt_parser(space, handle, name)
    async with ASession() as session:
        await del_type(flag, session, space, handle, name)
    await cmd0.finish(f"unban成功({space},{handle},{name})")


cmd1 = on_shell_command("ban", parser=parser, priority=1, permission=SUPERUSER)


@cmd1.handle()
@sender.when_raise()
async def _(bot: Bot, event: Event, args=ShellCommandArgs()):
    space, handle, name = await _parser(args)
    space, handle, name = await _nxt_parser(space, handle, name)
    async with ASession() as session:
        await set_ban(flag, session, space, handle, name)
    await cmd1.finish(f"ban成功({space},{handle},{name})")


cmd2 = on_shell_command("listban", parser=parser, priority=1, permission=SUPERUSER)


@cmd2.handle()
@sender.when_raise()
async def _(bot: Bot, event: Event, args=ShellCommandArgs()):
    space, handle, name = await _parser(args)
    async with ASession() as session:
        res = await get_all_ban(session, space, handle, name)
    if not res:
        msg = "空"
    else:
        msg = ""
        for i in res:
            if i.ban != ENABLE_TYPE:
                continue
            msg += ("全局" if i.space == GLOBAL_SPACE else f"群{i.space}") + "中"
            msg += ("所有人" if i.handle == GLOBAL_HANDLE else f"QQ{i.handle}") + "被ban"
            msg += (
                "所有插件" if i.plugin_name == GLOBAL_PLUGIN_NAME else f"插件{i.plugin_name}"
            ) + "\n"
        msg = msg if msg else "空"
    if not res:
        msg1 = "空"
    else:
        msg1 = ""
        for i in res:
            if i.ban != DISABLE_TYPE:
                continue
            msg1 += ("全局" if i.space == GLOBAL_SPACE else f"群{i.space}") + "中"
            msg1 += ("所有人" if i.handle == GLOBAL_HANDLE else f"QQ{i.handle}") + "被允许使用"
            msg1 += (
                "所有插件" if i.plugin_name == GLOBAL_PLUGIN_NAME else f"插件{i.plugin_name}"
            ) + "\n"
        msg1 = msg1 if msg1 else "空"
    await cmd2.send("ban列表")
    await cmd2.send(msg)
    await cmd2.send("unban列表")
    await cmd2.finish(msg1)
