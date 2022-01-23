import sqlalchemy.dialects.postgresql as po
import sqlalchemy.dialects.sqlite as sq

from .config import ENGINE_POSTGRESQL, ENGINE_SQLITE, ENGINE_MYSQL


def get_engine_type_by_name(name: str) -> int:
    if name == "sqlite":
        return ENGINE_SQLITE
    elif name == "postgresql":
        return ENGINE_POSTGRESQL
    elif name == "mysql":
        return ENGINE_MYSQL
    else:
        raise ValueError(f"name={name}")


def get_engine_type_dial(flag: int):
    if flag == ENGINE_SQLITE:
        return sq
    elif flag == ENGINE_POSTGRESQL:
        return po
    else:
        raise ValueError(f"flag={flag}")
