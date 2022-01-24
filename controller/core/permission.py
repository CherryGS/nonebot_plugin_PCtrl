from typing import Any, NamedTuple

from anyutils import anywhere_lim, anywhere, anyvalue
from sqlalchemy import Column, delete, select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import PyUserPerm, UserPerm
from .utils import get_engine_type_dial


async def insert_perm_update(
    flag: int,
    session: AsyncSession,
    data: list[dict] | dict,
    ign: tuple[str, ...] | None = None,
    all: tuple[str, ...] | None = None,
):
    r = get_engine_type_dial(flag)
    stmt = r.insert(UserPerm.__table__)

    res = PyUserPerm.make_value(stmt, ign, all)
    if not res:
        await insert_perm_ignore(flag, session, data)
        return

    stmt = stmt.on_conflict_do_update(
        index_elements=PyUserPerm.__primary_key__,
        set_=PyUserPerm.make_value(stmt, ign, all),
    )
    await session.execute(stmt, data)
    await session.commit()


async def insert_perm_ignore(flag: int, session: AsyncSession, data: list[dict] | dict):
    r = get_engine_type_dial(flag)
    stmt = r.insert(UserPerm.__table__)

    stmt = stmt.on_conflict_do_nothing()
    await session.execute(stmt, data)
    await session.commit()


async def insert_perm_after_query(
    session: AsyncSession,
    data: list[dict] | dict,
    upd: bool = False,
    all: set[str] | None = None,
):
    if upd and not all:
        raise ValueError(f"upd={upd} but all={all}")
    if isinstance(data, dict):
        data = [data]
    update_data = list()
    insert_data = list()
    for i in data:
        if not (
            await session.execute(
                anywhere_lim(
                    select(UserPerm.__table__),
                    (
                        (UserPerm.space, i["space"]),
                        (UserPerm.handle, i["handle"]),
                        (UserPerm.plugin_name, i["plugin_name"]),
                    ),
                    len(PyUserPerm.__primary_key__),
                )
            )
        ).all():
            insert_data.append(i)
        else:
            update_data.append(i)
    await session.execute(insert(UserPerm.__table__), insert_data)
    await session.commit()


async def merge_perm(session: AsyncSession, data: list[dict] | dict):
    if isinstance(data, dict):
        data = [data]
    for i in data:
        await session.merge(UserPerm(**i))
    await session.commit()


async def get_perms(
    session: AsyncSession,
    space: int | None = None,
    handle: int | None = None,
    name: str | None = None,
) -> list[PyUserPerm] | None:
    """
    获取 handle 在 space 对 name 的权限 , `None` 为不限制(全局)
    """

    stmt = anywhere(
        select(UserPerm.__table__),
        (
            (UserPerm.space, space),
            (UserPerm.handle, handle),
            (UserPerm.plugin_name, name),
        ),
    )
    res: list[NamedTuple] = (await session.execute(stmt)).all()
    if res:
        return [PyUserPerm.construct(**i._asdict()) for i in res]


async def set_perms(
    session: AsyncSession,
    data: tuple[tuple[Column[Any], int], ...],
    space: int | None = None,
    handle: int | None = None,
    name: str | None = None,
):
    stmt: update = anywhere(
        update(UserPerm.__table__),
        (
            (UserPerm.space, space),
            (UserPerm.handle, handle),
            (UserPerm.plugin_name, name),
        ),
    )
    stmt = anyvalue(stmt, data)
    await session.execute(stmt)
    await session.close()


async def del_perms(
    session: AsyncSession,
    space: int | None = None,
    handle: int | None = None,
    name: str | None = None,
):
    stmt = delete(UserPerm.__table__)
    stmt = anywhere(
        stmt,
        (
            (UserPerm.space, space),
            (UserPerm.handle, handle),
            (UserPerm.plugin_name, name),
        ),
    )

    await session.execute(stmt)
    await session.commit()
