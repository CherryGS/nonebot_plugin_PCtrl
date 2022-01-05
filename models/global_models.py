from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import BigInteger, Boolean, Integer, String
from . import Base

__all__ = []


class pluginsCfg(Base):
    __tablename__ = "_admin_plugins_global_cfg"

    plugin_name: str = Column(String, unique=True, primary_key=True)
    is_start: bool = Column(Boolean, default=1)

    __mapper_args__ = {"eager_defaults": True}


class pluginsBan(Base):
    __tablename__ = "_admin_plugins_global_ban"

    ban_type: int = Column(BigInteger, primary_key=True)
    handle: int = Column(BigInteger, primary_key=True)
    plugin_name: str = Column(String, primary_key=True)

    __mapper_args__ = {"eager_defaults": True}


if __name__ == "__main__":
    pass
