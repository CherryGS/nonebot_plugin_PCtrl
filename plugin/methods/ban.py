from typing import List
from .utils import *
from .config import *
from ..core import *


async def set_ban(space: int, handle: int, name: str):
    await ins_perm_ignore(
        PyUserPerm(
            space=space,
            handle=handle,
            plugin_name=name,
            perm_type=default_perm,
        ).dict()
    )
    await upd_perm(space, handle, name, my.ban.lv, True)


async def del_ban(space: int, handle: int, name: str):
    await ins_perm_ignore(
        PyUserPerm(
            space=space,
            handle=handle,
            plugin_name=name,
            perm_type=default_perm,
        ).dict()
    )
    await upd_perm(space, handle, name, my.ban.lv, False)


async def check_ban(space: int, handle: int, name: str) -> bool:
    return await check_perm(space, handle, name, my.ban.lv)


async def get_all_ban(
    space: int | None, handle: int | None, name: str | None, expect: bool = True
) -> List[PyUserPerm] | None:
    res = await get_perms(space, handle, name)
    if not res:
        return None
    lis = []
    for i in res:
        if (i.perm_type & (1 << my.ban.lv)) == expect:
            lis.append(i)
    return lis
