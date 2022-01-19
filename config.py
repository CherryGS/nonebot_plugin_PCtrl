from typing import List
from pydantic import BaseSettings


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


from nonebot import get_driver

conf = CtrlCfg(**get_driver().config.dict())


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
