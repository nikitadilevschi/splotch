"""
Save file management.
"""

import json
import os

from core.constants import SAVE_F


def default_save():
    return {
        "deaths": 0,
        "level_deaths": {},  # Per-level death tracking: "category_level" -> count
        "completed": {},
        "unlocked_cats": [0, 1],
        "unlocked_lvls": {"0":[0],"1":[0],"2":[0],"3":[0],"4":[0],"5":[0],"6":[0]},
        "muted": False,
    }


def load_save():
    if os.path.exists(SAVE_F):
        try:
            with open(SAVE_F) as f:
                s = json.load(f)
            if "unlocked_cats" not in s:
                s["unlocked_cats"] = [0, 1]
            if "unlocked_lvls" not in s:
                s["unlocked_lvls"] = {"0":[0],"1":[0],"2":[0],"3":[0],"4":[0],"5":[0],"6":[0]}
            if "muted" not in s:
                s["muted"] = False
            if "level_deaths" not in s:
                s["level_deaths"] = {}
            # Ensure Teleporters category level tracking exists
            if "6" not in s["unlocked_lvls"]:
                s["unlocked_lvls"]["6"] = [0]
            return s
        except:
            pass
    return default_save()


def write_save(s):
    with open(SAVE_F, 'w') as f:
        json.dump(s, f, indent=2)

