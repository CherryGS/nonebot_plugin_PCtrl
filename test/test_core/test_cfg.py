from collections import namedtuple
from random import randint, sample, choices
from typing import Type

import pytest
from controller.core.cfg import (
    PluginsCfg,
    PyPluginsCfg,
    insert_cfg_after_query,
    insert_cfg_update,
    merge_plugins_cfg,
    get_plugins_cfg,
    del_plugin_cfg,
)
from pydantic import parse_obj_as
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert

n = 200
string = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def randstr(l):
    return "".join(sample(string, l))


def make_data(model: Type, siz: int, **kwargs):
    tp = namedtuple("np", list(kwargs.keys()))
    res = []
    for i in range(siz):
        res += [tp(*[j[i] for j in kwargs.values()])]
    obj = parse_obj_as(list[model], res)
    return [i.dict() for i in obj]


key_space = [i for i in range(n)]
key_space_same = [1 for _ in range(n)]
key_plugin_name = [randstr(30) for _ in range(n)]

old_coolen_time = [i for i in range(n)]
new_coolen_time = [i + 1 for i in range(n)]

data1 = make_data(
    PyPluginsCfg,
    n,
    space=key_space,
    plugin_name=key_plugin_name,
    coolen_time=old_coolen_time,
)

data2 = make_data(
    PyPluginsCfg,
    n,
    space=key_space,
    plugin_name=key_plugin_name,
    coolen_time=new_coolen_time,
)

data3 = make_data(
    PyPluginsCfg,
    n,
    space=key_space_same,
    plugin_name=key_plugin_name,
    coolen_time=old_coolen_time,
)


class Test:
    """"""

    async def query_data(self, session, data):
        for i in data:
            res = (
                await session.execute(
                    select(PluginsCfg.__table__)
                    .where(PluginsCfg.space == i["space"])
                    .where(PluginsCfg.plugin_name == i["plugin_name"])
                    .where(PluginsCfg.coolen_time == i["coolen_time"])
                )
            ).all()
            yield res

    @pytest.mark.usefixtures("init_table", "insert_on_conflict")
    async def test_insert_cfg_update(self, session: AsyncSession, engine_type: int):

        await insert_cfg_update(engine_type, session, data1)
        async for i in self.query_data(session, data1):
            assert len(i) == 1

        await insert_cfg_update(engine_type, session, data2, ign=("coolen_time",))
        async for i in self.query_data(session, data1):
            assert len(i) == 1

        await insert_cfg_update(engine_type, session, data2)
        async for i in self.query_data(session, data2):
            assert len(i) == 1

        async for i in self.query_data(session, data1):
            assert len(i) == 0

    @pytest.mark.usefixtures("init_table")
    async def test_insert_cfg_after_query(self, session: AsyncSession):
        await insert_cfg_after_query(session, data1[: -int(n / 2)])
        async for i in self.query_data(session, data1[: -int(n / 2)]):
            assert len(i) == 1

        await insert_cfg_after_query(session, data1)
        async for i in self.query_data(session, data1):
            assert len(i) == 1

    @pytest.mark.usefixtures("init_table")
    async def test_merge_plugins_cfg(self, session: AsyncSession):
        await merge_plugins_cfg(session, data1)
        async for i in self.query_data(session, data1):
            assert len(i) == 1

        await merge_plugins_cfg(session, data2)
        async for i in self.query_data(session, data2):
            assert len(i) == 1

        async for i in self.query_data(session, data1):
            assert len(i) == 0

    @pytest.mark.usefixtures("init_table")
    async def test_get_plugins_cfg_1(self, session: AsyncSession):
        await session.execute(insert(PluginsCfg.__table__), data1)
        await session.commit()

        randlist = choices(data1, k=int(n / 3))
        for i in randlist:
            res = await get_plugins_cfg(session, i["space"])
            assert res and len(res) == 1

    @pytest.mark.usefixtures("init_table")
    async def test_get_plugins_cfg_2(self, session: AsyncSession):
        await session.execute(insert(PluginsCfg.__table__), data3)
        await session.commit()

        res = await get_plugins_cfg(session, data3[0]["space"])

        assert res and len(res) == len(data3)

    @pytest.mark.usefixtures("init_table")
    async def test_del_plugins_cfg_1(self, session: AsyncSession):
        await session.execute(insert(PluginsCfg.__table__), data1)
        await session.commit()

        randlist = choices(data1, k=int(n / 3))
        for i in randlist:
            await del_plugin_cfg(session, i["space"])
            res = await get_plugins_cfg(session, i["space"])
            assert not res or len(res) == 0

    @pytest.mark.usefixtures("init_table")
    async def test_del_plugins_cfg_2(self, session: AsyncSession):
        await session.execute(insert(PluginsCfg.__table__), data3)
        await session.commit()
        await del_plugin_cfg(session, data3[0]["space"])
        res = (await session.execute(select(PluginsCfg.__table__))).all()

        assert not res
