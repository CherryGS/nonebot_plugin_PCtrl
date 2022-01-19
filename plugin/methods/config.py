from pydantic import BaseSettings
from ... import conf

perm = {
    "ban": {
        "lv": 0,
    },
    "switch": {
        "lv": 1,
    },
    "configure": {
        "lv": 2,
    },
}


class SubPermSet(BaseSettings):
    lv: int  # 该权限在 perm 的第几位


class PermSet(BaseSettings):
    ban: SubPermSet  # 是否被ban
    switch: SubPermSet  # 是否允许开关插件
    configure: SubPermSet  # 是否允许修改配置


my = PermSet(**perm)  # type: ignore


class GlobalSet(BaseSettings):
    """
    有 8 种情况 , 重要程度 `space` > `handle` > `plugin_name`

    Args:
        `BaseSettings` : [description]
    """

    space: int = 0  # 全局空间代表
    handle: int = 0  # 全局 handle 代表
    name: str = "_1"  # 全局插件名代表


gbname = GlobalSet()

default_perm = (
    (conf.default_ban << my.ban.lv)
    + (conf.default_switch << my.switch.lv)
    + (conf.default_configure << my.configure.lv)
)
