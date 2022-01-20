import asyncio
from ..core import *
from .config import GLOBAL_SPACE, GLOBAL_HANDLE, ALL_PLUGIN_NAME


async def get_all_perm(space: int, handle: int, name: str) -> list[PyUserPerm] | None:
    query = [
        get_perms(space, handle, name),
        get_perms(space, handle, ALL_PLUGIN_NAME),
        get_perms(space, GLOBAL_HANDLE, name),
        get_perms(GLOBAL_SPACE, handle, name),
        get_perms(space, GLOBAL_HANDLE, ALL_PLUGIN_NAME),
        get_perms(GLOBAL_SPACE, handle, ALL_PLUGIN_NAME),
        get_perms(GLOBAL_SPACE, GLOBAL_HANDLE, name),
        get_perms(GLOBAL_SPACE, GLOBAL_HANDLE, ALL_PLUGIN_NAME),
    ]
    res = await asyncio.gather(*query)
    r = list()
    for i in res:
        if i:
            r.append(PyUserPerm.from_orm(i[0]))
    return r if r else None
