from typing import Any, Optional, Dict
from anyutils import ModelConfig
from pydantic import BaseModel, Field
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import BigInteger, Boolean, String, Integer
from sqlalchemy import text

from . import Base, BsModel


class PluginsCfg(Base):
    __tablename__ = "_admin_plugins_global_cfg"

    space = Column(BigInteger, primary_key=True)
    plugin_name = Column(String, primary_key=True)
    is_start = Column(Boolean, server_default=text("True"))
    coolen_time = Column(BigInteger, server_default=text("0"))
    latest_time = Column(BigInteger, server_default=text("0"))

    __mapper_args__ = {"eager_defaults": True}


class PyPluginsCfg(BsModel):

    space: int = Field(pk=True)
    plugin_name: str = Field(pk=True)
    is_start: bool
    coolen_time: int
    latest_time: int = 0

    class Config(ModelConfig):
        pass


PyPluginsCfg.check_pk(PluginsCfg)


if __name__ == "__main__":
    pass
