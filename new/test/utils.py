import uuid

from sqlalchemy.orm import registry, declarative_mixin, DeclarativeMeta
from sqlalchemy.ext.asyncio import AsyncEngine


class AutoTable:
    @staticmethod
    def get_base():
        mapper_registry = registry()

        class Base(metaclass=DeclarativeMeta):
            __abstract__ = True

            registry = mapper_registry
            metadata = mapper_registry.metadata

            __init__ = mapper_registry.constructor

        return Base

    @staticmethod
    def get_table(name, table, base):
        class tb(table, base):
            __tablename__ = name

        return tb

    def __init__(self, table, engine: AsyncEngine):
        """
        使用 `declarative_mixin` 构造随机名字的 `table`
        """
        r = uuid.uuid1()
        self.engine = engine
        self.base = self.get_base()
        self.random_table = type(
            str(r),
            (self.base, table),
            {"__tablename__": r},  # type: ignore
        )
        # self.random_table = self.get_table(r, table, self.base)

    async def __aenter__(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(self.base.metadata.drop_all)
        async with self.engine.begin() as conn:
            await conn.run_sync(self.base.metadata.create_all)

        return self.random_table

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        async with self.engine.begin() as conn:
            await conn.run_sync(self.base.metadata.drop_all)
