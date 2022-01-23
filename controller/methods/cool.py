from sqlalchemy.ext.asyncio import AsyncSession

from ..core import get_plugins_cfg


async def load_cool_config(session: AsyncSession) -> dict[tuple[int, str], int]:
    res = await get_plugins_cfg(session)
    if not res:
        raise ValueError("No cool config found")
    dic = {(i.space, i.plugin_name): i.coolen_time for i in res}
    return dic
