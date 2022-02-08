from sqlalchemy import (
    Column,
    BigInteger,
    SmallInteger,
    UniqueConstraint,
    Integer,
    String,
)
from sqlalchemy.orm import declarative_base, declarative_mixin, declared_attr
from pydantic import BaseModel
from .state import DEFAULT_NONE_TYPE

Base = declarative_base()


@declarative_mixin
class Mixin:

    # * INFO
    space = Column(BigInteger, primary_key=True)
    channel = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, primary_key=True)
    plugin_name = Column(String, primary_key=True)

    # * CONFIGS
    ban = Column(SmallInteger)
    configure = Column(SmallInteger)
    coolen_time = Column(Integer)

    __table_args__ = (
        UniqueConstraint("space", "channel", "user_id", "plugin_name", name="plugin"),
    )
    __mapper_args__ = {"eager_defaults": True}


class PluginConfig(Base, Mixin):  # type: ignore
    __tablename__ = "_admin_plugin_config"


class PyPluginConfig(BaseModel):

    # * INFO
    space: int
    channel: int
    user_id: int
    plugin_name: str

    # * CONFIGS
    ban: int | None = None
    configure: int | None = None
    coolen_time: int | None = None


if __name__ == "__main__":
    from pprint import pprint

    r = PluginConfig.__table__.constraints
    for i in r:
        if isinstance(i, UniqueConstraint):
            print(i.name)
            for j in i.columns:
                print(j)
