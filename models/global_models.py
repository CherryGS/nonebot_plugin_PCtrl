from anyutils import ModelConfig
from pydantic import BaseModel
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import BigInteger, Boolean, String, Integer

from . import Base


class PluginsCfg(Base):
    __tablename__ = "_admin_plugins_global_cfg"

    space = Column(Integer, primary_key=True)
    plugin_name = Column(String, primary_key=True)
    is_start = Column(Boolean, server_default=True)
    coolen_time = Column(BigInteger, server_default=0)

    __mapper_args__ = {"eager_defaults": True}


class PyPluginsCfg(BaseModel):

    space: int
    plugin_name: str
    is_start: bool
    coolen_time: int

    class Config(ModelConfig):
        pass


class PluginsBan(Base):
    __tablename__ = "_admin_plugins_global_ban"

    space = Column(Integer, primary_key=True)
    ban_type = Column(Integer, primary_key=True)
    handle = Column(BigInteger, primary_key=True)
    plugin_name = Column(String, primary_key=True)

    __mapper_args__ = {"eager_defaults": True}


class PyPluginsBan(BaseModel):

    space: int
    ban_type: int
    handle: int
    plugin_name: str

    class Config(ModelConfig):
        pass


class PluginsCooling(Base):
    __tablename__ = "_admin_plugins_global_coolen"

    space = Column(Integer, primary_key=True)
    plugin_name = Column(String, primary_key=True)
    latest_time = Column(BigInteger)

    __mapper_args__ = {"eager_defaults": True}


class PyPluginsCooling(BaseModel):

    space: int
    plugin_name: str
    latest_time: int

    class Config(ModelConfig):
        pass


if __name__ == "__main__":
    pass
