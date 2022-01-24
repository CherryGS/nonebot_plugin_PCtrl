from sqlalchemy.ext.asyncio import AsyncSession

from ..core import get_perms, insert_perm_update, INSERT_ON_CONFLICT, merge_perm
from ..models import PyUserPerm
from .config import NO_TYPE, ENABLE_TYPE, DISABLE_TYPE
from .exception import NoConfigError
from .utils import get_all_cate_perm


async def set_ban(flag: int, session: AsyncSession, space: int, handle: int, name: str):
    if flag in INSERT_ON_CONFLICT:
        await insert_perm_update(
            flag,
            session,
            data=PyUserPerm(
                space=space, handle=handle, plugin_name=name, ban=ENABLE_TYPE
            ).dict(),
            all=("ban",),
        )
    else:
        await merge_perm(
            session,
            PyUserPerm(
                space=space, handle=handle, plugin_name=name, ban=ENABLE_TYPE
            ).dict(),
        )


async def set_allow(
    flag: int, session: AsyncSession, space: int, handle: int, name: str
):
    if flag in INSERT_ON_CONFLICT:
        await insert_perm_update(
            flag,
            session,
            data=PyUserPerm(
                space=space, handle=handle, plugin_name=name, ban=DISABLE_TYPE
            ).dict(),
            all=("ban",),
        )
    else:
        await merge_perm(
            session,
            PyUserPerm(
                space=space, handle=handle, plugin_name=name, ban=DISABLE_TYPE
            ).dict(),
        )


async def del_type(
    flag: int, session: AsyncSession, space: int, handle: int, name: str
):
    if flag in INSERT_ON_CONFLICT:
        await insert_perm_update(
            flag,
            session,
            data=PyUserPerm(
                space=space, handle=handle, plugin_name=name, ban=NO_TYPE
            ).dict(),
            all=("ban",),
        )
    else:
        await merge_perm(
            session,
            PyUserPerm(
                space=space, handle=handle, plugin_name=name, ban=NO_TYPE
            ).dict(),
        )


async def check_ban(session: AsyncSession, space: int, handle: int, name: str) -> bool:
    """
    返回是否被 `ban` , `True` 是 , `False` 否
    """
    res = await get_all_cate_perm(session, space, handle, name)
    if not res:
        raise NoConfigError(f"space: {space} handle: {handle} name: {name} 未查询到 config")
    for i in res:
        if i.ban == ENABLE_TYPE:
            return True
        elif i.ban == DISABLE_TYPE:
            return False
    raise NoConfigError(f"space: {space} handle: {handle} name: {name} 所有情况 ban 都未设定")


async def get_all_ban(
    session: AsyncSession, space: int | None, handle: int | None, name: str | None
) -> list[PyUserPerm] | None:
    res = await get_perms(session, space, handle, name)
    if not res:
        return None
    lis = []
    for i in res:
        if i.ban != NO_TYPE:
            lis.append(i)
    return lis if lis else None
