from nonebot.adapters.onebot.v11 import (
    Bot,
    Event,
    GroupMessageEvent,
    PrivateMessageEvent,
)
from nonebot.exception import IgnoredException
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor
from nonebot.params import State
from nonebot.plugin import on_shell_command, on_command
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
from nonebot.rule import ArgumentParser

from .methods import *
from .sender import sender


@run_preprocessor
@sender.when_raise
async def _(matcher: Matcher, bot: Bot, event: Event, state: T_State = State()):
    if matcher.plugin_name == None:
        raise TypeError("插件名为空")
    if isinstance(event, PrivateMessageEvent):
        if check_ban(gbname.space, event.user_id, matcher.plugin_name):
            raise IgnoredException("ban")
    elif isinstance(event, GroupMessageEvent):
        if check_ban(event.group_id, event.user_id, matcher.plugin_name):
            raise IgnoredException("ban")


parser = ArgumentParser()
parser.add_argument("-u")  # qq 号
parser.add_argument("-g")  # 群号
parser.add_argument("-p")  # 插件名


cmd1 = on_shell_command(
    ("ban", "unban"), parser=parser, priority=1, permission=SUPERUSER
)


@cmd1.handle()
@sender.when_raise
async def _(bot: Bot, event: Event, state: T_State = State()):
    args = state["args"]
    space = args.g if args.g is not None else gbname.space
    handle = args.u if args.u is not None else gbname.handle
    name = args.p if args.p is not None else gbname.name
    c = "unban" if "unban" in state["_prefix"]["raw_command"] else "ban"
    if c is "unban":
        await del_ban(space, handle, name)
    else:
        await set_ban(space, handle, name)
    await cmd1.finish(f"{c}成功({space},{handle},{name})")


cmd2 = on_shell_command("listban", parser=parser, priority=1, permission=SUPERUSER)


@cmd2.handle()
@sender.when_raise
async def _(bot: Bot, event: Event, state: T_State = State()):
    args = state["args"]
    space = args.g if args.g is not None else gbname.space
    handle = args.u if args.u is not None else gbname.handle
    name = args.p if args.p is not None else gbname.name
    res = await get_all_ban(space, handle, name)

    if not res:
        await cmd2.finish("空")

    msg = ""
    for i in res:
        msg += "全局" if i.space == gbname.space else f"群{i.space}" + "中"
        msg += "所有人" if i.handle == gbname.handle else f"QQ{i.handle}" + "被ban"
        msg += "所有插件" if i.plugin_name == gbname.name else f"插件{i.plugin_name}" + "\n"
    await cmd2.finish(msg)
