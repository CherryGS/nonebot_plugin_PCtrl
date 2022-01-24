from typing import NamedTuple

from anyutils import anywhere, anywhere_lim
from sqlalchemy import delete, select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import PluginsCfg, PyPluginsCfg
from .utils import get_engine_type_dial


async def insert_cfg_update(
    flag: int,
    session: AsyncSession,
    data: list[dict] | dict,
    ign: tuple[str, ...] | None = None,
    all: tuple[str, ...] | None = None,
):
    r = get_engine_type_dial(flag)
    stmt = r.insert(PluginsCfg.__table__)

    res = PyPluginsCfg.make_value(stmt, ign, all)
    if not res:
        await insert_cfg_ignore(flag, session, data)
        return

    stmt = stmt.on_conflict_do_update(
        index_elements=PyPluginsCfg.__primary_key__,
        set_=res,
    )

    await session.execute(stmt, data)
    await session.commit()


async def insert_cfg_ignore(flag: int, session: AsyncSession, data: list[dict] | dict):
    r = get_engine_type_dial(flag)
    stmt = r.insert(PluginsCfg.__table__)

    stmt = stmt.on_conflict_do_nothing()

    await session.execute(stmt, data)
    await session.commit()


async def insert_cfg_after_query(session: AsyncSession, data: list[dict] | dict):
    if isinstance(data, dict):
        data = [data]
    for i in data:
        if not (
            await session.execute(
                anywhere_lim(
                    select(PluginsCfg.__table__),
                    (
                        (PluginsCfg.space, i["space"]),
                        (PluginsCfg.plugin_name, i["plugin_name"]),
                    ),
                    len(PyPluginsCfg.__primary_key__),
                )
            )
        ).all():
            await session.execute(insert(PluginsCfg.__table__), i)
    await session.commit()


async def merge_plugins_cfg(session: AsyncSession, data: list[dict] | dict):
    if isinstance(data, dict):
        data = [data]
    for i in data:
        await session.merge(PluginsCfg(**i))
    await session.commit()


async def get_plugins_cfg(
    session: AsyncSession, space: int | None = None, name: str | None = None
) -> list[PyPluginsCfg] | None:
    stmt = select(PluginsCfg.__table__)
    stmt = anywhere(stmt, ((PluginsCfg.space, space), (PluginsCfg.plugin_name, name)))

    res: list[NamedTuple] = (await session.execute(stmt)).all()
    if res:
        return [PyPluginsCfg.construct(**i._asdict()) for i in res]


async def del_plugin_cfg(
    session: AsyncSession, space: int | None = None, name: str | None = None
):
    stmt = delete(PluginsCfg.__table__)
    stmt = anywhere(stmt, ((PluginsCfg.space, space), (PluginsCfg.plugin_name, name)))

    await session.execute(stmt)
    await session.commit()
