from typing import Dict, Optional
from anyutils import ModelConfig
from pydantic import BaseModel
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import BigInteger, Boolean, String, Integer

from . import Base


class UserPerm(Base):
    """
    `perm_type` : 每一个二进制位代表一种权限情况
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
    perm_type: int

    __primary_key__ = ["space", "handle", "plugin_name"]

    def __hash__(self):
        return hash(tuple(self.__primary_key__))

    def __eq__(self, other):
        return set(self.__primary_key__) == set(other.__primary_key)

    @classmethod
    def make_value(cls, stmt, spec: str | None = None) -> Dict:
        if spec:
            if spec not in cls.__dict__["__fields__"].keys():
                raise KeyError(f"{spec} not in __fields__")
            return dict(spec=eval(f"stmt.excluded.{spec}"))
        r = dict()
        for i in cls.__dict__["__fields__"].keys():
            if i not in cls.__primary_key__:
                r[i] = eval(f"stmt.excluded.{i}")
        return r

    class Config(ModelConfig):
        pass
