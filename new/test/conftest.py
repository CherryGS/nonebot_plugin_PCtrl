from typing import Callable
import uuid
import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import sessionmaker


def pytest_addoption(parser):
    parser.addoption(
        "--db_choice",
        action="store",
        default="sqlite",
        help="type of database to use \n sqlite/sqlitememory/postgres/mysql",
    )
    parser.addini(name="postgresql_db_url", help="postgresql db_url", type="string")
    parser.addini(name="mysql_db_url", help="mysql db_url ", type="string")


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def engine(request, tmpdir):
    choice = request.config.getoption("--db_choice")
    db_url = None

    if choice == "sqlite":
        db_url = f"sqlite+aiosqlite:///{tmpdir}/{uuid.uuid1()}.sqlite"
    elif choice == "postgres":
        db_url = request.config.getini("postgresql_db_url")
    elif choice == "mysql":
        db_url = request.config.getini("mysql_db_url")
    engine: AsyncEngine = create_async_engine(db_url, future=True)

    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def ASession(engine):
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    yield async_session


@pytest.fixture(scope="function")
async def session(ASession: Callable[..., AsyncSession]):
    async with ASession() as a:
        yield a
