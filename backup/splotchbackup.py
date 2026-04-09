"""
Splotch – Precision Platformer
================================
Run instructions:
    pip install pygame
    python main.py

Controls:
    Arrow Keys / WASD  – Move & Jump
    Space              – Jump
    R                  – Reset current level (+1 death)
    ESC                – Back to previous menu
    Ctrl+R             – Reset all save data (on category select screen)

Save file: save.json  (auto-created next to main.py)

HIDDEN TRAP PHILOSOPHY
──────────────────────
Every trap tile LOOKS identical to the normal floor on first approach.
Something triggers mid-run – platforms slide, spikes erupt, saws charge.
On the next attempt the player knows the pattern and can survive.
"""

import pygame, sys, json, os, math

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
SW, SH  = 1024, 576          # window size (16:9)
FPS     = 60
TILE    = 32                 # tile size in pixels  (27×15 grid = 864×480)
OW, OH  = 864, 480           # original world size
OX      = (SW - OW) // 2    # 80 – horizontal offset to centre world
OY      = 56                 # vertical offset = top-bar height
TOP_H   = OY
SAVE_F  = "save.json"

# Palette
TEAL        = ( 38, 166, 154)
TEAL_DARK   = ( 25, 130, 120)
CREAM       = (255, 250, 220)   # platform / trap tile fill (SAME colour)
CREAM_LINE  = (210, 200, 165)   # grid lines on tiles
CREAM_EDGE  = (200, 190, 155)   # platform outer border
ORANGE      = (255, 140,   0)
ORANGE_DK   = (200, 100,   0)
WHITE       = (255, 255, 255)
BLACK       = (  0,   0,   0)
GREY        = (150, 150, 150)
YELLOW      = (255, 220,  50)
RED_FLASH   = (220,  50,  50)

# Physics  (pixels / second)
GRAVITY  = 1400
MAX_FALL = 850
JUMP_V   = -560
SPEED    = 210
COYOTE   = 0.10
JBUF     = 0.10

# ─────────────────────────────────────────────────────────────────────────────
# SAVE  HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def default_save():
    return {
        "deaths": 0,
        "completed": {},
        "unlocked_cats": [0, 1],
        "unlocked_lvls": {"0":[0],"1":[0],"2":[0],"3":[0],"4":[0]},
    }

def load_save():
    if os.path.exists(SAVE_F):
        try:
            with open(SAVE_F) as f: s = json.load(f)
            if "unlocked_cats" not in s: s["unlocked_cats"] = [0,1]
            if "unlocked_lvls" not in s:
                s["unlocked_lvls"] = {"0":[0],"1":[0],"2":[0],"3":[0],"4":[0]}
            return s
        except: pass
    return default_save()

def write_save(s):
    with open(SAVE_F, 'w') as f: json.dump(s, f, indent=2)

# ─────────────────────────────────────────────────────────────────────────────
# FONT / TEXT
# ─────────────────────────────────────────────────────────────────────────────
_fonts = {}
def get_font(size, bold=True):
    k = (size, bold)
    if k not in _fonts:
        _fonts[k] = pygame.font.SysFont("Arial", size, bold=bold)
    return _fonts[k]

def draw_text(surf, text, size, color, cx, cy, bold=True, anchor="center"):
    s = get_font(size, bold).render(str(text), True, color)
    r = s.get_rect()
    if   anchor == "center":   r.center   = (cx, cy)
    elif anchor == "topleft":  r.topleft  = (cx, cy)
    elif anchor == "midleft":  r.midleft  = (cx, cy)
    surf.blit(s, r)

def rrect(surf, color, rect, radius=8):
    pygame.draw.rect(surf, color, rect, border_radius=radius)

# ─────────────────────────────────────────────────────────────────────────────
# DRAW HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def draw_tile_rect(surf, rect):
    """Draw a single tile-sized block with cream fill + thin grid lines."""
    pygame.draw.rect(surf, CREAM, rect)
    pygame.draw.rect(surf, CREAM_LINE, rect, 1)

def draw_tiled_platform(surf, rect, ox, oy):
    """Draw a moving-block rect looking identical to normal floor tiles."""
    r = rect.move(ox, oy)
    pygame.draw.rect(surf, CREAM, r)
    # grid lines
    x0, y0, w, h = r.x, r.y, r.width, r.height
    for col in range(0, w+1, TILE):
        pygame.draw.line(surf, CREAM_LINE, (x0+col, y0), (x0+col, y0+h), 1)
    for row in range(0, h+1, TILE):
        pygame.draw.line(surf, CREAM_LINE, (x0, y0+row), (x0+w, y0+row), 1)

