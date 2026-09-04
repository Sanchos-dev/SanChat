import os
import time

import ui
import client
import config as conf


def save_conf(inst, val):
    setattr(conf, inst, val)
    with open("config.py", "w", encoding="utf-8") as f:
        for k, v in vars(conf).items():
            if not k.startswith("__"):
                f.write(f"{k} = {repr(v)}\n")

save_conf("DEBUG",True)