from sqlalchemy.ext.asyncio import AsyncSession

from ..config import PluginCfg
from ..core import (
    INSERT_ON_CONFLICT,
    del_plugin_cfg,
    get_plugins_cfg,
    insert_cfg_ignore,
    insert_cfg_update,
    insert_cfg_after_query,
    merge_plugins_cfg,
)
from ..models import PyPluginsCfg
from .config import GLOBAL_PLUGIN_NAME, GLOBAL_SPACE


async def check_plugin_exist(session: AsyncSession, name: str) -> bool:
    return bool(await get_plugins_cfg(session, space=GLOBAL_SPACE, name=name))


async def del_left_plugin(session: AsyncSession, names: set[str]):
    res = await get_plugins_cfg(session)
    if not res:
        return
    s = set()
    for i in res:
        s.add(i.plugin_name)
    ans = s - names
    for i in ans:
        await del_plugin_cfg(session, name=i)


async def init_plugins(
    flag: int, session: AsyncSession, data: set[PyPluginsCfg], upd: bool = True
):
    if not data:
        return
    if flag in INSERT_ON_CONFLICT:
        if upd:
            await insert_cfg_update(flag, session, [i.dict() for i in data])
        else:
            await insert_cfg_ignore(flag, session, [i.dict() for i in data])
    else:
        if upd:
            await merge_plugins_cfg(session, [i.dict() for i in data])
        else:
            await insert_cfg_after_query(session, [i.dict() for i in data])


async def init_plugins_to_db(
    flag: int,
    session: AsyncSession,
    plugins_name: set[str],
    plugins: dict[str, list[PluginCfg]],
) -> set[str]:
    now: set[PyPluginsCfg] = set()
    name: set[str] = set()

    if "glob" in plugins:
        for i in plugins["glob"]:
            now.add(PyPluginsCfg(**i.dict(), plugin_name=GLOBAL_PLUGIN_NAME))
        name.add(GLOBAL_PLUGIN_NAME)

    for i in plugins.items():
        if i[0] not in plugins_name:
            continue
        for j in i[1]:
            now.add(PyPluginsCfg(**j.dict(), plugin_name=i[0]))
        name.add(i[0])

    await del_left_plugin(session, name | plugins_name)
    await init_plugins(flag, session, now)
    return set(plugins.keys()) - name - {"glob"}
