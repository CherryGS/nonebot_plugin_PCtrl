# Plugins controller for nonebot2
## 简介

基于 Hook 的插件管理器 , 提供常用的管理功能

使用异步 SQLAlchemy 方言实现持久化

功能持续增加中

## 计划

- [X] 全局插件开关
- [X] 全局ban人/群
- [X] 全局冷却时间
- [X] 冷却时间信息显示与命令修改

> 欢迎 issue 提出更多需求

## 使用说明

1. 本插件初始化于 `websocket` 连接时 , http协议上报未经测试
2. 导入时**注意大小写** `nonebot_plugin_PCtrl`
3. 所有命令只能由 `SUPERUSER` 激活
4. 数据库初始化未完成之前所有事件(除元事件)都会被忽略

## 功能

### global.switch

- `/listplugins` 列出所有受控的插件的插件名称和开启状态
- `/setplugin -p plugin_name` 将插件名为 `plugin_name` 的插件的开启状态反向

### global.ban

- `/listban` 列出存在的 ban 的信息
- `/ban -u handle -p plugin_name` ban 掉 QQ 号为 `handle` 的人使用名称为 `plugin_name` 插件的权限
- `/ban -g handle -p plugin_name` ban 掉群号为 `handle` 的群使用名称为 `plugin_name` 插件的权限
> 如果在群内执行 , 可以省略参数 `-g` , 会自动识别为该群
- `/unban -u handle -p plugin_name` 取消 ban
- `/unban -g handle -p plugin_name` 取消 ban

### global.cool

本部分提供三个级别的控制 , plugin , matcher , function

对于插件级别的控制 , 通过 nonebot2 提供的跨插件方法导出属性 `coolen_time = seconds` 其中 `seconds` 为冷却时间(s)

```py
from nonebot.plugin import export
_export = export()
_export.coolen_time = 5 # 冷却时间为 5s
```

对于 matcher 级别的控制 , 导出函数 `coolen_matcher(times, matcher)`
```py
from nonebot.plugin import require
_req = require("nonebot_plugin_PCtrl")
_cmd = _req.coolen_matcher(5, on_keyword({"jls", "jiangly"}, priority=10)) # 对一个 matcher 启用冷却
@_cmd.handle()
async def _(bot, event, state): pass
```

对于 function 级别的控制 , 通过跨插件方法导入插件提供的装饰器 `coolen_async(times, True/False)`
```py
from nonebot.plugin import require
_req = require("admin.nonebot_plugin_PCtrl")
coolen_async = _req.coolen_async

# handle,run_preprocessor,got 等有着固定参数名称要求的第二维请填 True
@some_matcher.handle()
@coolen_async(5, True)
async def _(bot, event, state): pass

# 其余填 False
@coolen_async(5, False)
async def _(*args, **kwargs): pass
```

对于插件级别的冷却控制还有一些指令

`/listcool` 显示当前插件级别冷却配置

`/setcool -p plugin_name -t times` 设置插件冷却时间

> :warning: 通过当前命令设置的冷却时间会被插件配置覆盖(如果有)

## 配置
请添加到 nonebot2 配置文件中
```ini
##### Plugins Controller ######
# 数据库配置(SQLAlchemy任意异步) ! 该选项会覆盖上述数据库配置
## 数据库链接(请参考SQLAlchemy官方文档) 
## url: https://docs.sqlalchemy.org/en/14/tutorial/engine.html#establishing-connectivity-the-engine
## 下面是一个例子
plugin_pctrl_db=sqlite+aiosqlite:///_my_admin.db
## 如果真的想将该插件信息和其他插件共用库 , 请确保构造的是 SQLAlchemy 的异步的 AsyncEngine
## 并且在该插件初始化前向全局设置传入 AsyncEngine , 设置 `get_driver().config.AEngine = your_AsyncEngine`
## 需要注意的是 , 该设置优先于传入的 AsyncEngine
# 冷却相关配置
## 是否启用全局 reply , 启用后 , 如果调用在冷却中的函数 , 会尝试向调用主体(人/群)发送剩余冷却时长
## 为空则不启用 , 否则需要填一个大于 0 的数字 , 代表发送剩余冷却时长的冷却时长
coolen_time_reply=
###############################
```

测试过的方言 , 使用前请安装相关依赖 
1. `postgresql+asyncpg` 需要安装 `asyncpg`
2. `sqlite+aiosqlite` 默认依赖
## 忽略管控

对于不想被此插件管控的插件 , 请使用 nonebot2 提供的跨插件方法导出属性 `ignore_global_control = True`
```py
from nonebot.plugin import export
_export = export()
_export.ignore_global_control = True
```

## 特别感谢

[nonebot2](https://github.com/nonebot/nonebot2) : 优秀的跨平台 python 异步机器人框架

[SQLAlchemy](https://www.sqlalchemy.org/) : 完善~~文档根本看不懂~~的 ORM

## 部分更新

- `0.1.6` : 全局冷却功能完成
- `0.1.8` : 冷却时间信息显示与命令修改功能完成