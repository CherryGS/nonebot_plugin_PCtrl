from sqlalchemy import select, update
from ..models import PluginsCfg, PyPluginsCfg, ASession


async def get_latest_time(space: int, name: str) -> int:
    session = ASession()
    stmt = (
        select(PluginsCfg)
        .where(PluginsCfg.space == space)
        .where(PluginsCfg.plugin_name == name)
        .limit(1)
    )
    try:
        res: PluginsCfg = (await session.execute(stmt)).scalars().first()
        return res.latest_time
    except:
        raise
    finally:
        await session.close()


async def set_latest_time(space: int, name: str, tim: int):
    session = ASession()
    stmt = (
        update(PluginsCfg)
        .where(PluginsCfg.space == space)
        .where(PluginsCfg.plugin_name == name)
        .values(latest_time=tim)
    )
    try:
        await session.execute(stmt)
    except:
        raise
    finally:
        await session.close()
