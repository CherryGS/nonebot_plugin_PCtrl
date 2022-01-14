from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import BigInteger, Boolean, String
from . import _Base


class pluginsCfg(_Base):
    __tablename__ = "_admin_plugins_global_cfg"

    plugin_name = Column(String, primary_key=True)
    is_start = Column(Boolean, default=True)
    coolen_time = Column(BigInteger, default=0)

    __mapper_args__ = {"eager_defaults": True}


class pluginsBan(_Base):
    __tablename__ = "_admin_plugins_global_ban"

    ban_type = Column(BigInteger, primary_key=True)
    handle = Column(BigInteger, primary_key=True)
    plugin_name = Column(String, primary_key=True)

    __mapper_args__ = {"eager_defaults": True}


class pluginsCoolen(_Base):
    __tablename__ = "_admin_plugins_global_coolen"

    plugin_name = Column(String, primary_key=True)
    latest_time = Column(BigInteger)

    __mapper_args__ = {"eager_defaults": True}


if __name__ == "__main__":
    pass
