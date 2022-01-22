# Plugins controller for nonebot2
## 简介

基于 Hook 的插件管理器 , 提供常用的管理功能

使用异步 SQLAlchemy 方言实现持久化

功能持续增加中

## 计划

- [X] ~~全局插件开关~~ 可以通过设置`ban`来实现
- [X] 设置`ban`人/群或人群
- [X] 设置冷却时间(通过配置文件)
- [X] 适配b1
- [X] 模块化
- [X] 使用 `core` + `pydantic` 代替 `ORM`
- [ ] 冷却时间信息显示与命令修改

> 欢迎 issue 提出更多需求

## 使用说明

1. 本插件初始化于 `websocket` 连接时 , http协议上报未经测试
2. 导入时**注意大小写** `nonebot_plugin_PCtrl`
3. 所有命令只能由 `SUPERUSER` 激活
4. 数据库初始化未完成之前所有事件(除元事件)都会被忽略

## 功能
### ban

- `/listban` 列出存在的 ban 的信息
- `/ban`
- `/unban`
  
以上命令皆有三个参数 

1. `-u` : QQ号
2. `-g` : 群号
3. `-p` : 插件名称

如果未输入参数则认为作用在全局 , 例如 `\ban -u 123456` 的意义为禁用 QQ 为 123456 的人在所有群使用所有插件的权限

### cool

本部分提供三个级别的控制 , plugin , matcher , function

对于插件级别的控制 , 通过配置文件实现 , 详见下

对于 matcher 级别的控制 , 通过跨插件方法导入类 `cooling`
```py
from nonebot.plugin import require
req = require("nonebot_plugin_PCtrl")
cmd = req.cooling.cool_matcher(5, on_keyword({"jls", "jiangly"}, priority=10)) # 对一个 matcher 启用冷却
@cmd.handle()
async def _(bot, event, state): pass
```

对于 function 级别的控制 , 通过跨插件方法导入类 `cooling`
```py
from nonebot.plugin import require
req = require("admin.nonebot_plugin_PCtrl")
coolen_async = req.cooling.cool_async

@coolen_async(5)
async def _(bot, event, state): pass
```

对于通过 `cooling` 类实现的冷却 , 当未到冷却时间调用时会 `raise CoolingError`
```py
# 参见
from anyutils import CoolingError
```
### sender (工具类)

通过跨插件方法导入类 `sender` , 源码位于 `plugin/sender.py`

```py
# 当有没有处理的 `Execption` 时汇报到群聊(见配置)
@sender.when_raise(log)
async def _():
    pass

# 当函数被调用时汇报到群聊
@sender.when_func_call(log)
async def _():
    pass

```

## 配置
请在 `bot.py` 同一目录下创建文件 `secure.yaml` (注意后缀名) , 然后根据自己的情况填写配置 (目录下有一个示例)
```yaml
config:
  basic:
    reply_id: # !必须换成一个群号 , 是用来报告一些管理相关信息的群聊号码
    bot_name: # bot 名
    debug: false # 是否开启 `debug` 模式 (影响`sqla`的`echo`设置)
    db_link: "sqlite+aiosqlite:///admin.sqlite" # sqla 数据库链接
    ignore_global_control: # 忽略管控的插件名称
      - nonebot_plugin_PCtrl

  plugins:
    # 配置越具体的优先级越高 , 同一具体的优先级 群 > qq号 > 插件名称
    glob: # 使用 glob 代表所有插件
      - space: 0 # 使用 0 代表私聊
        coolen_time: 10 # 冷却时间
      - space: 123456 # 否则代表群号为该数字的群
        coolen_time: 10

    echo: # 否则使用插件名(以 nonebot 加载显示的为准)
      - space: 0
        coolen_time: 10
      - space: 1919810
        coolen_time: 10

```

因为使用了特殊的语句~~(`mysql`泰拉)~~ , 所以以下方言二选一使用
1. `postgresql+asyncpg` 需要安装 `asyncpg`
2. `sqlite+aiosqlite` 默认依赖

## 特别感谢

[nonebot2](https://github.com/nonebot/nonebot2) : 优秀的跨平台 python 异步机器人框架

[SQLAlchemy](https://www.sqlalchemy.org/) : 完善~~文档根本看不懂~~的 ORM

## 部分更新

- `0.2.0` : 适配 `b1` , ~~优化整体逻辑~~
- `0.1.8` : 冷却时间信息显示与命令修改功能完成
- `0.1.6` : 全局冷却功能完成