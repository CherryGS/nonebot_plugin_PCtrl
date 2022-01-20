from ..core import get_plugins_cfg
from ... import gbname


async def check_plugin_exist(name: str) -> bool:
    return bool(await get_plugins_cfg(space=gbname.space, name=name))
