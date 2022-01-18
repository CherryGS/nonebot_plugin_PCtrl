from typing import Optional
from anyutils import ModelConfig
from pydantic import BaseModel
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import BigInteger, Boolean, String, Integer

from . import Base


class UserPerm(Base):
    """
    `perm_type` :
        1. 是否允许使用
        2. 是否允许开关
        3. 是否允许修改配置
    """

    __tablename__ = "_admin_user_permissions"

    space = Column(BigInteger, primary_key=True)
    handle = Column(BigInteger, primary_key=True)
    plugin_name = Column(String, primary_key=True)
    perm_type = Column(BigInteger)


class PyUserPerm(BaseModel):

    space: int
    handle: int
    plugin_name: str
    perm_type: Optional[int]

    __primary_key__ = ["space", "handle", "plugin_name"]

    class Config(ModelConfig):
        pass
