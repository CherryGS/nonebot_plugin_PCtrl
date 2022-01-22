from ...config import PluginCfg
from ...models import PyPluginsCfg
from ..core import (
    del_plugin_cfg,
    get_plugins_cfg,
    ins_plugins_cfg_ignore,
    ins_plugins_cfg_update,
)
from .config import ALL_PLUGIN_NAME, GLOBAL_SPACE


async def check_plugin_exist(name: str) -> bool:
    return bool(await get_plugins_cfg(space=GLOBAL_SPACE, name=name))


async def del_left_plugin(names: set[str]):
    res = await get_plugins_cfg()
    if not res:
        return
    s = set()
    for i in res:
        s.add(i.plugin_name)
    ans = s - names
    for i in ans:
        await del_plugin_cfg(name=i)


async def init_plugins(data: set[PyPluginsCfg], upd: bool = True):
    if not data:
        return
    if upd:
        await ins_plugins_cfg_update([i.dict() for i in data])
    else:
        await ins_plugins_cfg_ignore([i.dict() for i in data])


async def init_plugins_to_db(
    plugins_name: set[str], plugins: dict[str, list[PluginCfg]]
) -> set[str]:
    now: set[PyPluginsCfg] = set()
    name: set[str] = set()

    if "glob" in plugins:
        for i in plugins["glob"]:
            now.add(PyPluginsCfg(**i.dict(), plugin_name=ALL_PLUGIN_NAME))
        name.add(ALL_PLUGIN_NAME)

    for i in plugins.items():
        if i[0] not in plugins_name:
            continue
        for j in i[1]:
            now.add(PyPluginsCfg(**j.dict(), plugin_name=i[0]))
        name.add(i[0])

    await del_left_plugin(name | plugins_name)
    await init_plugins(now)
    return set(plugins.keys()) - name - {"glob"}
