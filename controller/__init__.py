import yaml
from nonebot import export

from .config import config as cfg


def load_config() -> cfg:
    with open("secure.yaml", "r") as f:
        res: cfg = yaml.safe_load(f.read())["config"]
    return cfg.parse_obj(res)


all_cfg = load_config()
conf = all_cfg.basic

from .plugin import CoolMakerPlus, sender

export = export()
export.sender = sender
export.cooling = CoolMakerPlus()
