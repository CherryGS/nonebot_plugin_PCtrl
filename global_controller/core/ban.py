from typing import Any, List

from sqlalchemy.sql.expression import select, delete
from sqlalchemy import func

from ...models import ASession, PluginsBan, PyPluginsBan


async def get_plugin_ban(
    space: int, ban_type: int, handle: int, name: str
) -> PyPluginsBan | None:
    """
    根据 ban 的 primary key 获取唯一行

    Args:
        `space` : 命名空间 (全局/群/...)
        `ban_type` : ban 类型
        `handle` : 标识符
        `name` : 插件名称

    """
    session = ASession()
    stmt = (
        select(PluginsBan)
        .where(PluginsBan.space == space)
        .where(PluginsBan.ban_type == ban_type)
        .where(PluginsBan.handle == handle)
        .where(PluginsBan.plugin_name == name)
        .limit(1)
    )

    try:
        res = (await session.execute(stmt)).scalars().first()
        if res:
            return PyPluginsBan.from_orm(res)
        return None
    except:
        raise
    finally:
        await session.close()


async def check_plugin_ban(ban_type: int, handle: int, name: str) -> bool:
    session = ASession()
    stmt = (
        select(PluginsBan)
        .where(PluginsBan.ban_type == ban_type)
        .where(PluginsBan.handle == handle)
        .where(PluginsBan.plugin_name == name)
        .limit(1)
    )

    try:
        res = (await session.execute(stmt)).scalars().first()
        return bool(res)
    except:
        raise
    finally:
        await session.close()


async def set_plugin_ban(ban_type: int, handle: int, name: str, **kwargs: Any):
    """
    设置 ban , 重复则覆盖

    Args:
        `ban_type` : ban 类型
        `handle` : 识别名称
        `name` : 插件名称
    """
    session = ASession()
    data = PyPluginsBan(ban_type=ban_type, handle=handle, plugin_name=name, **kwargs)
    obj = PluginsBan(**data.dict())

    try:
        await session.merge(obj)
        await session.commit()
    except:
        raise
    finally:
        await session.close()


async def list_plugin_ban() -> List[PyPluginsBan]:
    session = ASession()
    stmt = select(PluginsBan)

    try:
        res = (await session.execute(stmt)).scalars().all()
        return [PyPluginsBan.from_orm(i) for i in res]
    except:
        raise
    finally:
        await session.close()


async def del_plugin_ban(ban_type: int, handle: int, name: str):
    session = ASession()
    stmt = (
        delete(PluginsBan)
        .where(PluginsBan.ban_type == ban_type)
        .where(PluginsBan.handle == handle)
        .where(PluginsBan.plugin_name == name)
    )
    try:
        await session.execute(stmt)
        await session.commit()
    except:
        raise
    finally:
        await session.close()
