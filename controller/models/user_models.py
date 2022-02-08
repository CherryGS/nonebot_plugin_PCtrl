from anyutils import ModelConfig, BsModel
from pydantic import Field
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import BigInteger, String, SmallInteger

from . import Base


class UserPerm(Base):

    __tablename__ = "_admin_user_permissions"

    space = Column(BigInteger, primary_key=True)
    handle = Column(BigInteger, primary_key=True)
    plugin_name = Column(String, primary_key=True)
    ban = Column(SmallInteger)
    switch = Column(SmallInteger)
    configure = Column(SmallInteger)


class PyUserPerm(BsModel):

    space: int = Field(pk=True)
    handle: int = Field(pk=True)
    plugin_name: str = Field(pk=True)
    ban: int = 0
    switch: int = 0
    configure: int = 0

    class Config(ModelConfig):
        pass


PyUserPerm.check_pk(UserPerm)
