from ..core import get_plugins_cfg
from .config import gbname


async def check_plugin_exist(name: str) -> bool:
    return bool(await get_plugins_cfg(space=gbname.space, name=name))
