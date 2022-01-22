from nonebot import export

from .plugin import CoolMakerPlus, sender

export = export()
export.sender = sender
export.cooling = CoolMakerPlus()
