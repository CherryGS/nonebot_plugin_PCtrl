from typing import List, NamedTuple

from sqlalchemy import delete, insert, select

from ...models import ASession, PluginsCfg, PyPluginsCfg, PyUserPerm, UserPerm


async def get_perms(space: int, handle: int, name: str) -> List[PyUserPerm] | None:
    session = ASession()
    tb = UserPerm.__table__
    stmt = (
        select(tb)
        .where(tb.c.space == space)
        .where(tb.c.handle == handle)
        .where(tb.c.plugin_name == name)
    )

    try:
        res: List[NamedTuple] = (await session.execute(stmt)).all()
        if res:
            return [PyUserPerm.construct(**i._asdict()) for i in res]
    except:
        raise
    finally:
        await session.close()
