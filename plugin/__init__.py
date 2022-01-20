from anyutils import HookMaker

hook = HookMaker("After init_db")

from .ban import *
from .init_db import *
