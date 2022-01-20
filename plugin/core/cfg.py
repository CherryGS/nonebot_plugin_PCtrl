from typing import Any, Dict, List, NamedTuple

from sqlalchemy import delete, select

from anyutils import anywhere

from ...models import ASession, PluginsCfg, PyPluginsCfg, flag

if flag == "sqlite":
    from sqlalchemy.dialects.sqlite import insert as ins
elif flag == "postgresql":
    from sqlalchemy.dialects.postgresql import insert as ins


async def get_plugins_cfg(
    space: int | None = None, name: str | None = None
) -> List[PyPluginsCfg] | None:
    session = ASession()
    stmt = select(PluginsCfg.__table__)
    stmt = anywhere(stmt, {(PluginsCfg.space, space), (PluginsCfg.plugin_name, name)})

    async with ASession() as session:
        res: List[NamedTuple] = (await session.execute(stmt)).all()
        if res:
            return [PyPluginsCfg.construct(**i._asdict()) for i in res]


async def ins_plugins_cfg_update(
    data: list[dict] | dict, ign=set(), all: set | None = None
):
    stmt = ins(PluginsCfg.__table__)
    stmt = stmt.on_conflict_do_update(
        index_elements=PyPluginsCfg.__primary_key__,
        set_=PyPluginsCfg.make_value(stmt, ign, all),
    )

    async with ASession() as session:
        await session.execute(stmt, data)
        await session.commit()


async def ins_plugins_cfg_ignore(data: List[Any]):
    stmt = ins(PluginsCfg.__table__)
    stmt = stmt.on_conflict_do_nothing()

    async with ASession() as session:
        await session.execute(stmt, data)
        await session.commit()


async def del_plugin_cfg(space: int | None = None, name: str | None = None):
    session = ASession()
    stmt = delete(PluginsCfg.__table__)
    stmt = anywhere(stmt, {(PluginsCfg.space, space), (PluginsCfg.plugin_name, name)})

    async with ASession() as session:
        await session.execute(stmt)
        await session.commit()
