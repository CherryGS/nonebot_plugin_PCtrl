from typing import Any, Dict, List, NamedTuple

from sqlalchemy import delete, select

from anyutils import anywhere

from ...models import ASession, PluginsCfg, PyPluginsCfg, flag

if flag is "sqlite":
    from sqlalchemy.dialects.sqlite import insert as ins
elif flag is "postgresql":
    from sqlalchemy.dialects.postgresql import insert as ins


async def get_plugins_cfg(
    space: int | None = None, name: str | None = None
) -> List[PyPluginsCfg] | None:
    session = ASession()
    stmt = select(PluginsCfg.__table__)

    if space is not None:
        stmt = stmt.where(PluginsCfg.space == space)
    if name is not None:
        stmt = stmt.where(PluginsCfg.plugin_name == name)

    async with ASession() as session:
        res: List[NamedTuple] = (await session.execute(stmt)).all()
        if res:
            return [PyPluginsCfg.construct(**i._asdict()) for i in res]


async def ins_plugins_cfg_update(data: List[Dict[str, Any]]):
    stmt = ins(PluginsCfg.__table__)  # type: ignore
    stmt = stmt.on_conflict_do_update(
        index_elements=PyPluginsCfg.__primary_key__,
        set_=PyPluginsCfg.make_value(stmt),
    )

    async with ASession() as session:
        await session.execute(stmt, data)
        await session.commit()


async def ins_plugins_cfg_ignore(data: List[Any]):
    stmt = ins(PluginsCfg.__table__)  # type: ignore
    stmt = stmt.on_conflict_do_nothing()

    async with ASession() as session:
        await session.execute(stmt, data)
        await session.commit()


async def ups_plugin_cfg(space: int, name: str, **kwargs):
    session = ASession()

    async with ASession() as session:
        await session.merge(PluginsCfg(space=space, name=name, **kwargs))
        await session.commit()


async def del_plugin_cfg(space: int | None = None, name: str | None = None):
    session = ASession()
    stmt = delete(PluginsCfg.__table__)
    stmt = await anywhere(
        stmt, ((PluginsCfg.space, space), (PluginsCfg.plugin_name, name))
    )

    async with ASession() as session:
        await session.execute(stmt)
        await session.commit()
