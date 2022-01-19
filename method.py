from typing import Any, Dict
import orjson as js

from .config import conf, PluginCfg
from .plugin.core import *


async def del_left_plugin(names: set[str]):
    res = await get_plugins_cfg()
    if not res:
        return
    s = set()
    for i in res:
        s.add(i.plugin_name)
    ans = s - names
    for i in ans:
        await del_plugin_cfg()


async def init_plugins(data: set[PyPluginsCfg]):
    names = {i.plugin_name for i in data}
    await del_left_plugin(names)
    await ins_plugins_cfg_update([i.dict() for i in data])


async def load_config() -> Dict[str, PluginCfg]:
    file = conf.plugin_cfg_file
    with open(file, "r") as f:
        cfg: Dict[str, Any] = js.loads(f.read())
    res: Dict[str, PluginCfg] = dict()
    for i in cfg.items():
        res[i[0]] = PluginCfg(**i[1])
    return res
