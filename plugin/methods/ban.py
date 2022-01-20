from .config import *
from .utils import *
from .exception import *
from .config import *


async def set_ban(space: int, handle: int, name: str):
    await ins_perm_update(
        PyUserPerm(
            space=space, handle=handle, plugin_name=name, ban=REJECT_TYPE
        ).dict(),
        all={"ban"},
    )


async def del_ban(space: int, handle: int, name: str):
    await ins_perm_update(
        PyUserPerm(space=space, handle=handle, plugin_name=name, ban=NO_TYPE).dict(),
        all={"ban"},
    )


async def check_ban(space: int, handle: int, name: str) -> bool:
    """
    返回是否被 `ban` , `True` 是 , `False` 否

    Args:
        `space` : [description]
        `handle` : [description]
        `name` : [description]

    Raises:
        `NoConfigError`: [description]
        `NoConfigError`: [description]

    Returns:
        `bool`: [description]
    """
    res = await get_all_perm(space, handle, name)
    if not res:
        raise NoConfigError(f"space: {space} handle: {handle} name: {name} 未查询到 config")
    for i in res:
        if i.ban == 1:
            return True
        elif i.ban == 2:
            return False
    raise NoConfigError(f"space: {space} handle: {handle} name: {name} 所有情况 ban 都未设定")


async def get_all_ban(
    space: int | None, handle: int | None, name: str | None
) -> list[PyUserPerm] | None:
    res = await get_perms(space, handle, name)
    if not res:
        return None
    lis = []
    for i in res:
        if i.ban != 0:
            lis.append(i)
    return lis if lis else None
