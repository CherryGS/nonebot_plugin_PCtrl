from anyutils import ModelConfig, BsModel
from pydantic import Field
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import BigInteger, Boolean, String
from sqlalchemy import text

from . import Base


class PluginsCfg(Base):
    __tablename__ = "_admin_plugins_global_cfg"

    space = Column(BigInteger, primary_key=True)
    plugin_name = Column(String, primary_key=True)
    coolen_time = Column(BigInteger, server_default=text("0"))

    __mapper_args__ = {"eager_defaults": True}


class PyPluginsCfg(BsModel):

    space: int = Field(pk=True)
    plugin_name: str = Field(pk=True)
    coolen_time: int = 0

    class Config(ModelConfig):
        pass


PyPluginsCfg.check_pk(PluginsCfg)
