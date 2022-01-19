from functools import wraps
from typing import List, Tuple, Type
import time
from nonebot import get_bot
from nonebot.exception import (
    IgnoredException,
    SkippedException,
    FinishedException,
    RejectedException,
    PausedException,
    StopPropagation,
)

from ..config import conf
import inspect
from nonebot import get_driver

driver = get_driver()


@driver.on_bot_connect
async def _(bot1):
    global bot
    bot = bot1


class SenderFactory:
    group_id = conf.reply_id

    def __init__(self, ignore: Tuple[Type[Exception], ...]) -> None:
        self.ign = ignore

    async def _send(self, msg: str):
        await bot.call_api(
            "/send_group_msg",
            group_id=self.group_id,
            message=str(msg),
        )

    def when_raise(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                r = await func(*args, **kwargs)
                return r
            except self.ign:
                pass
            except Exception as e:
                await self._send(str(e))
                raise

        return wrapper

    def when_func_call(self, log: str | None = None):
        def decorater(func):
            nonlocal log
            if log is None:
                log = str(func.__qualname__) + str(inspect.signature(func))

            @wraps(func)
            async def wrapper(*args, **kwargs):
                msg = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + str(log)
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
    )
)
