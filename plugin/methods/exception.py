class MethodError(Exception):
    pass


class PluginNotFoundError(MethodError):
    pass


class NoConfigError(MethodError):
    """
    当在数据库没有查询到相应配置时抛出

    期待行为是不`raise`而是采用默认值
    """
