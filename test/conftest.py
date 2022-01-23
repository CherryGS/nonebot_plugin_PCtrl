import asyncio

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import sessionmaker
from controller.models import init, dele


def pytest_addoption(parser):
    parser.addoption(
        "--db_choice",
        action="store",
        default="sqlite",
        help="type of database to use \n sqlite/sqlitememo/postgres/mysql",
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


@pytest.fixture(scope="session")
async def engine(request):
    choice = request.config.getoption("--db_choice")
    db_url = None

    if choice == "sqlite":
        db_url = f"sqlite+aiosqlite:///test.sqlite"
    elif choice == "sqlitememo":
        db_url = "sqlite+aiosqlite:///:memory:"
    elif choice == "postgres":
        db_url = request.config.getini("postgresql_db_url")
    elif choice == "mysql":
        db_url = request.config.getini("mysql_db_url")
    print(db_url)

    engine: AsyncEngine = create_async_engine(db_url, future=True)

    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
def Session(engine: AsyncEngine):
    ASession = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    yield ASession


@pytest.fixture(scope="session")
async def session(Session: sessionmaker):
    session = Session()
    yield session
    await session.close()


@pytest.fixture(scope="function")
async def init_table(engine: AsyncEngine):
    await init(engine)
    yield
    await dele(engine)
