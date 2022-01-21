from time import time

from nonebot.adapters.onebot.v11 import Event, GroupMessageEvent, PrivateMessageEvent
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor
from nonebot.exception import IgnoredException
from . import hook
from .methods import GLOBAL_SPACE, load_cool_config, ALL_PLUGIN_NAME
from anyutils import CoolMaker

tim = dict()
cool = dict()


class CoolMakerPlus(CoolMaker):
    def cool_matcher(self, tim: int, matcher: Matcher):
        matcher.simple_run = self.cool_async(tim)(matcher.simple_run)


@hook.add_hook
async def _():
    global cool
    cool = await load_cool_config()


@run_preprocessor
async def _(matcher: Matcher, event: Event):
    t = time()
    if isinstance(event, PrivateMessageEvent):
        k = (GLOBAL_SPACE, matcher.plugin_name)
    elif isinstance(event, GroupMessageEvent):
        k = (event.group_id, matcher.plugin_name)
    else:
        return
    global tim, cool

    if k not in cool:
        k = (k[0], ALL_PLUGIN_NAME)

    if k in cool:
        if k in tim and tim[k] + cool[k] > t:
            raise IgnoredException("coolen")
        else:
            tim[k] = t
