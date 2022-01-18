from typing import List
from ...models import ASession, PluginsCfg, PyPluginsCfg
from sqlalchemy import select, delete


async def get_plugins_cfg(space: int, name: str) -> List[PyPluginsCfg] | None:
    tb = PluginsCfg.__table__
    session = ASession()
    stmt = select(tb).where(tb.c.space == space).where(tb.c.plugin_name == name)

    try:
        res: List[PyPluginsCfg] = (await session.execute(stmt)).scalars().first()
        if res:
            return [PyPluginsCfg.construct(**i.dict()) for i in res]
    except:
        raise
    finally:
        await session.close()


async def add_plugin_cfg(space: int, name: str, **kwargs):
    session = ASession()

    try:
        await session.merge(PluginsCfg(space=space, name=name, **kwargs))
        await session.commit()
    except:
        raise
    finally:
        await session.close()


async def del_plugin_cfg(space: int, name: str):
    session = ASession()
    stmt = (
        delete(PluginsCfg)
        .where(PluginsCfg.space == space)
        .where(PluginsCfg.plugin_name == name)
    )

    try:
        await session.execute(stmt)
        await session.commit()
    except:
        raise
    finally:
        await session.close()
