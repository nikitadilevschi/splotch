"""
Spike obstacles (static or pop-up).
"""

import pygame

from engine.tl_runner import TLRunner
from ui.draw_helpers import (
    draw_spike, draw_spike_colored,
    draw_spike_down, draw_spike_down_colored,
    draw_spike_left, draw_spike_left_colored,
    draw_spike_right, draw_spike_right_colored
)


class SpikeObj:
    def __init__(self, x, y, w=32, h=14, steps=None, sensor=None, dir='up'):
        # x,y is the top-left corner (Tiled coords)
        # The spike tip is at (x + w//2, y)  i.e. centre-x, top-y
        # dir: 'up' (default), 'down', 'left', 'right'
        self.ox, self.oy = float(x), float(y)
        self.w = w
        self.h = h
        self.dir = dir
        self.sensor = sensor
        steps = steps or []
        self.runner = TLRunner(x, y, steps, loop=False)
        self.static = (sensor is None and not steps)
        if self.static:
            self.runner.active = True

    def reset(self):
        self.runner.reset()
        if self.static:
            self.runner.active = True
        if self.sensor:
            self.sensor.reset()

    def update(self, dt, prect):
        if self.sensor and not self.runner.active:
            if self.sensor.check(prect):
                self.runner.activate()
        self.runner.update(dt)

    @property
    def cx(self):
        return self.runner.x + self.w // 2

    @property
    def cy(self):
        return self.runner.y   # top of spike (tip)

    def _triggered(self):
        """True once the spike has been activated (or is always-on static)."""
        if self.static:
            return True
        if not (self.runner.active or self.runner.done):
            return False
        # If still waiting for the first step's delay, keep the spike hidden
        if self.runner.active and not self.runner.done and self.runner.step == 0:
            delay = self.runner.steps[0].get('d', 0.0) if self.runner.steps else 0.0
            if self.runner.timer < delay:
                return False
        return True

    def kill_rect(self):
        if not self._triggered():
            return pygame.Rect(0, 0, 0, 0)   # hidden – not yet dangerous
        
        # Collision box matches the actual small visual spike
        x = int(self.runner.x)
        y = int(self.runner.y)
        
        if self.dir == 'up':
            # Upward spike: collision centered at tip
            return pygame.Rect(x + 11, y, 10, 8)
        elif self.dir == 'down':
            # Downward spike: collision centered at tip
            return pygame.Rect(x + 11, y + 6, 10, 8)
        elif self.dir == 'left':
            # Left spike: collision centered on the spike tip
            # Spike is centered at cy, extends hw=5 pixels vertically
            return pygame.Rect(x + 5, y + 11, 8, 10)
        elif self.dir == 'right':
            # Right spike: collision centered on the spike tip
            # Spike is centered at cy, extends hw=5 pixels vertically
            return pygame.Rect(x + 19, y + 11, 8, 10)
        else:
            # Default fallback
            return pygame.Rect(x + 11, y, 10, 8)

    def draw(self, surf, ox, oy, palette=None):
        if not self._triggered():
            return   # still hidden inside the floor tile – don't paint it
        cx, cy = int(self.cx) + ox, int(self.cy) + oy
        color = palette['spike'] if palette else (180, 180, 180)
        if self.dir == 'up':
            if palette is None:
                draw_spike(surf, cx, cy + 16)
            else:
                draw_spike_colored(surf, cx, cy + 16, color)
        elif self.dir == 'down':
            if palette is None:
                draw_spike_down(surf, cx, cy - self.h + 16)
            else:
                draw_spike_down_colored(surf, cx, cy - self.h + 16, color)
        elif self.dir == 'left':
            if palette is None:
                draw_spike_left(surf, cx + 16, cy)
            else:
                draw_spike_left_colored(surf, cx + 16, cy, color)
        elif self.dir == 'right':
            if palette is None:
                draw_spike_right(surf, cx - self.w + 16, cy)
            else:
                draw_spike_right_colored(surf, cx - self.w + 16, cy, color)

