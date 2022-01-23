from pydantic import BaseSettings


class CtrlCfg(BaseSettings):
    """
    整体配置文件规范
    """

    # 基本配置
    reply_id: int  # 报告一些管理相关信息的群聊号码
    bot_name: str | list[str] = "小小"  # bot名字,管理时使用
    debug: bool = False  # 是否开启 `debug` 模式 (影响`sqla`的`echo`设置)
    ignore_global_control: set[str] = set()

    # 数据库配置
    db_link: str = "sqlite+aiosqlite:///admin.sqlite"

    # 默认插件权限配置 , 对于没有配置文件的插件生效
    default_ban: bool = False
    default_configure: bool = False

    class Config:
        extra = "forbid"


class PluginCfg(BaseSettings):
    """
    单插件配置文件规范

    Args:
        `ignore_global_control` : 是否忽略管控
        `is_start` : 是否默认已启动
        `coolen_time` : 冷却时长
    """

    space: int
    coolen_time: int = 0

    class Config:
        extra = "forbid"


class config(BaseSettings):
    basic: CtrlCfg
    plugins: dict[str, list[PluginCfg]]
