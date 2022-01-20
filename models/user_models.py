from anyutils import ModelConfig
from pydantic import Field
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import BigInteger, String

from . import Base, BsModel


class UserPerm(Base):
    """
    `perm_type` : 每一个二进制位代表一种权限情况
    """

    __tablename__ = "_admin_user_permissions"

    space = Column(BigInteger, primary_key=True)
    handle = Column(BigInteger, primary_key=True)
    plugin_name = Column(String, primary_key=True)
    perm_type = Column(BigInteger)


class PyUserPerm(BsModel):

    space: int = Field(pk=True)
    handle: int = Field(pk=True)
    plugin_name: str = Field(pk=True)
    perm_type: int

    __primary_key__ = {"space", "handle", "plugin_name"}

    class Config(ModelConfig):
        pass
