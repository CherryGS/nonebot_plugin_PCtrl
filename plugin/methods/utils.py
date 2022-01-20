from ..core import *
from ... import default_perm, gbname


async def clean_perms(p=default_perm):
    await del_perms(perm=p)


async def check_perm(space: int, handle: int, name: str, perm: int):
    flag = False
    res = await get_perms(space, handle, name)
    if res is None:
        flag = True
    else:
        return bool(res[0].perm_type & (1 << perm))

    res = await get_perms(space, handle, gbname.name)
    if res is None:
        flag = True
    else:
        return bool(res[0].perm_type & (1 << perm))

    res = await get_perms(space, gbname.handle, name)
    if res is None:
        flag = True
    else:
        return bool(res[0].perm_type & (1 << perm))

    res = await get_perms(gbname.space, handle, name)
    if res is None:
        flag = True
    else:
        return bool(res[0].perm_type & (1 << perm))

    res = await get_perms(space, gbname.handle, gbname.name)
    if res is None:
        flag = True
    else:
        return bool(res[0].perm_type & (1 << perm))

    res = await get_perms(gbname.space, handle, gbname.name)
    if res is None:
        flag = True
    else:
        return bool(res[0].perm_type & (1 << perm))

    res = await get_perms(gbname.space, gbname.handle, name)
    if res is None:
        flag = True
    else:
        return bool(res[0].perm_type & (1 << perm))

    res = await get_perms(gbname.space, gbname.handle, gbname.name)
    if res is None:
        pass
    else:
        return bool(res[0].perm_type & (1 << perm))

    return bool(default_perm & (1 << perm))
