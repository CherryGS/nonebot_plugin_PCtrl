from time import time

from nonebot.adapters.onebot.v11 import Event, GroupMessageEvent, PrivateMessageEvent
from nonebot.matcher import Matcher
from nonebot.message import event_preprocessor
from nonebot.exception import IgnoredException
from . import hook
from .methods import GLOBAL_SPACE, load_cool_config

tim = dict()
cool = dict()

from anyutils import CoolMaker


class CoolMakerPlus(CoolMaker):
    def cool_matcher(self, tim: int, matcher: Matcher):
        matcher.simple_run = self.cool_async(tim)(matcher.simple_run)


@hook.add_hook
async def _():
    global cool
    cool = await load_cool_config()


@event_preprocessor
async def _(event: Event):
    t = time()
    if isinstance(event, PrivateMessageEvent):
        k = (GLOBAL_SPACE, event.user_id)
    elif isinstance(event, GroupMessageEvent):
        k = (event.group_id, event.user_id)
    else:
        return

    global tim, cool

    if k in cool:
        if cool[k] == 0:
            cool.pop(k)
            return
        if k in tim and tim[k] + cool[k] > t:
            raise IgnoredException("coolen")
        else:
            tim[k] = t
