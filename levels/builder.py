"""
Level builder functions.
"""

import pygame

from engine.mblock import MBlock
from engine.spike import SpikeObj
from engine.teleporter import Teleporter
from engine.sensor import Sensor
from core.constants import TILE


def tiles_to_rects(tiles, tw=27, th=15):
    """Merge horizontally-adjacent solid tiles into wide Rects (world coords)."""
    rects = []
    for row in range(th):
        col = 0
        while col < tw:
            if tiles[row*tw + col]:
                sc = col
                while col < tw and tiles[row*tw + col]:
                    col += 1
                rects.append(pygame.Rect(sc*TILE, row*TILE, (col-sc)*TILE, TILE))
            else:
                col += 1
    return rects


def _build_trap(td):
    """Build one trap object from level data and attach an optional sensor trigger."""
    kind = td['kind']
    sx = td.get('sensor')
    s_obj = Sensor(*sx) if sx else None

    if kind == 'mblock':
        return MBlock(td['x'], td['y'], td['w'], td['h'],
                      td['steps'], td.get('loop', False),
                      td.get('auto', False), s_obj, td.get('is_saw', False))
    if kind == 'spike':
        return SpikeObj(td['x'], td['y'],
                        td.get('w', 32), td.get('h', 14),
                        td.get('steps', []), s_obj, td.get('dir', 'up'))
    if kind == 'teleporter':
        destination_mode = td.get('destination_mode', 'static')
        destinations = td.get('destinations')
        if not destinations:
            if 'dest_x' in td and 'dest_y' in td:
                destinations = [(td['dest_x'], td['dest_y'])]
            elif destination_mode == 'self_top':
                # Seed with current teleporter position; runtime target comes from live position.
                destinations = [(td['x'], td['y'])]
            else:
                raise ValueError(
                    "Teleporter trap requires 'destinations' or 'dest_x'/'dest_y'"
                )
        return Teleporter(td['x'], td['y'], 
                         destinations[0][0], destinations[0][1],
                         td.get('w', 40), td.get('h', 40),
                         td.get('steps', []), s_obj, td.get('loop', True),
                         destinations=destinations,
                         destination_mode=destination_mode,
                         teleport_cooldown=td.get('cooldown', 0.5),
                         self_top_offset_tiles=td.get('self_top_offset_tiles', 0))
    return None

