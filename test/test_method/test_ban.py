import pytest
from controller.methods.ban import check_ban, del_type, get_all_ban, set_ban
from controller.methods.config import (
    GLOBAL_PLUGIN_NAME,
    DISABLE_TYPE,
    GLOBAL_HANDLE,
    GLOBAL_SPACE,
    NO_TYPE,
    ENABLE_TYPE,
)
from controller.models import PyUserPerm, UserPerm
from controller import NoConfigError
from pydantic import parse_obj_as
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

key_space = [
    GLOBAL_SPACE,
    GLOBAL_SPACE,
    GLOBAL_SPACE,
    GLOBAL_SPACE,
    233,
    233,
    233,
    233,
]
key_handle = [
    GLOBAL_HANDLE,
    GLOBAL_HANDLE,
    233,
    233,
    GLOBAL_HANDLE,
    GLOBAL_HANDLE,
    233,
    233,
]
key_plugin_name = [
    GLOBAL_PLUGIN_NAME,
    "233",
    GLOBAL_PLUGIN_NAME,
    "233",
    GLOBAL_PLUGIN_NAME,
    "233",
    GLOBAL_PLUGIN_NAME,
    "233",
]


data = [
    PyUserPerm(
        space=i[0], handle=i[1], plugin_name=i[2], ban=i[3], switch=i[4], configure=i[5]
    ).dict()
    for i in zip(
        key_space,
        key_handle,
        key_plugin_name,
        [ENABLE_TYPE for _ in range(8)],
        [NO_TYPE for _ in range(8)],
        [NO_TYPE for _ in range(8)],
    )
]


@pytest.mark.usefixtures("init_table")
class Test:
    """"""

    async def query_data(self, session, data):
        for i in data:
            res = (
                await session.execute(
                    select(UserPerm.__table__)
                    .where(UserPerm.space == i["space"])
                    .where(UserPerm.plugin_name == i["plugin_name"])
                    .where(UserPerm.handle == i["handle"])
                    .where(UserPerm.ban == i["ban"])
                    .where(UserPerm.switch == i["switch"])
                    .where(UserPerm.configure == i["configure"])
                )
            ).all()
            yield res

    async def test_set_ban(self, session: AsyncSession, engine_type: int):
        for i in data:
            await set_ban(
                engine_type, session, i["space"], i["handle"], i["plugin_name"]
            )
        async for i in self.query_data(session, data):
            assert len(i) == 1

    async def test_del_type(self, session: AsyncSession, engine_type: int):
        for i in data:
            await set_ban(
                engine_type, session, i["space"], i["handle"], i["plugin_name"]
            )
        for i in data:
            await del_type(
                engine_type, session, i["space"], i["handle"], i["plugin_name"]
            )
        async for i in self.query_data(session, data):
            assert len(i) == 0

    async def test_check_ban(self, session: AsyncSession, engine_type: int):
        with pytest.raises(NoConfigError):
            await check_ban(
                session, data[0]["space"], data[0]["handle"], data[0]["plugin_name"]
            )
        for i in data:

            await set_ban(
                engine_type, session, i["space"], i["handle"], i["plugin_name"]
            )

            res = await check_ban(session, i["space"], i["handle"], i["plugin_name"])
            assert res == True

            res = await check_ban(session, 233, 233, "233")
            assert res == True

            await del_type(
                engine_type, session, i["space"], i["handle"], i["plugin_name"]
            )
            with pytest.raises(NoConfigError):
                await check_ban(session, 233, 233, "233")
