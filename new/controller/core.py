import asyncio
from typing import NamedTuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
from sqlalchemy.dialects.sqlite import insert as insert_sqlite
from sqlalchemy.dialects.postgresql import insert as insert_postgres
from .models import PluginConfig as cfg

__all__ = [
    "insert_ignore",
    "upsert",
    "merge_all",
    "delete_all",
    "show_all",
    "insert_ignore_sqlite",
    "upsert_sqlite",
    "insert_ignore_postgres",
    "upsert_postgres",
]


def all(ignore: set, allow: set, table):
    if not allow:
        allow = set([i.name for i in table.__table__.columns]) - ignore
    allow -= set([i.name for i in table.__table__.primary_key])
    return allow


# ! Common dialect
async def insert_ignore(
    session: AsyncSession, data: list[dict], table=cfg
) -> list[dict]:
    q = []
    for src in data:
        stmt = select(table.__table__)
        for i in table.__table__.primary_key:
            stmt = stmt.where(i == src[i.name])
        q.append(session.execute(stmt))
    res = await asyncio.gather(*q)
    ins = []
    upd = []
    for i in zip(res, data):
        if not i[0].scalars().all():
            ins.append(i[1])
        else:
            upd.append(i[1])
    if ins:
        await session.execute(insert(table.__table__), ins)
    await session.commit()
    return upd


async def upsert(
    session: AsyncSession,
    data: list[dict],
    ignore: set[str] = set(),
    allow: set[str] = set(),
    table=cfg,
):
    return await merge_all(session, data, ignore, allow, table)
    allow = all(ignore, allow, table)
    upd = await insert_ignore(session, data, table)
    for src in upd:
        stmt = update(table.__table__)
        for i in table.__table__.primary_key:
            stmt = stmt.where(i == src[i.name])
        for i in allow:
            stmt = stmt.values(**{i: src[i]})
        await session.execute(stmt)
    await session.commit()


async def merge_all(
    session: AsyncSession,
    data: list[dict],
    ignore: set[str] = set(),
    allow: set[str] = set(),
    table=cfg,
):
    allow = all(ignore, allow, table)
    q = []
    for src in data:
        stmt = select(table)
        for i in table.__table__.primary_key:
            stmt = stmt.where(i == src[i.name])
        q.append(session.execute(stmt))
    res = await asyncio.gather(*q)
    for i, j in zip(res, data):
        r = i.scalars().first()
        if not r:
            session.add(table(**j))
        else:
            for i in allow:
                setattr(r, i, j[i])
    await session.commit()


async def delete_all(session: AsyncSession, lim: dict = dict(), table=cfg):
    stmt = delete(table.__table__)
    for i in lim:
        stmt = stmt.where(table.__table__.c[i] == lim[i])
    await session.execute(stmt)
    await session.commit()


async def show_all(
    session: AsyncSession, lim: dict = dict(), table=cfg
) -> list[NamedTuple]:
    stmt = select(table.__table__)
    for i in lim:
        stmt = stmt.where(table.__table__.c[i] == lim[i])
    return (await session.execute(stmt)).scalars().all()


# ! SQLite dialect
async def insert_ignore_sqlite(session: AsyncSession, data: list[dict], table=cfg):
    await session.execute(insert_sqlite(table.__table__).on_conflict_do_nothing(), data)
    await session.commit()


async def upsert_sqlite(
    session: AsyncSession,
    data: list[dict],
    ignore: set[str] = set(),
    allow: set[str] = set(),
    table=cfg,
):
    stmt = insert_sqlite(table.__table__)
    await session.execute(
        stmt.on_conflict_do_update(
            index_elements=table.__table__.primary_key,
            _set={i: getattr(stmt.excluded, i) for i in all(ignore, allow, table)},
        ),
        data,
    )
    await session.commit()


# ! Postgres dialect
async def insert_ignore_postgres(session: AsyncSession, data: list[dict], table=cfg):
    await session.execute(
        insert_postgres(table.__table__).on_conflict_do_nothing(), data
    )
    await session.commit()


async def upsert_postgres(
    session: AsyncSession,
    data: list[dict],
    ignore: set[str] = set(),
    allow: set[str] = set(),
    table=cfg,
):
    stmt = insert_postgres(table.__table__)
    await session.execute(
        stmt.on_conflict_do_update(
            index_elements=table.__table__.primary_key,
            _set={i: getattr(stmt.excluded, i) for i in all(ignore, allow, table)},
        ),
        data,
    )
    await session.commit()
