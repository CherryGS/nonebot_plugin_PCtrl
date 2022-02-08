from typing import Any
from .core import *
from sqlalchemy.ext.asyncio import AsyncSession
from .models import PyPluginConfig

__all__ = []


async def set_config(
    session: AsyncSession,
    space: int,
    channel: int,
    user_id: int,
    plugin_name: str,
    key: str,
    value: Any,
):
    await upsert(
        session,
        [
            PyPluginConfig(
                space=space,
                channel=channel,
                user_id=user_id,
                plugin_name=plugin_name,
                **{key: value}
            ).dict()
        ],
        allow={key},
    )
 