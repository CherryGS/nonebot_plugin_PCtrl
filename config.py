from typing import List
from pydantic import BaseSettings
from nonebot import get_driver


class CtrlCfg(BaseSettings):
    """
    整体配置文件规范
    """

    # 基本配置
    reply_id: int  # 报告信息的群聊号码
    bot_name: str | List[str] = "小小"
    debug: bool = False
    plugin_cfg_file: str = "secure.json"  # 使用json格式

    # 数据库配置
    db_link: str = "sqlite+aiosqlite:///admin.sqlite"

    # 默认权限配置
    default_ban: bool = False
    default_switch: bool = False
    default_configure: bool = False

    class Config:
        extra = "ignore"


class PluginCfg(BaseSettings):
    """
    单插件配置文件规范
    """

    ignore_global_control: bool = False
    space: int = 0  # 该插件作用命名空间(默认为全局,其他值为群聊号码)
    is_start: bool = True
    coolen_time: int = 0

    class Config:
        extra = "ignore"


class GlobalSet(BaseSettings):
    """
    有 8 种情况 , 重要程度 `space` > `handle` > `plugin_name`

    Args:
        `BaseSettings` : [description]
    """

    space: int = 0  # 全局空间代表 (一般为群名)
    handle: int = 0  # 全局 handle 代表 (一般为QQ名)
    name: str = "_1"  # 全局插件名代表


class SubPermSet(BaseSettings):
    lv: int  # 该权限在 perm 的第几位


class PermSet(BaseSettings):
    ban: SubPermSet  # 是否被ban
    switch: SubPermSet  # 是否允许开关插件
    configure: SubPermSet  # 是否允许修改配置


conf = CtrlCfg(**get_driver().config.dict())

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


my = PermSet(**perm)  # type: ignore

gbname = GlobalSet()

default_perm = (
    (conf.default_ban << my.ban.lv)
    + (conf.default_switch << my.switch.lv)
    + (conf.default_configure << my.configure.lv)
)
