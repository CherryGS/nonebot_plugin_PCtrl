from typing import Any, Callable, Set
import asyncio
from nonebot.log import logger


class Hook(object):
    _hooked_func: Set[Callable[..., Any]]

    def add_hook(self, func: Callable[..., Any]) -> Callable[..., Any]:
        self._hooked_func.add(func)
        return func

    async def run_hook(self):
        if self._hooked_func:
            try:
                lis = list(map(lambda x: x(), self._hooked_func))
                await asyncio.gather(*lis)
            except Exception as e:
                logger.opt(exception=e).error("执行插件数据库初始化后 HOOK 时出错")
                raise


db_init_finished = Hook()
