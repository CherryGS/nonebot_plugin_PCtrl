import os

import yaml

from .config import config as cfg
from .methods.exception import *


def load_config(pth) -> cfg:
    if not os.path.isfile(pth):
        pth = os.path.dirname(__file__) + "/secure.yaml"
    with open(pth, "r") as f:
        res: cfg = yaml.safe_load(f.read())["config"]
    return cfg.parse_obj(res)


all_cfg = load_config("secure.yaml")
conf = all_cfg.basic

if not os.environ.get("RUN_TESTS"):
    from nonebot import export

    from .plugin import CoolMakerPlus, sender

    export = export()
    export.sender = sender
    export.cooling = CoolMakerPlus()
