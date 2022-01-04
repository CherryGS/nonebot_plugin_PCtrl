from typing import List
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.adapters.cqhttp.event import GroupMessageEvent
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

from ..hook import hook
from ..models import ASession
from ..models.global_models import pluginsBan, pluginsCfg


# -----------------------------------------------------------------------------


async def exists_rule(ban_type, handle, plugin_name):
    stmt = (
        select(pluginsBan)
        .where(pluginsBan.ban_type == ban_type)
        .where(pluginsBan.handle == handle)
        .where(pluginsBan.plugin_name == plugin_name)
        .limit(1)
    )
    try:
        session = ASession()
        res = await session.execute(stmt)
        return bool(res.scalars().first())
    except:
        raise
    finally:
        await session.close()


@run_preprocessor
async def _(matcher: Matcher, bot: Bot, event: Event, state: T_State):
    # ignore掉全局被ban的人/群的matcher
    logger.debug("--- ban ---")
    handle_qq = int(event.user_id)
    name = matcher.plugin_name
    if await exists_rule(0, handle_qq, name):
        logger.warning("QQ号:{}被全局ban".format(handle_qq))
        raise IgnoredException("")

    if isinstance(event, GroupMessageEvent):
        handle_gr = event.group_id
        if await exists_rule(1, handle_gr, name):
            logger.warning("群号:{}被全局ban".format(handle_gr))
            raise IgnoredException("")


# -----------------------------------------------------------------------------

_parser = ArgumentParser()
_parser.add_argument("-u")  # 个人 qq 号
_parser.add_argument("-g")  # 群号
_parser.add_argument("-p")  # 插件名

_cmd1 = on_shell_command("ban", parser=_parser, permission=SUPERUSER)


async def _BanParser(matcher, args):
    if isinstance(args, Exception):
        await matcher.finish("参数填写错误 , 请检查")

    if args.u and args.g:
        await matcher.finish("个人和群只能选择一个")

    if not args.u and not args.g:
        await matcher.finish("个人和群必须选择一个")

    async with ASession() as session:
        stmt = select(pluginsCfg).where(pluginsCfg.plugin_name == args.p).limit(1)
        res = await session.execute(stmt)
        if not res.first():
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


@_cmd1.handle()
async def _(bot: Bot, event: Event, state: T_State):
    # ban 人/群
    ban_type, handle, name = await _BanParser(_cmd1, state["args"])
    global _ban_settings

    session = ASession()
    stmt = (
        select(pluginsBan)
        .where(pluginsBan.ban_type == ban_type)
        .where(pluginsBan.handle == handle)
        .where(pluginsBan.plugin_name == name)
        .limit(1)
    )
    try:
        res = (await session.execute(stmt)).scalars().first()
        now = pluginsBan(ban_type=ban_type, handle=handle, plugin_name=name)
        if res:
            res = now
        else:
            session.add(now)
        await session.commit()
        await _cmd1.finish("ban执行成功")
    except SQLAlchemyError as e:
        await _cmd1.send("向数据库中添加ban时出现异常\n 异常信息 : \n {}".format(e))
        raise e
    finally:
        await session.close()


# -----------------------------------------------------------------------------

_parser = ArgumentParser()
_parser.add_argument("-u")  # 个人 qq 号
_parser.add_argument("-g")  # 群号
_parser.add_argument("-p")  # 插件名

_cmd2 = on_shell_command("unban", parser=_parser, permission=SUPERUSER)


@_cmd2.handle()
async def _(bot: Bot, event: Event, state: T_State):
    # unban 人/群
    ban_type, handle, name = await _BanParser(_cmd2, state["args"])

    if await exists_rule(ban_type, handle, name):
        session = ASession()
        try:
            stmt = delete(pluginsBan).where(
                pluginsBan.ban_type == ban_type,
                pluginsBan.handle == handle,
                pluginsBan.plugin_name == name,
            )
            await session.execute(stmt)
            await session.commit()
            await _cmd2.finish("unban执行成功")
        except SQLAlchemyError as e:
            await _cmd1.send("unban时出现异常\n 异常信息 : \n {}".format(e))
            raise
        finally:
            await session.close()
    else:
        await _cmd2.finish("该人/群未被ban插件 |{}|".format(name))


# -----------------------------------------------------------------------------

_cmd3 = on_command("listban", permission=SUPERUSER)


@_cmd3.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global _ban_settings
    msg = ""
    try:
        session = ASession()
        res: List[pluginsBan] = (
            await session.execute(select(pluginsBan))
        ).scalars().all()
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
        await _cmd3.send(str(e))
        raise
    finally:
        await session.close()
    await _cmd3.finish(msg)
