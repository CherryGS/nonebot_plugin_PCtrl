# nonebot_plugin_PCtrl
## 简介

基于 Hook 的插件管理器

使用 SQLAlchemy + asyncpg 实现持久化

功能持续增加中

## 功能

### global.switch

- `/listplugins` 列出所有受控的插件的插件名称和开启状态
- `/setplugin -p plugin_name` 将插件名为 `plugin_name` 的插件的开启状态反向

### global.ban

- `/ban -u handle -p plugin_name` ban 掉 QQ 号为 `handle` 的人使用名称为 `plugin_name` 插件的权限
- `/ban -g handle -p plugin_name` ban 掉群号为 `handle` 的群使用名称为 `plugin_name` 插件的权限
- `/unban -u handle -p plugin_name` 取消 ban
- `/unban -g handle -p plugin_name` 取消 ban

## 配置
请添加到 nonebot2 配置文件中
```ini
# 数据库配置(postgres+asyncpg)
## 用户名
db_user=
## 密码
db_passwd=
## 数据库名
db_name=
## 数据库地址
db_addr=

# 数据库配置(SQLAlchemy任意异步) ! 该选项会覆盖上述数据库配置
## 数据库链接(请参考SQLAlchemy官方文档)
## url: https://docs.sqlalchemy.org/en/14/tutorial/engine.html#establishing-connectivity-the-engine
db_link=
```

## 侵入式管理部分

### 忽略管控

对于不想被此插件管控的插件 , 请使用 nonebot2 提供的跨插件方法导出属性 `ignore_global_control = True`

## 特别感谢

[nonebot2](https://github.com/nonebot/nonebot2) : 优秀的跨平台 python 异步机器人框架

[SQLAlchemy](https://www.sqlalchemy.org/) : 完善~~文档根本看不懂~~的 ORM

## 额外说明

本插件初始化于 `websocket` 连接时 , http协议未经测试

导入时**注意大小写** `nonebot_plugin_PCtrl`