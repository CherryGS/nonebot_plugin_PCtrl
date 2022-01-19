from ..core import *
from .exception import *


async def get_latest_used(space: int, name: str) -> int:
    """
    获得某个插件在某个space上一次使用时间

    Raises:
        `PluginNotFound`: 数据库查询无条目时抛出
    """
    res = await get_plugins_cfg(space, name)
    if res is None:
        raise PluginNotFoundError
    return res[0].latest_time


async def set_latest_used(space: int, name: str, time: int):
    res = await get_plugins_cfg(space, name)
    if res is None:
        raise PluginNotFoundError
    res = res[0]
    res.latest_time = time
    await ups_plugin_cfg(**res.dict())


async def check_cool_down(space: int, name: str, time: int) -> bool:
    res = await get_plugins_cfg(space, name)
    if res is None:
        raise PluginNotFoundError
    res = res[0]
    return (res.latest_time + res.coolen_time) <= time
