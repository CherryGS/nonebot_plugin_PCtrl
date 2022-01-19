from typing import List, Literal, NamedTuple

from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError

from ...models import ASession, PluginsCfg, PyPluginsCfg, PyUserPerm, UserPerm, flag

if flag is "sqlite":
    from sqlalchemy.dialects.sqlite import insert as ins
elif flag is "postgresql":
    from sqlalchemy.dialects.postgresql import insert as ins


async def ins_perm_update(data: list):
    stmt = ins(UserPerm.__table__)  # type: ignore
    stmt = stmt.on_conflict_do_update(
        index_elements=PyUserPerm.__primary_key__,
        set_=PyUserPerm.make_value(stmt),
    )

    async with ASession() as session:
        await session.execute(stmt, data)
        await session.commit()


async def ins_perm_ignore(data: list):
    stmt = ins(UserPerm.__table__)  # type: ignore
    stmt = stmt.on_conflict_do_nothing()

    async with ASession() as session:
        await session.execute(stmt, data)
        await session.commit()


async def upd_perm(space: int, handle: int, name: str, perm: int, val: bool):
    stmt = (
        update(UserPerm.__table__)
        .where(UserPerm.space == space)
        .where(UserPerm.plugin_name == name)
        .where(UserPerm.handle == handle)
    )
    if val:
        stmt = stmt.values(perm_type=UserPerm.perm_type | (1 << perm))
    else:
        stmt = stmt.values(perm_type=UserPerm.perm_type & (~(1 << perm)))

    async with ASession() as session:
        await session.execute(stmt)
        await session.commit()


async def ups_perm(**kw):
    async with ASession() as session:
        await session.merge(UserPerm(**kw))
        await session.commit()


async def get_perms(
    space: int | None, handle: int | None, name: str | None
) -> List[PyUserPerm] | None:
    """
    获取 handle 在 space 对 name 的权限 , `None` 为不限制(全局)
    """
    session = ASession()
    stmt = select(UserPerm.__table__)

    if space is not None:
        stmt = stmt.where(UserPerm.space == space)
    if handle is not None:
        stmt = stmt.where(UserPerm.handle == handle)
    if name is not None:
        stmt = stmt.where(UserPerm.plugin_name == name)

    async with ASession() as session:
        res: List[NamedTuple] = (await session.execute(stmt)).all()
        if res:
            return [PyUserPerm.construct(**i._asdict()) for i in res]
