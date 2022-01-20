from nonebot import export

from admin.nonebot_plugin_PCtrl.plugin.cool import CoolMakerPlus
from .plugin import *

export = export()
export.sender = sender
export.cooling = CoolMakerPlus()
export.cooling.cool_async
