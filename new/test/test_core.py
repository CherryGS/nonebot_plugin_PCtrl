from typing import Callable
from controller.models import PyPluginConfig, Mixin
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy import insert, select
from utils import AutoTable

from controller.core import *

n = 1000
data1 = [
    PyPluginConfig(
        space=i,
        channel=i,
        user_id=i,
        plugin_name=str(i),
        ban=0,
        configure=0,
        coolen_time=0,
    ).dict()
    for i in range(n)
]

data2 = [
    PyPluginConfig(
        space=i,
        channel=i,
        user_id=i,
        plugin_name=str(i),
        ban=1,
        configure=1,
        coolen_time=1,
    ).dict()
    for i in range(n + n)
]


async def test_insert_ignore_common(
    ASession: Callable[..., AsyncSession], engine: AsyncEngine
):
    async with AutoTable(Mixin, engine) as table:
        async with ASession() as session:
            await session.execute(insert(table), data1)
            await insert_ignore(session, data2, table)
            cnt1 = len(
                (await session.execute(select(table.__table__).where(table.ban == 0)))
                .scalars()
                .all()
            )
            cnt2 = len(
                (await session.execute(select(table.__table__).where(table.ban == 1)))
                .scalars()
                .all()
            )
            assert cnt1 == cnt2


async def test_upsert_common(
    ASession: Callable[..., AsyncSession], engine: AsyncEngine
):
    async with AutoTable(Mixin, engine) as table:
        async with ASession() as session:
            await session.execute(insert(table), data1)
            await upsert(session, data2, ignore={"ban"}, table=table)
            assert (
                len(
                    (
                        await session.execute(
                            select(table.__table__).where(table.ban == 0)
                        )
                    )
                    .scalars()
                    .all()
                )
                == n
            )
            assert (
                len(
                    (
                        await session.execute(
                            select(table.__table__).where(table.ban == 1)
                        )
                    )
                    .scalars()
                    .all()
                )
                == n
            )
            assert (
                len(
                    (
                        await session.execute(
                            select(table.__table__).where(table.configure == 1)
                        )
                    )
                    .scalars()
                    .all()
                )
                == n + n
            )

            await upsert(session, data2, allow={"ban"}, table=table)
            assert (
                len(
                    (
                        await session.execute(
                            select(table.__table__).where(table.ban == 0)
                        )
                    )
                    .scalars()
                    .all()
                )
                == 0
            )


async def test_delete_all(ASession: Callable[..., AsyncSession], engine: AsyncEngine):
    async with AutoTable(Mixin, engine) as table:
        async with ASession() as session:
            await session.execute(insert(table.__table__), data1)
            await delete_all(session, {"ban": 0}, table=table)
            assert (
                len((await session.execute(select(table.__table__))).scalars().all())
                == 0
            )


async def test_show_all(ASession: Callable[..., AsyncSession], engine: AsyncEngine):
    async with AutoTable(Mixin, engine) as table:
        async with ASession() as session:
            await session.execute(insert(table.__table__), data1)
            assert len(await show_all(session, table=table)) == n
            await upsert(session, data2, ignore={"ban"}, table=table)
            assert len(await show_all(session, {"ban": 1}, table=table)) == n