def draw_player(surf, x, y, w=26, h=26):
    """Orange square with big cartoon eyes."""
    r = pygame.Rect(int(x - w//2), int(y - h), w, h)
    pygame.draw.rect(surf, ORANGE, r, border_radius=5)
    pygame.draw.rect(surf, ORANGE_DK, r, 2, border_radius=5)
    ew = 8; eh = 8
    lx = r.x + 4;  rx2 = r.right - 4 - ew
    ey2 = r.y + 6
    pygame.draw.ellipse(surf, WHITE, (lx, ey2, ew, eh))
    pygame.draw.ellipse(surf, WHITE, (rx2, ey2, ew, eh))
    pygame.draw.circle(surf, BLACK, (lx + ew//2 + 1, ey2 + eh//2 + 1), 3)
    pygame.draw.circle(surf, BLACK, (rx2 + ew//2 + 1, ey2 + eh//2 + 1), 3)

def draw_flag(surf, fx, fy):
    """Black pole + solid orange triangular flag."""
    pole_h = 42
    top    = fy - pole_h
    pygame.draw.line(surf, BLACK, (fx, fy), (fx, top), 3)
    pts = [(fx, top), (fx + 22, top + 11), (fx, top + 22)]
    pygame.draw.polygon(surf, ORANGE, pts)

def draw_spike(surf, cx, bot_y):
    """Single upward spike – grey, looks like a tile when flush."""
    hw = 11; h = 16
    pts = [(cx, bot_y - h), (cx - hw, bot_y), (cx + hw, bot_y)]
    pygame.draw.polygon(surf, (180, 180, 180), pts)
    pygame.draw.polygon(surf, (80, 80, 80), pts, 1)

def draw_splotch_icon(surf, cx, cy, r, color, num):
    n = 10
    pts = []
    for i in range(n):
        a  = i * 2*math.pi/n
        dr = r * (0.65 + 0.35 * math.sin(i*3.9 + 1.1))
        pts.append((cx + math.cos(a)*dr, cy + math.sin(a)*dr))
    pygame.draw.polygon(surf, color, pts)
    draw_text(surf, str(num), max(10, r-5), BLACK, cx, cy)

def draw_lock(surf, cx, cy, size=30):
    hw = size//3
    body = pygame.Rect(cx-hw, cy-hw//2, hw*2, int(hw*1.4))
    pygame.draw.rect(surf, GREY, body, border_radius=3)
    arc_r = pygame.Rect(cx-hw+2, cy-hw-hw//2, (hw-2)*2, hw*2)
    pygame.draw.arc(surf, GREY, arc_r, 0, math.pi, 4)

def draw_flag_icon(surf, cx, cy, size=14, color=WHITE, filled=True):
    pole_top = cy - size
    pygame.draw.line(surf, color, (cx, cy+2), (cx, pole_top), 2)
    pts = [(cx, pole_top), (cx+size, pole_top+size//2), (cx, pole_top+size)]
    if filled:
        pygame.draw.polygon(surf, color, pts)
    else:
        pygame.draw.polygon(surf, color, pts, 1)

# ─────────────────────────────────────────────────────────────────────────────
# TILE MAP → PLATFORM RECTS
# ─────────────────────────────────────────────────────────────────────────────
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

# ─────────────────────────────────────────────────────────────────────────────
# EASING  +  TIMELINE
# ─────────────────────────────────────────────────────────────────────────────
def _ease(name, t):
    t = max(0.0, min(1.0, t))
    n = (name or '').strip().lower()
    if n == 'ease-in':     return t*t
    if n == 'ease-out':    return 1-(1-t)*(1-t)
    if n == 'ease-in-out': return t*t*(3-2*t)
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
        self._sx = self.x; self._sy = self.y

    def activate(self):
        self.active = True
        self.done   = False
        self.step   = 0
        self.timer  = 0.0
        self.x, self.y = self.ox0, self.oy0
        self._sx = self.x; self._sy = self.y

    def reset(self):
        self.active = False
        self.done   = False
        self.step   = 0
        self.timer  = 0.0
        self.x, self.y = self.ox0, self.oy0
        self._sx = self.x; self._sy = self.y

    def update(self, dt):
        if not self.active or self.done or not self.steps: return
        self.timer += dt
        s = self.steps[self.step]
        delay = s.get('d', 0.0)
        dur   = max(0.001, s.get('t', 0.5))
        if self.timer < delay: return
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

# ─────────────────────────────────────────────────────────────────────────────
# SENSOR ZONE
# ─────────────────────────────────────────────────────────────────────────────
class Sensor:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.fired = False

    def check(self, player_rect):
        if not self.fired and self.rect.colliderect(player_rect):
            self.fired = True
            return True
        return False

    def reset(self):
        self.fired = False

# ─────────────────────────────────────────────────────────────────────────────
# MOVING  BLOCK  (trap floor / moving platform)
# ─────────────────────────────────────────────────────────────────────────────
class MBlock:
    def __init__(self, x, y, w, h, steps, loop=False, auto=False, sensor=None):
        self.ox, self.oy = x, y
        self.w, self.h   = w, h
        self.sensor      = sensor
        self.auto        = auto
        self.runner      = TLRunner(x, y, steps, loop)
        self.prev_x, self.prev_y = float(x), float(y)
        if auto: self.runner.activate()

    def reset(self):
        self.runner.reset()
        self.prev_x, self.prev_y = float(self.ox), float(self.oy)
        if self.auto: self.runner.activate()
        if self.sensor: self.sensor.reset()

    def update(self, dt, prect):
        self.prev_x, self.prev_y = self.runner.x, self.runner.y
        if self.sensor and not self.runner.active:
            if self.sensor.check(prect):
                self.runner.activate()
        self.runner.update(dt)

    @property
    def prev_rect(self):
        return pygame.Rect(int(self.prev_x), int(self.prev_y), self.w, self.h)

    @property
    def rect(self):
        return pygame.Rect(int(self.runner.x), int(self.runner.y), self.w, self.h)

    def draw(self, surf, ox, oy):
        """Draw identical to normal tile – the whole trick."""
        draw_tiled_platform(surf, self.rect, ox, oy)

# ─────────────────────────────────────────────────────────────────────────────
# SPIKE  (static or pop-up)
# The spike starts FLUSH with the floor (invisible until triggered).
# ─────────────────────────────────────────────────────────────────────────────
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
        if self.static: self.runner.active = True

    def reset(self):
        self.runner.reset()
        if self.static: self.runner.active = True
        if self.sensor: self.sensor.reset()

    def update(self, dt, prect):
        if self.sensor and not self.runner.active:
            if self.sensor.check(prect):
                self.runner.activate()
        self.runner.update(dt)

    @property
    def cx(self): return self.runner.x + self.w // 2
    @property
    def cy(self): return self.runner.y   # top of spike (tip)

    def kill_rect(self):
        return pygame.Rect(int(self.runner.x) + 2, int(self.runner.y), self.w - 4, 16)

    def draw(self, surf, ox, oy):
        draw_spike(surf, int(self.cx) + ox, int(self.cy) + oy + 16)

# ─────────────────────────────────────────────────────────────────────────────
# PLAYER
# ─────────────────────────────────────────────────────────────────────────────
class Player:
    W, H = 26, 26

    def __init__(self, sx, sy):
        self._sx, self._sy = float(sx), float(sy)
        self.reset_pos()

    def reset_pos(self):
        self.x, self.y = self._sx, self._sy
        self.vx = self.vy = 0.0
        self.on_ground = False
        self.coyote    = 0.0
        self.jbuf      = 0.0
        self.alive     = True

    def handle_input(self, keys):
        left  = keys[pygame.K_LEFT]  or keys[pygame.K_a]
        right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        jump  = keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]
        self.vx = SPEED * (right - left)
        if jump: self.jbuf = JBUF

    def update(self, dt, platforms):
        self.vy = min(self.vy + GRAVITY*dt, MAX_FALL)
        self.coyote = max(0, self.coyote - dt)
        self.jbuf   = max(0, self.jbuf   - dt)

        if self.jbuf > 0 and (self.on_ground or self.coyote > 0):
            self.vy = JUMP_V
            self.coyote = self.jbuf = 0

        self.on_ground = False
        self.x += self.vx * dt; self._cx(platforms)
        self.y += self.vy * dt; self._cy(platforms)

    def _cx(self, plats):
        r = self.rect
        for p in plats:
            if r.colliderect(p):
                if self.vx > 0:
                    self.x = p.left - self.W//2
                elif self.vx < 0:
                    self.x = p.right + self.W//2
                else:
                    # If platform motion causes overlap while idle, push to nearest side.
                    if r.centerx < p.centerx:
                        self.x = p.left - self.W//2
                    else:
                        self.x = p.right + self.W//2
                self.vx = 0; r = self.rect

    def _cy(self, plats):
        r = self.rect
        for p in plats:
            if r.colliderect(p):
                if self.vy >= 0:
                    self.y = p.top; self.on_ground = True; self.coyote = COYOTE
                else:
                    self.y = p.bottom + self.H
                self.vy = 0; r = self.rect

    @property
    def rect(self):
        return pygame.Rect(int(self.x - self.W//2), int(self.y - self.H),
                           self.W, self.H)

    def draw(self, surf, ox, oy):
        draw_player(surf, int(self.x)+ox, int(self.y)+oy, self.W, self.H)

# ─────────────────────────────────────────────────────────────────────────────
# LEVEL DATA  (5 categories × 3 levels) — exact data from original JS
# All coordinates are in world pixel space (Tiled export).
# ─────────────────────────────────────────────────────────────────────────────

# ██████  GAPS  ████████████████████████████████████████████████████████████████

GAPS_L1 = {
 'tiles': [
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
  1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
  1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
  1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,0,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,0,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,0,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,0,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,0,1,1,1,1,1,1,1,1,
 ],
 # player y=320 means feet at row 10 top = y coord is bottom of player
 'player': [160, 320],
 'goal':   [672, 320],
 # Block at x=576,y=320, w=32, h=160 slides right ty=6 when sensor fires
 # Sensor at x=560, y=192, w=32, h=128
 'traps': [
  dict(kind='mblock', x=576,y=320,w=32,h=160,
       sensor=(560,192,32,128),
       steps=[dict(ty=6, t=0.3)], loop=False, auto=False),
 ],
 'hint': "That floor tile ahead will drop – jump the gap before it falls!",
}

GAPS_L2 = {
 'tiles': [
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
  1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
  1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
  1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
  1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,
 ],
 'player': [160, 320],
 'goal':   [704, 320],
 # Two blocks: x=448,y=320,w=64,h=160  and x=576,y=320,w=64,h=160
 # Both slide tx=-2 when sensor/1 at x=448,y=192,w=32,h=128 fires
 'traps': [
  dict(kind='mblock', x=448,y=320,w=64,h=160,
       sensor=(448,192,32,128),
       steps=[dict(tx=-2, t=0.2)], loop=False, auto=False),
  dict(kind='mblock', x=576,y=320,w=64,h=160,
       sensor=(448,192,32,128),
       steps=[dict(tx=-2, t=0.2)], loop=False, auto=False),
 ],
 'hint': "Two bridges vanish at once – sprint past before they slide away!",
}

GAPS_L3 = {
 'tiles': [
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
  1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
  1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
  1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
  1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,0,0,0,0,0,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,0,0,0,0,0,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,0,0,0,0,0,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,0,0,0,0,0,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,0,0,0,0,0,1,1,1,1,1,1,
 ],
 'player': [160, 320],
 'goal':   [704, 320],
 # Block1 x=416,y=320,w=96,h=160: slides tx=2.5 t=0.5 d=0.75 on sensor/1
 # Block2 x=576,y=320,w=96,h=160: slides tx=2.5 t=0.25 on sensor/1 (same)
 # Two separate sensors: sensor/1 at 480,256,160,32  sensor/2 at 512,288,128,32
 # The blocks respond to sensor/1; sensor/2 is chained (py=-1 on sensor/1)
 # Simplify: use sensor/1 for both blocks (first wide sensor player steps on)
 'traps': [
  dict(kind='mblock', x=416,y=320,w=96,h=160,
       sensor=(480,256,160,32),
       steps=[dict(tx=2.5, t=0.5, d=0.75)], loop=False, auto=False),
  dict(kind='mblock', x=576,y=320,w=96,h=160,
       sensor=(512,288,128,32),
       steps=[dict(tx=2.5, t=0.25)], loop=False, auto=False),
 ],
 'hint': "Jump on the first bridge, then run – the second one moves faster!",
}

# ██████  SPIKES  ██████████████████████████████████████████████████████████████

SPIKES_L1 = {
 'tiles': [
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,
  1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,
  1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,
  1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,
  1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
 ],
 'player': [160, 320],
 'goal':   [640, 320],
 # spike at x=320,y=320 static (no sensor)
 # spike at x=480,y=320 pops tx=1,t=0.25 on sensor/1 (x=464,y=192,w=32,h=128)
 'traps': [
  dict(kind='spike', x=320, y=320, w=32, h=14, steps=[], sensor=None),
  dict(kind='spike', x=480, y=320, w=32, h=14,
       steps=[dict(tx=1, t=0.25)],
       sensor=(464,192,32,128)),
 ],
 'hint': "One spike is already there – a second one hides in the floor ahead!",
}

SPIKES_L2 = {
 'tiles': [
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,
  1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
  1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
  1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
  1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
 ],
 'player': [128, 288],
 'goal':   [704, 288],
 # Static spikes: x=224,y=320  and x=416,y=352
 # Pop spike 1: x=224,y=320 sensor/2 at (224,224,32,96) tx=2,t=0.25
 # Pop spike 2: x=640,y=320 sensor/3 at (544,224,32,96) ty=1,t=0.25
 # Pop spike 3: x=608,y=320 sensor/3 at (544,224,32,96) ty=1,t=0.25
 # Pop spike 4: x=608,y=336 sensor/4 at (608,224,32,96) ty=-0.5,t=0.1
 # Static (no sensor): x=192,y=320
 'traps': [
  # static visible spikes
  dict(kind='spike', x=192, y=320, w=32, h=14, steps=[], sensor=None),
  dict(kind='spike', x=416, y=352, w=32, h=14, steps=[], sensor=None),
  # hidden pop-up spikes
  dict(kind='spike', x=224, y=320, w=32, h=14,
       steps=[dict(tx=2, t=0.25)], sensor=(224,224,32,96)),
  dict(kind='spike', x=640, y=320, w=32, h=14,
       steps=[dict(ty=1, t=0.25)], sensor=(544,224,32,96)),
  dict(kind='spike', x=608, y=320, w=32, h=14,
       steps=[dict(ty=1, t=0.25)], sensor=(544,224,32,96)),
  dict(kind='spike', x=608, y=336, w=32, h=14,
       steps=[dict(ty=-0.5, t=0.1)], sensor=(608,224,32,96)),
 ],
 'hint': "Mid-room spike shoots right, then two more drop near the goal!",
}

SPIKES_L3 = {
 # Exact tile grid from JS: pyramid shape with spikes along floor
 'tiles': [
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,
  1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
  1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
 ],
 # player at row 8 open area (y=288 = feet at top of row 9 solid)
 'player': [80, 288],
 'goal':   [768, 288],
 # 21 spikes erupt from the floor (y=288 = top of row 9)
 # sensor/1 at x=192,y=192,w=32,h=64
 'traps': [
  *[dict(kind='spike', x=64+i*32, y=288, w=32, h=14,
         steps=[dict(ty=-1, t=0.25, d=round(i*0.2, 2))],
         sensor=(192,192,32,64))
    for i in range(21)],
 ],
 'hint': "Step past the hidden trigger and 21 spikes erupt like a wave!",
}

# ██████  PUSH  ████████████████████████████████████████████████████████████████

PUSH_L1 = {
 'tiles': [
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
  1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
  1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
  1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
  1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
 ],
 'player': [192, 320],
 'goal':   [640, 320],
 # Block1 x=512,y=320,w=32,h=64: timeline up-left-down loop, triggered by sensor/1 (448,192,32,128)
 # Block2 x=448,y=320,w=32,h=96: timeline up-down loop, triggered by sensor/2 (352,192,96,32)
 # Spike at x=416,y=320 (static)
 'traps': [
  dict(kind='spike', x=416, y=320, w=32, h=14, steps=[], sensor=None),
  dict(kind='mblock', x=512,y=320,w=32,h=64,
       sensor=(448,192,32,128),
       steps=[dict(ty=-2,t=0.25), dict(tx=-2,t=0.25,d=0.5), dict(ty=2,t=0.5,d=1,e='ease-in')],
       loop=True, auto=False),
  dict(kind='mblock', x=448,y=320,w=32,h=96,
       sensor=(352,192,96,32),
       steps=[dict(ty=-3,t=0.25), dict(ty=3,t=0.5,d=1,e='ease-in')],
       loop=True, auto=False),
 ],
 'hint': "Enter the sensor to start the lift cycle, then time your ride!",
}

PUSH_L2 = {
 'tiles': [
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
  1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
  1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
  1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
  1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,1,1,
 ],
 'player': [192, 320],
 'goal':   [640, 320],
 # Big wall sweeps: x=32,y=320,w=288,h=32 rises then sweeps right on sensor (352,192,32,128)
 # Block at x=416,y=320,w=160,h=160: slides tx=4.5,t=0.5 same sensor
 'traps': [
  dict(kind='mblock', x=32,y=320,w=288,h=32,
       sensor=(352,192,32,128),
       steps=[dict(ty=-1,t=0.25), dict(tx=4,t=0.5,d=0.1)],
       loop=False, auto=False),
  dict(kind='mblock', x=416,y=320,w=160,h=160,
       sensor=(352,192,32,128),
       steps=[dict(tx=4.5,t=0.5)],
       loop=False, auto=False),
 ],
 'hint': "A wall sweeps right – duck through the gap or get crushed!",
}

PUSH_L3 = {
 'tiles': [
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,
  1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,
  1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,
  1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,
  1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,
  1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,
 ],
 'player': [160, 320],
 'goal':   [672, 320],
 # Block1 x=320,y=320,w=32,h=96: sensor/1 (248,192,32,128) up-down loop
 #   Also has sensor/2 (376,192,32,128) alt timeline: up then slides right tx=5
 # Block2 x=608,y=320,w=32,h=96: sensor/3 (536,192,32,128) up-down loop
 # Use simple up-down for each
 'traps': [
  dict(kind='mblock', x=320,y=320,w=32,h=96,
       sensor=(248,192,32,128),
       steps=[dict(ty=-3,t=0.25), dict(ty=3,t=0.5,d=0.25,e='ease-in')],
       loop=True, auto=False),
  dict(kind='mblock', x=608,y=320,w=32,h=96,
       sensor=(536,192,32,128),
       steps=[dict(ty=-3,t=0.25), dict(ty=3,t=0.5,d=0.25,e='ease-in')],
       loop=True, auto=False),
 ],
 'hint': "Two pillars pop up from separate triggers – bait each one then cross!",
}

# ██████  PLATFORMS  ###########################################################

PLATFORMS_L1 = {
 'tiles': [
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
  1,1,1,1,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
  1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
  1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
  1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
  1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
  1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
 ],
 'player': [96,  288],
 'goal':   [736, 288],
 # Platform1 x=384,y=288,w=96,h=32: drops ty=7 on sensor/1 (352,160,32,128)
 # Platform2 x=224,y=288,w=96,h=32: slides tx=2 on sensor/1
 # Platform3 x=544,y=288,w=96,h=32: flies up ty=-3 on sensor/2 (512,96,32,192)
 # Platform4 x=384,y=512,w=96,h=32: rises ty=-14 on sensor/1 (fake floor below view)
 'traps': [
  dict(kind='mblock', x=384,y=288,w=96,h=32,
       sensor=(352,160,32,128),
       steps=[dict(ty=7,t=0.4,e='ease-in')], loop=False, auto=False),
  dict(kind='mblock', x=224,y=288,w=96,h=32,
       sensor=(352,160,32,128),
       steps=[dict(tx=2,t=0.2)], loop=False, auto=False),
  dict(kind='mblock', x=544,y=288,w=96,h=32,
       sensor=(512,96,32,192),
       steps=[dict(ty=-3,t=0.25,e='ease-in-out')], loop=False, auto=False),
  dict(kind='mblock', x=384,y=512,w=96,h=32,
       sensor=(352,160,32,128),
       steps=[dict(ty=-14,t=6,d=1)], loop=False, auto=False),
 ],
 'hint': "The middle platform drops! Use the sides as stepping stones.",
}

PLATFORMS_L2 = {
 'tiles': [
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
  1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
  1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
  1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
  1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
  1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
  1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
 ],
 'player': [96,  288],
 'goal':   [736, 288],
 # 10 domino blocks x=160..448 each 32x32 drop in sequence on sensor/1 (193,192,32,96)
 # Big platform x=448,y=288,w=96 slides then drops on sensor/2 (480,192) + sensor/3 (448,128)
 # Several more smaller blocks x=544+,w=160
 'traps': [
  *[dict(kind='mblock', x=160+i*32,y=288,w=32,h=32,
         sensor=(193,192,32,96),
         steps=[dict(ty=7,t=0.5,d=i*0.25,e='ease-in')],
         loop=False, auto=False)
    for i in range(10)],
  dict(kind='mblock', x=448,y=288,w=96,h=32,
       sensor=(480,192,32,96),
       steps=[dict(tx=3,t=2,d=1.5,e='ease-in'), dict(ty=7,t=0.5,d=2,e='ease-in')],
       loop=False, auto=False),
  dict(kind='mblock', x=544,y=288,w=160,h=32,
       sensor=(480,192,32,96),
       steps=[dict(ty=7,t=0.5,d=0.4,e='ease-in')],
       loop=False, auto=False),
 ],
 'hint': "The whole floor is fake – sprint before the domino eats you!",
}

PLATFORMS_L3 = {
 'tiles': [
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
  1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,1,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
 ],
 'player': [96,  224],
 'goal':   [736, 384],
 # Oscillating platform x=128,y=224,w=96: auto loop left-right
 # Platform2 x=288,y=224,w=96: slides tx=6 on sensor/1 (160,128,32,96)
 # Goal-area platform x=608,y=384,w=96: drops ty=4 on sensor/2 (576,240,64,16)
 # Top platform x=736,y=224,w=128: wobble then falls on sensor/2+3
 # Left floor platform x=64,y=384: drops on sensor/4 (64,288,224,32)
 'traps': [
  dict(kind='mblock', x=128,y=224,w=96,h=32,
       sensor=None,
       steps=[dict(tx=5,t=2,d=1.25,e='ease-in-out'),
              dict(tx=-5,t=2,d=0.5,e='ease-in-out')],
       loop=True, auto=True),
  dict(kind='mblock', x=288,y=224,w=96,h=32,
       sensor=(160,128,32,96),
       steps=[dict(tx=6,t=0.5,d=0.5,e='ease-in')],
       loop=False, auto=False),
  dict(kind='mblock', x=608,y=384,w=96,h=96,
       sensor=(576,240,64,16),
       steps=[dict(ty=4,t=0.3,e='ease-in')],
       loop=False, auto=False),
  dict(kind='mblock', x=736,y=224,w=128,h=32,
       sensor=(768,128,32,96),
       steps=[dict(ty=2,t=1.5,e='ease-in-out'), dict(tx=-2,t=0.2,e='ease-in-out'),
              dict(ty=-2,t=0.2,d=0.2)],
       loop=False, auto=False),
  dict(kind='mblock', x=64,y=384,w=192,h=96,
       sensor=(64,288,224,32),
       steps=[dict(ty=4,t=0.3,e='ease-in')],
       loop=False, auto=False),
 ],
 'hint': "The goal platform drops when you step on the hidden floor trigger!",
}

# ██████  SAWS  ████████████████████████████████████████████████████████████████
# NOTE: The original "Saws" levels contain no actual SAW objects.
# They use moving blocks + spikes that behave like saw traps.
# We replicate the exact tile grids and trap mechanics here.

SAWS_L1 = {
 'tiles': [
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
  1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
  1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
  1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
  1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
  1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,
 ],
 'player': [128, 256],
 'goal':   [704, 256],
 # Block x=448,y=0,w=128,h=64: drops ty=2,t=0.25 on sensor/1 (472,192,64,64)
 # Block x=448,y=256,w=64,h=224: slides tx=2,t=0.5 on sensor/1
 # Spikes-top (gid=10) at x=448,96  x=480,96  x=512,96  x=544,96 – drop ty=2 same sensor
 'traps': [
  dict(kind='mblock', x=448,y=0,w=128,h=64,
       sensor=(472,192,64,64),
       steps=[dict(ty=2,t=0.25)], loop=False, auto=False),
  dict(kind='mblock', x=448,y=256,w=64,h=224,
       sensor=(472,192,64,64),
       steps=[dict(tx=2,t=0.5,e='ease-out')], loop=False, auto=False),
  # spikes-top treated as spikes that drop down
  dict(kind='spike', x=448,y=96, w=32,h=14,
       steps=[dict(ty=2,t=0.25)], sensor=(472,192,64,64)),
  dict(kind='spike', x=480,y=96, w=32,h=14,
       steps=[dict(ty=2,t=0.25)], sensor=(472,192,64,64)),
  dict(kind='spike', x=512,y=96, w=32,h=14,
       steps=[dict(ty=2,t=0.25)], sensor=(472,192,64,64)),
  dict(kind='spike', x=544,y=96, w=32,h=14,
       steps=[dict(ty=2,t=0.25)], sensor=(472,192,64,64)),
 ],
 'hint': "The ceiling block drops and slides – sprint through before it seals the gap!",
}

SAWS_L2 = {
 'tiles': [
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
  1,1,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,
  1,1,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
 ],
 'player': [96,  320],
 'goal':   [688, 320],
 # Block x=544,y=256,w=32,h=64: rises ty=-1 on sensor/1 (512,192,32,32)
 # Static spike at x=288,y=256  x=416,y=256
 # Pop spike at x=544,y=256 same sensor/1
 # Spring at x=624,y=336: rises on sensor/2 (624,312,32,32) – treat as block
 # Pop spikes x=736,y=352 and x=768,y=352 on sensor/2
 'traps': [
  dict(kind='mblock', x=544,y=256,w=32,h=64,
       sensor=(512,192,32,32),
       steps=[dict(ty=-1,t=0.25)], loop=False, auto=False),
  dict(kind='spike', x=288, y=256, w=32, h=14, steps=[], sensor=None),
  dict(kind='spike', x=416, y=256, w=32, h=14, steps=[], sensor=None),
  dict(kind='spike', x=544, y=256, w=32, h=14,
       steps=[dict(ty=-1,t=0.25)], sensor=(512,192,32,32)),
  dict(kind='spike', x=736, y=352, w=32, h=14,
       steps=[dict(ty=-1,t=0.25)], sensor=(624,312,32,32)),
  dict(kind='spike', x=768, y=352, w=32, h=14,
       steps=[dict(ty=-1,t=0.25)], sensor=(624,312,32,32)),
 ],
 'hint': "Three traps: a block rises, and two spikes fire near the goal!",
}

SAWS_L3 = {
 'tiles': [
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
  1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
  1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
  1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
 ],
 # player=97,287 → round to 96,288
 'player': [96, 288],
 'goal':   [704, 288],
 # Block x=672,y=288,w=96,h=96: rises ty=-3 on sensor/1 (608,224,64,128)
 # Blocks (rise stagger) x=224,352 and 352,352 and 480,352 and 608,352 on sensor/2
 # sensor/2 at x=224,y=64,w=32,h=64 (triggered when player reaches mid upper area)
 # sensor/3 at x=544,y=32,w=32,h=96
 # sensor/4 at x=480,y=32,w=32,h=96
 # Spikes at y=384 over the full floor, rising on sensor/2
 'traps': [
  dict(kind='mblock', x=672,y=288,w=96,h=96,
       sensor=(608,224,64,128),
       steps=[dict(ty=-3,t=0.5,e='ease-in-out')], loop=False, auto=False),
  dict(kind='mblock', x=224,y=352,w=32,h=32,
       sensor=(224,64,32,64),
       steps=[dict(ty=-1,t=0.5,d=1)], loop=False, auto=False),
  dict(kind='mblock', x=352,y=352,w=32,h=64,
       sensor=(544,32,32,96),
       steps=[dict(ty=-2,t=0.5,d=0.25)], loop=False, auto=False),
  dict(kind='mblock', x=480,y=352,w=32,h=96,
       sensor=(544,32,32,96),
       steps=[dict(ty=-3,t=0.5,d=0.5)], loop=False, auto=False),
  dict(kind='mblock', x=608,y=352,w=32,h=128,
       sensor=(544,32,32,96),
       steps=[dict(ty=-4,t=0.5,d=0.75)], loop=False, auto=False),
  # spikes wave on sensor/2
  *[dict(kind='spike', x=160+i*32, y=384, w=32, h=14,
         steps=[dict(ty=-1,t=0.5)],
         sensor=(224,64,32,64))
    for i in range(16)],
 ],
 'hint': "Multiple traps trigger in sequence – learn the order before sprinting!",
}

# ─────────────────────────────────────────────────────────────────────────────
# MASTER TABLE
# ─────────────────────────────────────────────────────────────────────────────
LEVELS = [
    [GAPS_L1,      GAPS_L2,      GAPS_L3],
    [SPIKES_L1,    SPIKES_L2,    SPIKES_L3],
    [PUSH_L1,      PUSH_L2,      PUSH_L3],
    [PLATFORMS_L1, PLATFORMS_L2, PLATFORMS_L3],
    [SAWS_L1,      SAWS_L2,      SAWS_L3],
]
CAT_NAMES  = ["Gaps", "Spikes", "Push", "Platforms", "Saws"]
CAT_COLORS = [
    ( 70, 180, 168),
    (185,  75,  75),
    ( 75, 130, 185),
    (125,  75, 185),
    (185, 145,  50),
]

# ─────────────────────────────────────────────────────────────────────────────
# LEVEL  SCENE
# ─────────────────────────────────────────────────────────────────────────────
def _build_trap(td):
    kind = td['kind']
    sx = td.get('sensor')
    s_obj = Sensor(*sx) if sx else None

    if kind == 'mblock':
        return MBlock(td['x'], td['y'], td['w'], td['h'],
                      td['steps'], td.get('loop', False),
                      td.get('auto', False), s_obj)
    if kind == 'spike':
        return SpikeObj(td['x'], td['y'],
                        td.get('w', 32), td.get('h', 14),
                        td.get('steps', []), s_obj)
    return None


class LevelScene:
    def __init__(self, game, ci, li):
        self.game   = game
        self.ci, self.li = ci, li
        self.data   = LEVELS[ci][li]
        self._build()
        self.flash  = 0.0
        self.hint_t = 5.0
        self.win    = False
        self.win_t  = 0.0
        self.run_deaths = 0

    def _build(self):
        d = self.data
        self._static_plats = tiles_to_rects(d['tiles'])
        px, py = d['player']
        self.player = Player(px, py)
        gx, gy = d['goal']
        self.gx, self.gy = gx, gy
        self.goal_rect = pygame.Rect(gx-8, gy-48, 22, 48)

        self._mblocks = []
        self._spikes  = []
        for td in d.get('traps', []):
            obj = _build_trap(td)
            if obj is None: continue
            if isinstance(obj, MBlock):   self._mblocks.append(obj)
            if isinstance(obj, SpikeObj): self._spikes.append(obj)

        self._rebuild_plats()

    def _rebuild_plats(self):
        self._platforms = list(self._static_plats)
        for mb in self._mblocks:
            self._platforms.append(mb.rect)

    def _carry_player_with_moving_blocks(self, player, prect):
        for mb in self._mblocks:
            old_r = mb.prev_rect
            new_r = mb.rect
            dx = new_r.x - old_r.x
            dy = new_r.y - old_r.y
            if dx == 0 and dy == 0:
                continue

            stood_on_top = (
                prect.bottom >= old_r.top - 6 and
                prect.bottom <= old_r.top + 4 and
                prect.right > old_r.left + 2 and
                prect.left < old_r.right - 2
            )
            if stood_on_top:
                player.x += dx
                player.y += dy
                prect = player.rect

    def _die(self):
        self.game.save['deaths'] = self.game.save.get('deaths', 0) + 1
        write_save(self.game.save)
        self.run_deaths += 1
        self.flash = 0.45
        self.win   = False
        self.win_t = 0.0
        px, py = self.data['player']
        self.player.reset_pos()
        self.player._sx, self.player._sy = float(px), float(py)
        self.player.x, self.player.y     = float(px), float(py)
        for mb in self._mblocks: mb.reset()
        for sp in self._spikes:  sp.reset()
        self._rebuild_plats()

    def handle_event(self, ev):
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_r:      self._die()
            if ev.key == pygame.K_ESCAPE: self.game.go_level_select(self.ci)

    def update(self, dt):
        if self.win:
            self.win_t += dt
            if self.win_t > 2.0:
                self.game.go_level_select(self.ci)
            return
        self.flash  = max(0, self.flash - dt)
        self.hint_t = max(0, self.hint_t - dt)

        keys  = pygame.key.get_pressed()
        p     = self.player
        pr    = p.rect

        p.handle_input(keys)
        for mb in self._mblocks: mb.update(dt, pr)
        for sp in self._spikes:  sp.update(dt, pr)
        self._rebuild_plats()
        self._carry_player_with_moving_blocks(p, pr)
        p.update(dt, self._platforms)

        pr = p.rect

        # Death: fall off screen
        if p.y > OH + 80:
            self._die(); return
        # Death: spike
        for sp in self._spikes:
            if pr.colliderect(sp.kill_rect()):
                self._die(); return
        # Death: crushed by moving block
        for mb in self._mblocks:
            mr = mb.rect
            # Crushing = block moving into player from side or above
            if pr.colliderect(mr):
                # Check if we couldn't resolve collision (block pushed player off-screen or into wall)
                # Simple check: if player is inside block after physics, they're crushed
                if not any(pr.colliderect(sp) for sp in self._static_plats if sp != mr):
                    # Only kill if not standing on top (that's normal platform riding)
                    if not (pr.bottom <= mr.top + 4 and p.vy >= 0):
                        self._die(); return

        # Win
        if pr.colliderect(self.goal_rect):
            self.win = True
            key = f"{self.ci}_{self.li}"
            self.game.save['completed'][key] = True
            ul = self.game.save['unlocked_lvls']
            ck = str(self.ci)
            if ck not in ul: ul[ck] = [0]
            if self.li + 1 < 3 and (self.li+1) not in ul[ck]:
                ul[ck].append(self.li+1)
            if all(self.game.save['completed'].get(f"{self.ci}_{x}", False)
                   for x in range(3)):
                if self.ci+1 < 5:
                    if (self.ci+1) not in self.game.save['unlocked_cats']:
                        self.game.save['unlocked_cats'].append(self.ci+1)
                    nk = str(self.ci+1)
                    if nk not in ul: ul[nk] = [0]
            write_save(self.game.save)

    def draw(self, surf):
        ox, oy = OX, OY

        # Background
        surf.fill(TEAL)
        pygame.draw.rect(surf, TEAL_DARK, (ox, oy, OW, OH))

        # ── Draw tile grid ──
        # 1) Fill all solid tiles with cream
        tiles = self.data['tiles']
        for row in range(15):
            for col in range(27):
                if tiles[row*27+col]:
                    r = pygame.Rect(ox+col*TILE, oy+row*TILE, TILE, TILE)
                    pygame.draw.rect(surf, CREAM, r)

        # 2) Draw grid lines over whole world area
        for col in range(28):
            x = ox + col*TILE
            pygame.draw.line(surf, CREAM_LINE, (x, oy), (x, oy+OH), 1)
        for row in range(16):
            y = oy + row*TILE
            pygame.draw.line(surf, CREAM_LINE, (ox, y), (ox+OW, y), 1)

        # 3) Clip grid lines to solid tile interiors
        for row in range(15):
            for col in range(27):
                if tiles[row*27+col]:
                    r = pygame.Rect(ox+col*TILE+1, oy+row*TILE+1, TILE-2, TILE-2)
                    pygame.draw.rect(surf, CREAM, r)

        # ── Moving blocks – look IDENTICAL to normal tiles ──
        for mb in self._mblocks:
            mb.draw(surf, ox, oy)

        # ── Spikes ──
        for sp in self._spikes:
            sp.draw(surf, ox, oy)

        # ── Flag / Goal ──
        draw_flag(surf, self.gx + ox, self.gy + oy)

        # ── Player ──
        self.player.draw(surf, ox, oy)

        # ── Death flash ──
        if self.flash > 0:
            a = int(160 * self.flash / 0.45)
            fl = pygame.Surface((SW, SH), pygame.SRCALPHA)
            fl.fill((*RED_FLASH, a))
            surf.blit(fl, (0, 0))

        # ── Win overlay ──
        if self.win:
            a = min(220, int(self.win_t * 500))
            ov = pygame.Surface((SW, SH), pygame.SRCALPHA)
            ov.fill((38, 166, 154, a))
            surf.blit(ov, (0, 0))
            if self.win_t > 0.25:
                draw_text(surf, "LEVEL COMPLETE!", 52, WHITE, SW//2, SH//2-36)
                draw_text(surf, f"Deaths this run: {self.run_deaths}", 26, YELLOW, SW//2, SH//2+18)
                draw_text(surf, "Returning to level select...", 18, WHITE, SW//2, SH//2+58, bold=False)

        # ── Top bar ──
        pygame.draw.rect(surf, TEAL_DARK, (0, 0, SW, TOP_H))
        pygame.draw.line(surf, (80, 100, 100), (0, TOP_H), (SW, TOP_H), 1)

        _draw_exit_icon(surf, 28, TOP_H//2)
        draw_text(surf, "Back", 14, WHITE, 70, TOP_H//2, bold=False)
        draw_text(surf, CAT_NAMES[self.ci], 26, WHITE, SW//2 - 60, TOP_H//2)

        for li in range(3):
            done  = self.game.save['completed'].get(f"{self.ci}_{li}", False)
            fx    = SW//2 + 10 + li*28
            fy    = TOP_H//2
            color = WHITE if done else (80, 100, 100)
            draw_flag_icon(surf, fx, fy, size=12, color=color, filled=(li == self.li or done))

        total_d = self.game.save.get('deaths', 0)
        draw_splotch_icon(surf, SW-46, TOP_H//2, 18, WHITE, total_d)
        _draw_sound_icons(surf, SW-120, TOP_H//2)

        if self.hint_t > 0:
            hint = self.data.get('hint', '')
            if hint:
                alpha = min(255, int(255 * min(1.0, self.hint_t / 1.5)))
                fs = get_font(16, False).render(hint, True, WHITE)
                fs.set_alpha(alpha)
                surf.blit(fs, fs.get_rect(center=(SW//2, SH - 22)))


def _draw_exit_icon(surf, cx, cy):
    s = 18
    pts = [(cx-s//2, cy), (cx, cy-s//2+3), (cx, cy+s//2-3)]
    pygame.draw.polygon(surf, WHITE, pts)
    pygame.draw.rect(surf, WHITE, (cx, cy-s//3, s//2, s*2//3), 2)

def _draw_sound_icons(surf, cx, cy):
    for i, offset in enumerate([-18, 0]):
        x = cx + offset
        pygame.draw.rect(surf, WHITE, (x-5, cy-5, 6, 10), 1)
        pts = [(x-5,cy-5),(x+4,cy-10),(x+4,cy+10),(x-5,cy+5)]
        pygame.draw.polygon(surf, WHITE, pts, 1)
        pygame.draw.line(surf, WHITE, (x+6,cy-5),(x+12,cy+5), 2)
        pygame.draw.line(surf, WHITE, (x+12,cy-5),(x+6,cy+5), 2)

# ─────────────────────────────────────────────────────────────────────────────
# LEVEL  SELECT  SCENE
# ─────────────────────────────────────────────────────────────────────────────
class LevelSelectScene:
    def __init__(self, game, ci):
        self.game = game
        self.ci   = ci
        self.hover = -1

    def _btns(self):
        bw, bh = 220, 130
        gap    = 24
        total  = 3*bw + 2*gap
        x0     = (SW - total)//2
        y0     = SH//2 - bh//2 + 20
        return [pygame.Rect(x0+i*(bw+gap), y0, bw, bh) for i in range(3)]

    def handle_event(self, ev):
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            self.game.go_category_select()
        if ev.type == pygame.MOUSEMOTION:
            self.hover = -1
            for i,r in enumerate(self._btns()):
                if r.collidepoint(ev.pos): self.hover = i
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            unl = self.game.save['unlocked_lvls'].get(str(self.ci), [0])
            for i,r in enumerate(self._btns()):
                if r.collidepoint(ev.pos) and i in unl:
                    self.game.go_level(self.ci, i)

    def update(self, dt): pass

    def draw(self, surf):
        surf.fill(TEAL)
        cc = CAT_COLORS[self.ci]
        draw_text(surf, CAT_NAMES[self.ci], 42, WHITE, SW//2, TOP_H+54)
        draw_text(surf, "Choose a Level", 20, (200,240,235), SW//2, TOP_H+96, bold=False)
        unl = self.game.save['unlocked_lvls'].get(str(self.ci), [0])
        for i,r in enumerate(self._btns()):
            locked = i not in unl
            done   = self.game.save['completed'].get(f"{self.ci}_{i}", False)
            hov    = (self.hover==i and not locked)
            bg = (min(255,cc[0]+20),min(255,cc[1]+20),min(255,cc[2]+20)) if hov else TEAL_DARK
            if done: bg = (45,155,75)
            rrect(surf, bg, r, 14)
            pygame.draw.rect(surf, WHITE if not locked else GREY, r, 2, border_radius=14)
            draw_text(surf, f"Level {i+1}", 26, WHITE if not locked else GREY, r.centerx, r.centery-16)
            if locked:
                draw_lock(surf, r.centerx, r.centery+10, 28)
            elif done:
                draw_text(surf, "✓", 36, YELLOW, r.centerx, r.centery+16)
            else:
                draw_text(surf, "▶", 30, WHITE, r.centerx, r.centery+16)

        pygame.draw.rect(surf, TEAL_DARK, (0,0,SW,TOP_H))
        pygame.draw.line(surf, GREY, (0,TOP_H),(SW,TOP_H),1)
        _draw_exit_icon(surf, 28, TOP_H//2)
        draw_text(surf, "Back", 14, WHITE, 70, TOP_H//2, bold=False)
        draw_text(surf, CAT_NAMES[self.ci], 24, WHITE, SW//2, TOP_H//2)
        draw_splotch_icon(surf, SW-46, TOP_H//2, 18, WHITE, self.game.save.get('deaths',0))
        _draw_sound_icons(surf, SW-120, TOP_H//2)

# ─────────────────────────────────────────────────────────────────────────────
# CATEGORY  SELECT  SCENE
# ─────────────────────────────────────────────────────────────────────────────
class CategorySelectScene:
    def __init__(self, game):
        self.game  = game
        self.hover = -1
        self.reset_confirm = False

    def _cards(self):
        cw,ch = 162, 290
        gap   = 12
        total = 5*cw + 4*gap
        x0    = (SW-total)//2
        y0    = TOP_H + 110
        return [pygame.Rect(x0+i*(cw+gap), y0, cw, ch) for i in range(5)]

    def _reset_btn(self):
        return pygame.Rect(SW//2-85, SH-46, 170, 32)

    def handle_event(self, ev):
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
            if ev.key == pygame.K_r and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                if self.reset_confirm: self.game.reset_save()
                else: self.reset_confirm = True
        if ev.type == pygame.MOUSEMOTION:
            self.hover = -1
            for i,r in enumerate(self._cards()):
                if r.collidepoint(ev.pos): self.hover = i
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button==1:
            mx,my = ev.pos
            for i,r in enumerate(self._cards()):
                if r.collidepoint(ev.pos):
                    if i in self.game.save['unlocked_cats']:
                        self.game.go_level_select(i)
                    self.reset_confirm = False
                    return
            if self._reset_btn().collidepoint(mx,my):
                if self.reset_confirm: self.game.reset_save()
                else: self.reset_confirm = True
            else:
                self.reset_confirm = False

    def update(self, dt): pass

    def draw(self, surf):
        surf.fill(TEAL)
        deaths = self.game.save.get('deaths', 0)

        draw_text(surf, "SPLOTCH", 60, WHITE, SW//2, TOP_H+50)
        draw_text(surf, "How far can you go before you get splotched?",
                  16, (200,240,235), SW//2, TOP_H+88, bold=False)

        tips  = ["Fake floors","Pop-up spikes","Sneaky blocks",
                 "Shifting platforms","Hidden traps"]

        for i,r in enumerate(self._cards()):
            unl  = i in self.game.save['unlocked_cats']
            cc   = CAT_COLORS[i]
            hov  = (self.hover==i and unl)
            bg   = (min(255,cc[0]+(20 if hov else 0)),
                    min(255,cc[1]+(20 if hov else 0)),
                    min(255,cc[2]+(20 if hov else 0))) if unl else (50,62,62)
            fg   = WHITE if unl else GREY
            rrect(surf, bg, r, 16)
            pygame.draw.rect(surf, WHITE if unl else (80,90,90), r, 2, border_radius=16)

            draw_text(surf, CAT_NAMES[i], 18, fg, r.centerx, r.y+26)

            if not unl:
                draw_lock(surf, r.centerx, r.centery, 38)
                draw_text(surf, "Complete\nprevious" if i>0 else "???",
                          11, (100,110,110), r.centerx, r.bottom-32, bold=False)
            else:
                for li in range(3):
                    done = self.game.save['completed'].get(f"{i}_{li}", False)
                    dx   = r.centerx - 18 + li*18
                    dy   = r.y + 52
                    pygame.draw.circle(surf, YELLOW if done else (fg[0]//3+30,fg[1]//3+30,fg[2]//3+30), (dx,dy), 7)
                    if done: pygame.draw.circle(surf, fg, (dx,dy), 4)

                draw_text(surf, tips[i], 13, fg, r.centerx, r.bottom-30, bold=False)

        draw_splotch_icon(surf, SW-56, TOP_H+34, 26, WHITE, deaths)
        draw_text(surf, "deaths", 12, WHITE, SW-56, TOP_H+65, bold=False)

        rb = self._reset_btn()
        rrect(surf, (190,70,70) if self.reset_confirm else (50,100,95), rb, 8)
        draw_text(surf, "Confirm Reset?" if self.reset_confirm else "Reset Save",
                  15, WHITE, rb.centerx, rb.centery)
        draw_text(surf, "Click category  |  Ctrl+R = reset save",
                  13, (170,220,215), SW//2, SH-14)

        pygame.draw.rect(surf, TEAL_DARK, (0,0,SW,TOP_H))
        pygame.draw.line(surf, GREY, (0,TOP_H),(SW,TOP_H),1)
        draw_text(surf, "SPLOTCH", 26, WHITE, SW//2, TOP_H//2)
        draw_splotch_icon(surf, SW-46, TOP_H//2, 16, WHITE, deaths)
        _draw_sound_icons(surf, SW-120, TOP_H//2)

# ─────────────────────────────────────────────────────────────────────────────
# GAME
# ─────────────────────────────────────────────────────────────────────────────
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SW, SH))
        pygame.display.set_caption("Splotch – Precision Platformer")
        self.clock  = pygame.time.Clock()
        self.save   = load_save()
        self.scene  = CategorySelectScene(self)

    def go_category_select(self): self.scene = CategorySelectScene(self)
    def go_level_select(self, ci): self.scene = LevelSelectScene(self, ci)
    def go_level(self, ci, li):    self.scene = LevelScene(self, ci, li)

    def reset_save(self):
        self.save  = default_save()
        write_save(self.save)
        self.scene = CategorySelectScene(self)

    def run(self):
        while True:
            dt = min(self.clock.tick(FPS)/1000.0, 0.05)
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    mx, my = ev.pos
                    if my < TOP_H and mx < 100:
                        if isinstance(self.scene, LevelScene):
                            self.go_level_select(self.scene.ci); continue
                        elif isinstance(self.scene, LevelSelectScene):
                            self.go_category_select(); continue
                self.scene.handle_event(ev)
            self.scene.update(dt)
            self.scene.draw(self.screen)
            pygame.display.flip()


if __name__ == "__main__":
    Game().run()
