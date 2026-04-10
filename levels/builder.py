"""
Level builder functions.
"""

import pygame

from engine.mblock import MBlock
from engine.spike import SpikeObj
from engine.sensor import Sensor
from core.constants import TILE, OW, OH


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
    return None

