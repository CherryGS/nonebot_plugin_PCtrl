from typing import Any, Optional, Dict
from anyutils import ModelConfig
from pydantic import BaseModel
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

    space: int
    plugin_name: str
    is_start: bool
    coolen_time: int
    latest_time: int = 0

    __primary_key__ = {"space", "plugin_name"}

    def __hash__(self):
        return hash(tuple(self.dict(include=self.__primary_key__).values()))

    def __eq__(self, other):
        return (
            self.dict(include=self.__primary_key__).values()
            == other.dict(include=other.__primary_key__).values()
        )

    @classmethod
    def make_value(cls, stmt, spec: str | None = None) -> Dict:
        if spec:
            return dict(spec=eval(f"stmt.excluded.{spec}"))
        r = dict()
        for i in cls.__dict__["__fields__"].keys():
            if i not in cls.__primary_key__:
                r[i] = eval(f"stmt.excluded.{i}")
        return r

    class Config(ModelConfig):
        pass


if __name__ == "__main__":
    pass
