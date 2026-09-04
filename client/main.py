import os
import time

import ui
import client
import config

ui.init()


### I will start with ui
def save_config(inst, val):
    setattr(conf, inst, val)
    with open("config.py", "w", encoding="utf-8") as f:
        for k, v in vars(conf).items():
            if not k.startswith("__"):
                f.write(f"{k} = {repr(v)}\n")

