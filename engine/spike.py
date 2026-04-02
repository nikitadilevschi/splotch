"""
Spike obstacles (static or pop-up).
"""

import pygame

from engine.tl_runner import TLRunner
from ui.draw_helpers import draw_spike, draw_spike_colored


class SpikeObj:
    def __init__(self, x, y, w=32, h=14, steps=None, sensor=None):
        # x,y is the top-left corner (Tiled coords)
        # The spike tip is at (x + w//2, y)  i.e. centre-x, top-y
        self.ox, self.oy = float(x), float(y)
        self.w = w
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
        return pygame.Rect(int(self.runner.x) + 2, int(self.runner.y), self.w - 4, 16)

    def draw(self, surf, ox, oy, palette=None):
        if not self._triggered():
            return   # still hidden inside the floor tile – don't paint it
        if palette is None:
            draw_spike(surf, int(self.cx) + ox, int(self.cy) + oy + 16)
        else:
            draw_spike_colored(surf, int(self.cx) + ox, int(self.cy) + oy + 16, palette['spike'])

