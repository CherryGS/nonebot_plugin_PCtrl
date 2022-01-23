import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from ..core import get_perms
from ..models import PyUserPerm
from .config import ALL_PLUGIN_NAME, GLOBAL_HANDLE, GLOBAL_SPACE


async def get_all_cate_perm(
    session: AsyncSession, space: int, handle: int, name: str
) -> list[PyUserPerm] | None:
    query = [
        get_perms(session, space, handle, name),
        get_perms(session, space, handle, ALL_PLUGIN_NAME),
        get_perms(session, space, GLOBAL_HANDLE, name),
        get_perms(session, GLOBAL_SPACE, handle, name),
        get_perms(session, space, GLOBAL_HANDLE, ALL_PLUGIN_NAME),
        get_perms(session, GLOBAL_SPACE, handle, ALL_PLUGIN_NAME),
        get_perms(session, GLOBAL_SPACE, GLOBAL_HANDLE, name),
        get_perms(session, GLOBAL_SPACE, GLOBAL_HANDLE, ALL_PLUGIN_NAME),
    ]
    res = await asyncio.gather(*query)
    r = list()
    for i in res:
        if i:
            r.append(PyUserPerm.from_orm(i[0]))
    return r if r else None
