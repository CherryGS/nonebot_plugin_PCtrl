from typing import Optional
from anyutils import ModelConfig
from pydantic import BaseModel
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import BigInteger, Boolean, String, Integer

from . import Base


class PluginsCfg(Base):
    __tablename__ = "_admin_plugins_global_cfg"

    space = Column(BigInteger, primary_key=True)
    plugin_name = Column(String, primary_key=True)
    is_start = Column(Boolean, server_default=True)
    coolen_time = Column(BigInteger, server_default=0)
    latest_time = Column(BigInteger, server_default=0)

    __mapper_args__ = {"eager_defaults": True}


class PyPluginsCfg(BaseModel):

    space: int
    plugin_name: str
    is_start: Optional[bool]
    coolen_time: Optional[int]
    latest_time: Optional[int]

    __primary_key__ = ["space", "plugin_name"]

    class Config(ModelConfig):
        pass


class PluginsBan(Base):
    __tablename__ = "_admin_plugins_global_ban"

    space = Column(BigInteger, primary_key=True)
    ban_type = Column(BigInteger, primary_key=True)
    handle = Column(BigInteger, primary_key=True)
    plugin_name = Column(String, primary_key=True)

    __mapper_args__ = {"eager_defaults": True}


class PyPluginsBan(BaseModel):

    space: int
    ban_type: int
    handle: int
    plugin_name: str

    __primary_key__ = ["space", "ban_type", "handle", "plugin_name"]

    class Config(ModelConfig):
        pass


if __name__ == "__main__":
    pass
