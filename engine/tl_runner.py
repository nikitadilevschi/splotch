"""
Timeline runner and easing functions for animations.
"""

from core.constants import TILE


def _ease(name, t):
    t = max(0.0, min(1.0, t))
    n = (name or '').strip().lower()
    if n == 'ease-in':
        return t*t
    if n == 'ease-out':
        return 1-(1-t)*(1-t)
    if n == 'ease-in-out':
        return t*t*(3-2*t)
    return t


class TLRunner:
    """Runs a sequence of tween steps on a (x,y) position."""
    def __init__(self, ox, oy, steps, loop=False):
        self.ox0, self.oy0 = ox, oy
        self.x, self.y     = float(ox), float(oy)
        self.steps  = steps
        self.loop   = loop
        self.step   = 0
        self.timer  = 0.0
        self.active = False
        self.done   = False
        self._sx = self.x
        self._sy = self.y

    def activate(self):
        self.active = True
        self.done   = False
        self.step   = 0
        self.timer  = 0.0
        self.x, self.y = self.ox0, self.oy0
        self._sx = self.x
        self._sy = self.y

    def reset(self):
        self.active = False
        self.done   = False
        self.step   = 0
        self.timer  = 0.0
        self.x, self.y = self.ox0, self.oy0
        self._sx = self.x
        self._sy = self.y

    def update(self, dt):
        if not self.active or self.done or not self.steps:
            return
        self.timer += dt
        s = self.steps[self.step]
        delay = s.get('d', 0.0)
        dur   = max(0.001, s.get('t', 0.5))
        if self.timer < delay:
            return
        pct = min(1.0, (self.timer - delay) / dur)
        ep  = _ease(s.get('e',''), pct)
        self.x = self._sx + s.get('tx', 0) * TILE * ep
        self.y = self._sy + s.get('ty', 0) * TILE * ep
        if pct >= 1.0:
            self._sx, self._sy = self.x, self.y
            self.step += 1
            self.timer = 0.0
            if self.step >= len(self.steps):
                if self.loop:
                    self.step = 0
                    self._sx, self._sy = self.ox0, self.oy0
                    self.x, self.y = self.ox0, self.oy0
                else:
                    self.done = True

