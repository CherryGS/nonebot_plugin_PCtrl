import inspect
import time
from functools import wraps
from typing import List, Tuple, Type

from nonebot import get_bot, get_driver
from nonebot.exception import (
    FinishedException,
    IgnoredException,
    PausedException,
    RejectedException,
    SkippedException,
    StopPropagation,
)

from .. import conf
from anyutils import CoolingError

driver = get_driver()


@driver.on_bot_connect
async def _(bot1):
    global bot
    bot = get_bot()


class SenderFactory:
    group_id = conf.reply_id

    def __init__(
        self,
        ignore: Tuple[Type[Exception], ...] = (),
        catch: Tuple[Type[Exception], ...] = (),
    ) -> None:
        self.ign = ignore
        self.catch = catch

    async def _send(self, msg: str):
        await bot.call_api(
            "send_group_msg",
            group_id=self.group_id,
            message=str(msg),
        )

    def when_raise(self, log: str | None = None):
        def decorater(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    r = await func(*args, **kwargs)
                    return r
                except self.catch:
                    pass
                except self.ign:
                    raise
                except Exception as e:
                    msg = log if log is not None else str(type(e)) + str(e)
                    await self._send(msg)
                    raise

            return wrapper

        return decorater

    def when_func_call(self, log: str | None = None):
        def decorater(func):
            nonlocal log
            if log is None:
                log = str(func.__qualname__) + str(inspect.signature(func))

            @wraps(func)
            async def wrapper(*args, **kwargs):
                msg = (
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    + " "
                    + str(log)
                )
                await self._send(msg)
                return await func(*args, **kwargs)

            return wrapper

        return decorater


sender = SenderFactory(
    (
        IgnoredException,
        SkippedException,
        FinishedException,
        RejectedException,
        PausedException,
        StopPropagation,
        FinishedException,
    ),
    (CoolingError,),
)
