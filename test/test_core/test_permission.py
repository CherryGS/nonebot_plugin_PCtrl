from random import choices, randint, sample

import pytest
from controller.core.permission import (
    PyUserPerm,
    UserPerm,
    del_perms,
    get_perms,
    insert_perm_after_query,
    insert_perm_ignore,
    insert_perm_update,
    merge_perm,
    set_perms,
)
from controller.methods import DISABLE_TYPE, ENABLE_TYPE, NO_TYPE
from pydantic import parse_obj_as
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

n = 200
string = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def randstr(l):
    return "".join(sample(string, l))


key_space = [i for i in range(n)]
key_space_same = [1 for _ in range(n)]
key_handle = [i for i in range(n)]
key_plugin_name = [randstr(30) for _ in range(n)]
old_ban = [NO_TYPE for _ in range(n)]
new_ban = [ENABLE_TYPE for _ in range(n)]
old_switch = [NO_TYPE for _ in range(n)]
new_switch = [ENABLE_TYPE for _ in range(n)]
old_configure = [NO_TYPE for _ in range(n)]
new_configure = [ENABLE_TYPE for _ in range(n)]

data1 = [
    PyUserPerm(
        space=i[0], handle=i[1], plugin_name=i[2], ban=i[3], switch=i[4], configure=i[5]
    ).dict()
    for i in zip(
        key_space, key_handle, key_plugin_name, old_ban, old_switch, old_configure
    )
]
data2 = [
    PyUserPerm(
        space=i[0], handle=i[1], plugin_name=i[2], ban=i[3], switch=i[4], configure=i[5]
    ).dict()
    for i in zip(
        key_space, key_handle, key_plugin_name, new_ban, old_switch, old_configure
    )
]
data3 = [
    PyUserPerm(
        space=i[0], handle=i[1], plugin_name=i[2], ban=i[3], switch=i[4], configure=i[5]
    ).dict()
    for i in zip(
        key_space_same, key_handle, key_plugin_name, new_ban, old_switch, old_configure
    )
]


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

    @pytest.mark.usefixtures("init_table", "insert_on_conflict")
    async def test_insert_perm_update(self, session: AsyncSession, engine_type: int):
        await insert_perm_update(engine_type, session, data1)
        async for i in self.query_data(session, data1):
            assert len(i) == 1
        async for i in self.query_data(session, data2):
            assert len(i) == 0

        await insert_perm_update(
            engine_type, session, data2, ign=("ban", "switch", "configure")
        )
        async for i in self.query_data(session, data1):
            assert len(i) == 1
        async for i in self.query_data(session, data2):
            assert len(i) == 0

        await insert_perm_update(engine_type, session, data2)
        async for i in self.query_data(session, data2):
            assert len(i) == 1
        async for i in self.query_data(session, data1):
            assert len(i) == 0

    @pytest.mark.usefixtures("init_table")
    async def test_set_perms(self, session: AsyncSession):
        await session.execute(insert(UserPerm.__table__), data1)
        await session.commit()

        await set_perms(session, ((UserPerm.ban, ENABLE_TYPE),))
        async for i in self.query_data(session, data2):
            assert len(i) == 1

        await set_perms(session, ((UserPerm.ban, NO_TYPE),))
        async for i in self.query_data(session, data1):
            assert len(i) == 1

    @pytest.mark.usefixtures("init_table")
    async def test_insert_perm_after_query(self, session: AsyncSession):
        await insert_perm_after_query(session, data1[: -int(n / 2)])
        async for i in self.query_data(session, data1[: -int(n / 2)]):
            assert len(i) == 1

        await insert_perm_after_query(session, data1)
        async for i in self.query_data(session, data1):
            assert len(i) == 1

    @pytest.mark.usefixtures("init_table")
    async def test_merge_perm(self, session: AsyncSession):
        await merge_perm(session, data1)
        async for i in self.query_data(session, data1):
            assert len(i) == 1

        await merge_perm(session, data2)
        async for i in self.query_data(session, data2):
            assert len(i) == 1

        async for i in self.query_data(session, data1):
            assert len(i) == 0

    @pytest.mark.usefixtures("init_table")
    async def test_get_perms(self, session: AsyncSession):
        await session.execute(insert(UserPerm.__table__), data3)
        await session.commit()

        res = await get_perms(session, key_space_same[0])
        assert res and len(res) == len(data3)

    @pytest.mark.usefixtures("init_table")
    async def test_del_perms(self, session: AsyncSession):
        await session.execute(insert(UserPerm.__table__), data3)
        await session.commit()
        await del_perms(session, key_space_same[0])
        res = (await session.execute(select(UserPerm.__table__))).all()
        assert not res
