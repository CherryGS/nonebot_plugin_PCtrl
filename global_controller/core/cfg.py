from ...models import ASession, PluginsCfg, PyPluginsCfg
from sqlalchemy import select


async def get_plugin_cfg(name: str) -> PyPluginsCfg | None:
    session = ASession()
    stmt = select(PluginsCfg).where(PluginsCfg.plugin_name == name).limit(1)

    try:
        res = (await session.execute(stmt)).scalars().first()
        if res:
            return PyPluginsCfg.from_orm(res)
        return None
    except:
        raise
    finally:
        await session.close()


async def check_plugin_exist(name: str) -> bool:
    return bool(await get_plugin_cfg(name))
