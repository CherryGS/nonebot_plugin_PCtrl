from ..core import *
from .exception import *
from .config import *


async def load_cool_config() -> dict[tuple[int, str], int]:
    res = await get_plugins_cfg()
    if not res:
        raise ValueError("No cool config found")
    dic = {(i.space, i.plugin_name): i.coolen_time for i in res}
    return dic
