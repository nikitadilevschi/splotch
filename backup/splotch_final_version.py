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

# Extended depth palette
TEAL_LIGHT  = ( 68, 200, 188)
TEAL_DEEP   = ( 10,  62,  57)
TEAL_MID    = ( 32, 142, 132)
CARD_BG     = ( 20,  96,  88)
GREEN_DONE  = ( 46, 190,  80)
GREEN_DK    = ( 28, 138,  54)
ORANGE_WARM = (255, 162,  42)

# Physics  (pixels / second)
GRAVITY  = 1400
MAX_FALL = 850
JUMP_V   = -420
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
        _fonts[k] = pygame.font.SysFont("Segoe UI", size, bold=bold)
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
    """Draw a single tile-sized block with the solid-tile colour."""
    pygame.draw.rect(surf, TEAL_DARK, rect)

def draw_tiled_platform(surf, rect, ox, oy):
    """Draw a moving-block rect looking identical to normal floor tiles."""
    r = rect.move(ox, oy)
    pygame.draw.rect(surf, TEAL_DARK, r)

def draw_player(surf, x, y, w=26, h=26):
    """Orange square with big cartoon eyes and eye-glint."""
    r = pygame.Rect(int(x - w//2), int(y - h), w, h)
    pygame.draw.rect(surf, ORANGE, r, border_radius=6)
    pygame.draw.rect(surf, ORANGE_DK, r, 2, border_radius=6)
    ew = 8; eh = 8
    lx = r.x + 4;  rx2 = r.right - 4 - ew
    ey2 = r.y + 6
    pygame.draw.ellipse(surf, WHITE, (lx, ey2, ew, eh))
    pygame.draw.ellipse(surf, WHITE, (rx2, ey2, ew, eh))
    pygame.draw.circle(surf, BLACK, (lx + ew//2 + 1, ey2 + eh//2 + 1), 3)
    pygame.draw.circle(surf, BLACK, (rx2 + ew//2 + 1, ey2 + eh//2 + 1), 3)
    # specular glints
    pygame.draw.circle(surf, WHITE, (lx + 2, ey2 + 2), 1)
    pygame.draw.circle(surf, WHITE, (rx2 + 2, ey2 + 2), 1)

def draw_flag(surf, fx, fy):
    """Goal flag – pole with shadow + warm orange triangular flag."""
    pole_h = 48
    top    = fy - pole_h
    pygame.draw.line(surf, (40, 42, 40), (fx, fy), (fx, top), 3)
    pts = [(fx, top), (fx + 24, top + 12), (fx, top + 24)]
    pygame.draw.polygon(surf, ORANGE_DK, [(x+1, y+1) for x, y in pts])
    pygame.draw.polygon(surf, ORANGE, pts)
    pygame.draw.polygon(surf, ORANGE_WARM, pts, 1)

def draw_spike(surf, cx, bot_y):
    """Single upward spike – grey, looks like a tile when flush."""
    hw = 11; h = 16
    pts = [(cx, bot_y - h), (cx - hw, bot_y), (cx + hw, bot_y)]
    pygame.draw.polygon(surf, (180, 180, 180), pts)
    pygame.draw.polygon(surf, (80, 80, 80), pts, 1)

def get_saw_blade_radius(rect):
    """Return the radius of the saw blade for collision detection."""
    return min(rect.width, rect.height) // 2 - 4

def check_saw_collision(player_rect, saw_rect):
    """Check if player collides with the circular saw blade (not the platform)."""
    # Get saw blade center and radius
    cx = saw_rect.centerx
    cy = saw_rect.centery
    radius = get_saw_blade_radius(saw_rect)

    # Check if any part of the player rect is close enough to the saw blade center
    # Find closest point on player rect to saw center
    closest_x = max(player_rect.left, min(cx, player_rect.right))
    closest_y = max(player_rect.top, min(cy, player_rect.bottom))

    # Distance from saw center to closest point on player rect
    dx = cx - closest_x
    dy = cy - closest_y
    distance = math.sqrt(dx*dx + dy*dy)

    # Collision if distance is less than saw radius (with some padding for player size)
    return distance < radius + 8

def draw_saw(surf, rect, ox, oy, rotation=0):
    """Draw a circular saw blade with rotating teeth."""
    r = rect.move(ox, oy)

    # Draw saw circle in the center
    cx = r.centerx
    cy = r.centery
    radius = get_saw_blade_radius(rect)

    # Saw blade circle (red/orange)
    pygame.draw.circle(surf, (220, 80, 50), (cx, cy), radius)
    pygame.draw.circle(surf, (140, 40, 20), (cx, cy), radius, 2)

    # Draw saw teeth (triangular spikes around the circle) with rotation
    num_teeth = 8
    for i in range(num_teeth):
        angle = (i / num_teeth) * 2 * math.pi + rotation
        # Outer tooth point
        tx = cx + math.cos(angle) * (radius + 6)
        ty = cy + math.sin(angle) * (radius + 6)
        # Inner base points
        angle_next = ((i + 1) / num_teeth) * 2 * math.pi + rotation
        tx1 = cx + math.cos(angle - 0.3) * radius
        ty1 = cy + math.sin(angle - 0.3) * radius
        tx2 = cx + math.cos(angle_next + 0.3) * radius
        ty2 = cy + math.sin(angle_next + 0.3) * radius

        pygame.draw.polygon(surf, (240, 100, 60), [(tx, ty), (tx1, ty1), (tx2, ty2)])

    # Central hub (darker)
    pygame.draw.circle(surf, (80, 40, 30), (cx, cy), radius // 3)

def draw_splotch_icon(surf, cx, cy, r, color, num):
    n = 10
    pts = []
    for i in range(n):
        a  = i * 2*math.pi/n
        dr = r * (0.65 + 0.35 * math.sin(i*3.9 + 1.1))
        pts.append((cx + math.cos(a)*dr, cy + math.sin(a)*dr))
    spts = [(int(x+1), int(y+1)) for x, y in pts]
    pygame.draw.polygon(surf, TEAL_DEEP, spts)
    pygame.draw.polygon(surf, color, [(int(x), int(y)) for x, y in pts])
    draw_text(surf, str(num), max(9, r-5), BLACK, cx, cy)

def draw_lock(surf, cx, cy, size=30):
    hw = size//3
    body = pygame.Rect(cx-hw, cy-hw//2, hw*2, int(hw*1.4))
    pygame.draw.rect(surf, (50, 62, 60), body.move(1, 2), border_radius=3)
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
# MODERN  UI  HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _alpha_rect(surf, rgba, rect, radius=0):
    """Blit a translucent (optionally rounded) rect onto surf."""
    r = rect if isinstance(rect, pygame.Rect) else pygame.Rect(*rect)
    w, h = max(1, r.width), max(1, r.height)
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    if radius > 0:
        pygame.draw.rect(s, rgba, (0, 0, w, h), border_radius=max(0, radius))
    else:
        s.fill(rgba)
    surf.blit(s, r.topleft)

def draw_shadow_card(surf, rect, radius=14):
    """Layered soft drop-shadow under a card rect."""
    for i in range(5, 0, -1):
        r2 = rect.inflate(i*2, i*2).move(2, i+1)
        if r2.width > 0 and r2.height > 0:
            _alpha_rect(surf, (6, 24, 20, i * 11), r2, radius + i)

def draw_modern_card(surf, rect, bg, radius=14, hover=False, border_color=None):
    """Shadow → fill → top-shine strip → border (+ hover glow)."""
    draw_shadow_card(surf, rect, radius)
    pygame.draw.rect(surf, bg, rect, border_radius=radius)
    shine_h = max(6, rect.height // 9)
    _alpha_rect(surf, (255, 255, 255, 22),
                pygame.Rect(rect.x+3, rect.y+3, rect.width-6, shine_h), radius-2)
    bc = border_color if border_color else WHITE
    pygame.draw.rect(surf, bc, rect, 2 if hover else 1, border_radius=radius)
    if hover:
        _alpha_rect(surf, (255, 255, 255, 18), rect.inflate(8, 8), radius + 4)

def draw_pill_badge(surf, text, size, fg, bg, cx, cy, px=12, py=5):
    """Pill-shaped badge with top shine. Returns the badge Rect."""
    f  = get_font(size)
    ts = f.render(str(text), True, fg)
    tw, th = ts.get_size()
    r  = pygame.Rect(0, 0, tw + px*2, th + py*2)
    r.center = (cx, cy)
    _alpha_rect(surf, (0, 0, 0, 45), r.move(1, 2), r.height // 2)
    pygame.draw.rect(surf, bg, r, border_radius=r.height // 2)
    _alpha_rect(surf, (255, 255, 255, 38),
                pygame.Rect(r.x+2, r.y+2, r.width-4, r.height//2), r.height//2)
    surf.blit(ts, ts.get_rect(center=(cx, cy)))
    return r

def draw_text_shadow(surf, text, size, color, cx, cy, bold=True, anchor="center"):
    """Draw text with a dark offset shadow for depth."""
    draw_text(surf, text, size, TEAL_DEEP, cx+2, cy+2, bold, anchor)
    draw_text(surf, text, size, color, cx, cy, bold, anchor)

def draw_bg_dots(surf):
    """Dark dot-grid background for menu screens."""
    surf.fill(TEAL_DEEP)
    for y in range(0, SH + 28, 28):
        for x in range(0, SW + 28, 28):
            pygame.draw.circle(surf, TEAL_MID, (x, y), 1)

def draw_category_icon(surf, ci, cx, cy, size, color):
    """Draw a clearly recognisable icon for each trap category."""
    s  = size
    lw = max(2, s // 22)

    if ci == 0:
        # ── GAPS: two floor slabs with a hole + down-arrow danger + player dot ──
        ph   = max(5, s // 8)
        pw   = s * 5 // 14
        gap  = s // 5
        bot  = cy + s // 6
        # left slab
        pygame.draw.rect(surf, color, (cx - gap//2 - pw, bot, pw, ph), border_radius=2)
        # right slab
        pygame.draw.rect(surf, color, (cx + gap//2,       bot, pw, ph), border_radius=2)
        # down-arrow inside the gap (danger)
        hw  = max(3, s // 12)
        ay2 = bot + ph + s // 7
        pygame.draw.line(surf, color, (cx, bot + 2), (cx, ay2 - hw - 1), lw)
        pygame.draw.polygon(surf, color,
                            [(cx - hw, ay2 - hw*2 + 1), (cx, ay2 + 1), (cx + hw, ay2 - hw*2 + 1)])
        # small player circle on left slab top
        pygame.draw.circle(surf, color,
                           (cx - gap//2 - pw//2, bot - s//8 - 2), max(3, s // 9))

    elif ci == 1:
        # ── SPIKES: flat floor base with three sharp triangles ──
        floor_y = cy + s // 5
        floor_h = max(4, s // 9)
        pygame.draw.rect(surf, color,
                         (cx - s//2 + 2, floor_y, s - 4, floor_h), border_radius=2)
        n_sp       = 3
        sp_w       = max(4, s // 10)
        sp_spacing = (s - 4) // n_sp
        for k in range(n_sp):
            sx     = cx - s//2 + 2 + sp_spacing * k + sp_spacing // 2
            tip_y  = floor_y - s * 2 // 5
            pygame.draw.polygon(surf, color,
                                [(sx, tip_y), (sx - sp_w, floor_y), (sx + sp_w, floor_y)])

    elif ci == 2:
        # ── PUSH: centred block with motion arrows on both sides (←□→) ──
        bsz = s * 2 // 5
        pygame.draw.rect(surf, color,
                         (cx - bsz//2, cy - bsz//2, bsz, bsz), border_radius=3)
        hw  = max(3, s // 11)
        arm = s // 4
        # left arrow ←
        lx0 = cx - bsz//2 - 4
        lx1 = lx0 - arm
        pygame.draw.line(surf, color, (lx0, cy), (lx1 + hw, cy), lw + 1)
        pygame.draw.polygon(surf, color,
                            [(lx1 + hw*2, cy - hw), (lx1, cy), (lx1 + hw*2, cy + hw)])
        # right arrow →
        rx0 = cx + bsz//2 + 4
        rx1 = rx0 + arm
        pygame.draw.line(surf, color, (rx0, cy), (rx1 - hw, cy), lw + 1)
        pygame.draw.polygon(surf, color,
                            [(rx1 - hw*2, cy - hw), (rx1, cy), (rx1 - hw*2, cy + hw)])

    elif ci == 3:
        # ── PLATFORMS: staircase of three floating bars (stepping stones) ──
        bar_w = s * 7 // 12
        bar_h = max(4, s // 9)
        # three bars offset in X and Y like stair steps
        steps = [
            (cx - s*3//10, cy + s//5),
            (cx,           cy),
            (cx + s*3//10, cy - s//5),
        ]
        for bx, by in steps:
            pygame.draw.rect(surf, color,
                             (bx - bar_w//2, by, bar_w, bar_h), border_radius=2)
        # small player square on the top bar
        psz = max(4, s // 8)
        top_bx, top_by = steps[2]
        pygame.draw.rect(surf, color,
                         (top_bx - psz//2, top_by - psz - 2, psz, psz), border_radius=2)

    else:
        # ── SAWS: gear blade with hollow hub + rotation arc ──
        n_teeth = 8
        pts = []
        for k in range(n_teeth * 2):
            a  = k * math.pi / n_teeth - math.pi / 8
            r2 = (s // 2) if k % 2 == 0 else int(s * 0.32)
            pts.append((int(cx + math.cos(a) * r2),
                        int(cy + math.sin(a) * r2)))
        pygame.draw.polygon(surf, color, pts)
        # hollow hub
        hub_r = max(3, s // 7)
        pygame.draw.circle(surf, TEAL_DEEP, (cx, cy), hub_r)
        pygame.draw.circle(surf, color, (cx, cy), hub_r, lw)
        # rotation arc + arrowhead (↻)
        arc_r   = s // 2 + s // 6
        a_start = math.pi * 0.25
        a_end   = math.pi * 1.20
        pygame.draw.arc(surf, color,
                        pygame.Rect(cx - arc_r, cy - arc_r, arc_r * 2, arc_r * 2),
                        a_start, a_end, lw)
        # arrowhead at the end of the arc
        tang = a_end + math.pi / 2
        tip  = (int(cx + math.cos(a_end) * arc_r),
                int(cy - math.sin(a_end) * arc_r))
        hw2  = max(3, s // 10)
        pygame.draw.polygon(surf, color, [
            (int(tip[0] + math.cos(tang + 0.5) * hw2),
             int(tip[1] + math.sin(tang + 0.5) * hw2)),
            (int(tip[0] + math.cos(tang + math.pi) * hw2 * 0.7),
             int(tip[1] + math.sin(tang + math.pi) * hw2 * 0.7)),
            (int(tip[0] + math.cos(tang - 0.5) * hw2),
             int(tip[1] + math.sin(tang - 0.5) * hw2)),
        ])

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
    def __init__(self, x, y, w, h, steps, loop=False, auto=False, sensor=None, is_saw=False):
        self.ox, self.oy = x, y
        self.w, self.h   = w, h
        self.sensor      = sensor
        self.auto        = auto
        self.is_saw      = is_saw
        self.runner      = TLRunner(x, y, steps, loop)
        self.prev_x, self.prev_y = float(x), float(y)
        self.saw_rotation = 0.0  # Rotation angle for spinning saw animation
        if auto: self.runner.activate()

    def reset(self):
        self.runner.reset()
        self.prev_x, self.prev_y = float(self.ox), float(self.oy)
        if self.auto: self.runner.activate()
        if self.sensor: self.sensor.reset()
        self.saw_rotation = 0.0

    def update(self, dt, prect):
        self.prev_x, self.prev_y = self.runner.x, self.runner.y
        if self.sensor and not self.runner.active:
            if self.sensor.check(prect):
                self.runner.activate()
        self.runner.update(dt)
        # Update saw rotation (spin continuously)
        if self.is_saw:
            self.saw_rotation += dt * 8.0  # Rotation speed in radians per second

    @property
    def prev_rect(self):
        return pygame.Rect(int(self.prev_x), int(self.prev_y), self.w, self.h)

    @property
    def rect(self):
        return pygame.Rect(int(self.runner.x), int(self.runner.y), self.w, self.h)

    def draw(self, surf, ox, oy):
        """Draw moving block - as a regular platform or saw blade."""
        if self.is_saw:
            draw_saw(surf, self.rect, ox, oy, self.saw_rotation)
        else:
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

    def draw(self, surf, ox, oy):
        if not self._triggered():
            return   # still hidden inside the floor tile – don't paint it
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
        dict(kind='spike', x=320, y=304, w=32, h=14, steps=[], sensor=None),
        dict(kind='spike', x=480, y=320, w=32, h=14,
             steps=[dict(ty=-0.5, t=0.25)],
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
        # static visible spikes (y = floor_y - 16 so base sits on floor)
        dict(kind='spike', x=192, y=304, w=32, h=14, steps=[], sensor=None),
        dict(kind='spike', x=416, y=336, w=32, h=14, steps=[], sensor=None),
        # hidden pop-up spikes – all start flush with floor and erupt upward
        dict(kind='spike', x=224, y=320, w=32, h=14,
             steps=[dict(ty=-0.5, t=0.25)], sensor=(224,224,32,96)),
        dict(kind='spike', x=640, y=320, w=32, h=14,
             steps=[dict(ty=-0.5, t=0.25)], sensor=(544,224,32,96)),
        dict(kind='spike', x=608, y=320, w=32, h=14,
             steps=[dict(ty=-0.5, t=0.25)], sensor=(544,224,32,96)),
        dict(kind='spike', x=576, y=320, w=32, h=14,
             steps=[dict(ty=-0.5, t=0.15, d=0.15)], sensor=(608,224,32,96)),
    ],
    'hint': "Mid-room spike erupts behind you, then two more burst near the goal!",
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
    # 21 spikes erupt from the floor automatically 1 second after level starts
    # Sensor at spike start position (x=96) triggers when player approaches
    'traps': [
        *[dict(kind='spike', x=64+i*32, y=288, w=32, h=14,
               steps=[dict(ty=-0.5, t=0.20, d=round(0.5 + i*0.15, 2))],
               sensor=(84,256,32,64))
          for i in range(21)],
    ],
    'hint': "When the level starts, 21 spikes will erupt after 1 second!",
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
    # Spike at x=416,y=306 (sitting on ground)
    'traps': [
        dict(kind='spike', x=416, y=306, w=32, h=14, steps=[], sensor=None),
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
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
        1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
        1,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
        1,1,0,0,1,1,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
        1,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
    ],
    'player': [96, 320],
    'goal': [704, 320],
    'traps': [
        # LOW PENDULUM SAW: Swings down-right then up-left near ground level
        # Forces player to jump over when it swings down
        dict(kind='mblock', x=200, y=240, w=80, h=32,
             sensor=None,
             steps=[dict(tx=2, ty=2, t=0.8, e='ease-in-out'),
                    dict(tx=-2, ty=-2, t=0.8, e='ease-in-out')],
             loop=True, auto=True, is_saw=True),

        # HIGH PENDULUM SAW: Swings up-left then down-right at mid-height
        # Opposite phase - when low saw is down, high saw is up (creates weaving pattern)
        # Forces player to weave under when it swings high
        dict(kind='mblock', x=500, y=180, w=80, h=32,
             sensor=None,
             steps=[dict(tx=-2, ty=-2, t=0.8, e='ease-in-out'),
                    dict(tx=2, ty=2, t=0.8, e='ease-in-out')],
             loop=True, auto=True, is_saw=True),
        #ease platform
        dict(kind='mblock', x=508, y=388, w=96, h=32,
             sensor=(480, 305, 120, 40),
             steps=[dict(ty=-6.0, t=0.75, e='ease-in-out')], loop=False, auto=False),
        # HIDDEN SPIKE AMBUSH: Fires near goal as final surprise
        dict(kind='spike', x=670, y=320, w=32, h=14,
             steps=[dict(ty=-0.5, t=0.18, d=0.0)],
             sensor=(640, 224, 64, 96)),
    ],
    'hint': "Jump low saw, navigate mid-platforms under high saw, dodge final spike!",
}

SAWS_L2 = {
    'tiles': [
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
        1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
        1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
        1,1,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,1,1,1,0,0,0,0,1,1,1,
        1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
    ],
    'player': [96, 320],
    'goal': [704, 320],
    'traps': [
        # GROUND-LEVEL HORIZONTAL SAW: Forces player onto platforms
        # Sweeps across at floor level (y=288), auto-looping
        dict(kind='mblock', x=200, y=288, w=96, h=32,
             sensor=None,
             steps=[dict(tx=4, t=1.0, e='ease-in-out'),
                    dict(tx=-4, t=1.0, e='ease-in-out')],
             loop=True, auto=True, is_saw=True),

        # MID-AIR OSCILLATING SAW: Punishes staying on platforms too long
        # Vertical bouncer at mid-height (y=192), auto-looping
        # Moves between y=192 and y=256, directly threatening both platforms
        dict(kind='mblock', x=400, y=192, w=64, h=32,
             sensor=None,
             steps=[dict(ty=2, t=0.7, e='ease-in-out'),
                    dict(ty=-2, t=0.7, e='ease-in-out')],
             loop=True, auto=True, is_saw=True),

        # SENSOR-TRIGGERED THIRD SAW: Adds ticking-clock pressure mid-run
        # Horizontal sweeper activates when player crosses midpoint
        # Forces player to keep moving or get caught in back half
        dict(kind='mblock', x=480, y=240, w=80, h=32,
             sensor=(400, 200, 64, 64),
             steps=[dict(tx=-3, t=0.85, e='ease-in-out'),
                    dict(tx=3, t=0.85, e='ease-in-out')],
             loop=True, auto=False, is_saw=True),

        # HIDDEN SPIKE AMBUSH 1: First staggered spike
        # Fires immediately when player approaches goal
        dict(kind='spike', x=645, y=320, w=32, h=14,
             steps=[dict(ty=-0.5, t=0.18, d=0.0)],
             sensor=(640, 224, 64, 96)),

        # HIDDEN SPIKE AMBUSH 2: Second staggered spike
        # Fires 0.2s after first spike, staggered ambush pattern
        dict(kind='spike', x=730, y=320, w=32, h=14,
             steps=[dict(ty=-0.5, t=0.18, d=0.2)],
             sensor=(640, 224, 64, 96)),
    ],
    'hint': "Ground saw forces platforms. Mid-air saw threatens staying. Third saw activates—rush to goal, but watch for spikes!",
}

SAWS_L3 = {
    'tiles': [
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
        1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
        1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
        1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
        1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
        1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
        1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
        1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
    ],
    # SAWS LEVEL 3: Corridor of horizontal saws with midpoint vertical hazard
    # Wide open floor with staggered horizontal saw patrols and a vertical dropping saw
    'player': [96, 320],
    'goal':   [704, 320],
    'traps': [
        # HORIZONTAL SAW 1: Left patrol - phase 0
        dict(kind='mblock', x=120,y=288,w=96,h=32,
             sensor=None,
             steps=[dict(tx=5,t=1.2,e='ease-in-out'),
                    dict(tx=-5,t=1.2,e='ease-in-out')],
             loop=True, auto=True, is_saw=True),

        # HORIZONTAL SAW 2: Center-left patrol - phase offset (starts at different point)
        dict(kind='mblock', x=320,y=288,w=96,h=32,
             sensor=None,
             steps=[dict(tx=-4.5,t=1.0,e='ease-in-out'),
                    dict(tx=4.5,t=1.0,e='ease-in-out')],
             loop=True, auto=True, is_saw=True),

        # HORIZONTAL SAW 3: Center-right patrol - phase offset (different timing)
        dict(kind='mblock', x=500,y=288,w=96,h=32,
             sensor=None,
             steps=[dict(tx=4,t=0.9,e='ease-in-out'),
                    dict(tx=-4,t=0.9,e='ease-in-out')],
             loop=True, auto=True, is_saw=True),

        # VERTICAL SAW: Drops from above when player crosses midpoint sensor
        dict(kind='mblock', x=400,y=120,w=64,h=32,
             sensor=(400,200,64,32),
             steps=[dict(ty=3.5,t=0.8,e='ease-in'),
                    dict(ty=-3.5,t=0.8,e='ease-out')],
             loop=True, auto=False, is_saw=True),

        # SPIKE TRAP 1: Left flank of goal - immediate trigger
        dict(kind='spike', x=670, y=352, w=32, h=14,
             sensor=(670,320,32,32)),

        # SPIKE TRAP 2: Right flank of goal - delayed trigger (0.3s delay)
        dict(kind='spike', x=740, y=352, w=32, h=14,
             sensor=(740,320,32,32),
             steps=[dict(ty=-1,t=0.3)]),

        dict(kind='spike', x=670, y=320, w=32, h=14,
             steps=[dict(ty=-0.5, t=0.18, d=0.0)],
             sensor=(640, 224, 64, 96)),
    ],
    'hint': "Time the horizontal saws, dodge the vertical saw at mid-point, and avoid the spike traps flanking the goal!",
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
                      td.get('auto', False), s_obj, td.get('is_saw', False))
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
            # Skip saws - they only have blade collision, not platform collision
            if mb.is_saw:
                continue
            r = mb.rect
            # Only collide with blocks still inside the playable world area.
            # Blocks that have fallen past OH, risen above 0, or slid off the
            # sides are no longer reachable and must not act as solid ground.
            if r.top < OH and r.bottom > 0 and r.left < OW and r.right > 0:
                self._platforms.append(r)

    def _carry_player_with_moving_blocks(self, player, prect):
        for mb in self._mblocks:
            # Skip saws - they don't carry the player
            if mb.is_saw:
                continue
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
        # Death: saw hazard (only when touching the actual saw blade, not the platform)
        for mb in self._mblocks:
            if mb.is_saw and check_saw_collision(pr, mb.rect):
                self._die(); return
        # Death: crushed by moving block
        for mb in self._mblocks:
            if mb.is_saw:
                continue
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

        # Background – white world, dark tiles
        surf.fill(TEAL)
        pygame.draw.rect(surf, WHITE, (ox, oy, OW, OH))

        # ── Draw tile grid ──
        tiles = self.data['tiles']
        for row in range(15):
            for col in range(27):
                if tiles[row*27+col]:
                    r = pygame.Rect(ox+col*TILE, oy+row*TILE, TILE, TILE)
                    pygame.draw.rect(surf, TEAL_DARK, r)

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

        # ── Death flash (red vignette) ──
        if self.flash > 0:
            a = int(200 * self.flash / 0.45)
            fl = pygame.Surface((SW, SH), pygame.SRCALPHA)
            fl.fill((*RED_FLASH, a))
            surf.blit(fl, (0, 0))

        # ── Win overlay ──
        if self.win:
            a = min(200, int(self.win_t * 400))
            _alpha_rect(surf, (8, 40, 36, a), pygame.Rect(0, 0, SW, SH))
            if self.win_t > 0.30:
                t  = min(1.0, (self.win_t - 0.30) / 0.45)
                ca = int(255 * t)
                card_w, card_h = 390, 210
                card_r = pygame.Rect((SW - card_w)//2, SH//2 - card_h//2 - 10,
                                     card_w, card_h)
                # Card shadow + body
                draw_shadow_card(surf, card_r, radius=20)
                pygame.draw.rect(surf, TEAL_DARK, card_r, border_radius=20)
                # Teal header band
                hdr = pygame.Rect(card_r.x, card_r.y, card_r.width, 60)
                _alpha_rect(surf, (*TEAL, min(255, ca)), hdr, radius=20)
                _alpha_rect(surf, (*TEAL, min(255, ca)),
                            pygame.Rect(card_r.x, card_r.y+38, card_r.width, 22))
                # Top shine
                _alpha_rect(surf, (255, 255, 255, 18),
                            pygame.Rect(card_r.x+4, card_r.y+4, card_r.width-8, 28), 16)
                pygame.draw.rect(surf, TEAL_LIGHT, card_r, 2, border_radius=20)
                # Text
                if ca > 80:
                    draw_text(surf, "LEVEL COMPLETE!", 32, WHITE,
                              SW//2, card_r.y + 32)
                    draw_text(surf, f"Deaths this run:  {self.run_deaths}", 22,
                              YELLOW, SW//2, card_r.y + 108)
                    # Progress flags
                    for li in range(3):
                        done = self.game.save['completed'].get(f"{self.ci}_{li}", False)
                        fx   = SW//2 - 24 + li*24
                        fy   = card_r.y + 152
                        col  = YELLOW if done else (72, 94, 90)
                        draw_flag_icon(surf, fx, fy, size=10, color=col,
                                       filled=done)
                    draw_text(surf, "Returning to level select...", 14,
                              (160, 210, 205), SW//2, card_r.y + 186, bold=False)

        # ── Top bar (always on top) ──
        pygame.draw.rect(surf, TEAL_DEEP, (0, 0, SW, TOP_H))
        pygame.draw.line(surf, TEAL_MID, (0, TOP_H), (SW, TOP_H), 1)

        _draw_exit_icon(surf, 26, TOP_H // 2)
        draw_text(surf, "Back", 13, (196, 232, 226), 64, TOP_H // 2, bold=False)

        # Centre pill: "CATEGORY · Lv.N"
        lv_text = f"{CAT_NAMES[self.ci]}  ·  Lv.{self.li + 1}"
        draw_pill_badge(surf, lv_text, 14, WHITE, TEAL_MID, SW//2 - 18, TOP_H // 2)

        # Level progress flags (right of centre pill)
        x_flags = SW//2 + 90
        for li in range(3):
            done = self.game.save['completed'].get(f"{self.ci}_{li}", False)
            cur  = (li == self.li)
            if done:
                col, filled = YELLOW, True
            elif cur:
                col, filled = WHITE, True
            else:
                col, filled = (64, 90, 86), False
            draw_flag_icon(surf, x_flags + li * 18, TOP_H // 2 + 5,
                           size=9, color=col, filled=filled)

        total_d = self.game.save.get('deaths', 0)
        draw_splotch_icon(surf, SW - 42, TOP_H // 2, 16, WHITE, total_d)
        _draw_sound_icons(surf, SW - 110, TOP_H // 2)

        # ── Hint toast (bottom pill) ──
        if self.hint_t > 0:
            hint = self.data.get('hint', '')
            if hint:
                alpha = min(255, int(255 * min(1.0, self.hint_t / 1.5)))
                f_hint = get_font(14, False)
                ts = f_hint.render(hint, True, WHITE)
                tw, th = ts.get_size()
                pill_r = pygame.Rect((SW - tw - 32)//2, SH - 42, tw + 32, th + 14)
                _alpha_rect(surf, (0, 0, 0, int(alpha * 0.55)), pill_r, pill_r.height//2)
                _alpha_rect(surf, (255, 255, 255, int(alpha * 0.10)), pill_r, pill_r.height//2)
                _alpha_rect(surf, (*TEAL_LIGHT, int(alpha * 0.45)),
                            pill_r.inflate(2, 2), pill_r.height//2 + 1)
                ts.set_alpha(alpha)
                surf.blit(ts, ts.get_rect(center=(SW//2, SH - 35)))


def _draw_exit_icon(surf, cx, cy):
    """Modern back button: filled circle with a left chevron."""
    pygame.draw.circle(surf, TEAL_MID, (cx, cy), 14)
    pygame.draw.circle(surf, WHITE, (cx, cy), 14, 1)
    s = 6
    pts = [(cx + s//2, cy - s), (cx - s//2, cy), (cx + s//2, cy + s)]
    pygame.draw.lines(surf, WHITE, False, pts, 2)

def _draw_sound_icons(surf, cx, cy):
    """Single minimal speaker icon (decorative)."""
    col = (120, 160, 156)
    body = pygame.Rect(cx - 5, cy - 5, 5, 9)
    pygame.draw.rect(surf, col, body, border_radius=1)
    pts = [(cx-5, cy-5), (cx+3, cy-9), (cx+3, cy+9), (cx-5, cy+4)]
    pygame.draw.polygon(surf, col, pts)
    pygame.draw.arc(surf, col, (cx+4, cy-5, 7, 10), -0.7, 0.7, 1)
    pygame.draw.arc(surf, col, (cx+4, cy-8, 12, 16), -0.7, 0.7, 1)

# ─────────────────────────────────────────────────────────────────────────────
# LEVEL  SELECT  SCENE
# ─────────────────────────────────────────────────────────────────────────────
class LevelSelectScene:
    def __init__(self, game, ci):
        self.game = game
        self.ci   = ci
        self.hover = -1

    def _btns(self):
        bw, bh = 220, 168
        gap    = 28
        total  = 3*bw + 2*gap
        x0     = (SW - total)//2
        y0     = SH//2 - bh//2 + 16
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
        draw_bg_dots(surf)
        cc = CAT_COLORS[self.ci]

        draw_text_shadow(surf, CAT_NAMES[self.ci], 46, WHITE, SW//2, TOP_H + 52)
        draw_text(surf, "Choose a Level", 16, TEAL_LIGHT, SW//2, TOP_H + 90, bold=False)

        unl = self.game.save['unlocked_lvls'].get(str(self.ci), [0])
        for i, r in enumerate(self._btns()):
            locked = i not in unl
            done   = self.game.save['completed'].get(f"{self.ci}_{i}", False)
            hov    = (self.hover == i and not locked)

            if locked:
                bg = (36, 48, 46)
            elif done:
                bg = (30, 118, 56)
            elif hov:
                bg = tuple(min(255, c + 28) for c in cc)
            else:
                bg = tuple(max(0, c - 14) for c in cc)

            border = (68, 88, 84) if locked else (WHITE if hov else (200, 220, 218))
            draw_modern_card(surf, r, bg, radius=16, hover=hov, border_color=border)

            # ── Large numbered badge circle ──
            badge_cx, badge_cy, badge_r = r.centerx, r.y + 58, 30
            _alpha_rect(surf, (0, 0, 0, 55),
                        pygame.Rect(badge_cx-badge_r, badge_cy-badge_r, badge_r*2, badge_r*2),
                        badge_r)
            pygame.draw.circle(surf,
                               (68, 88, 84) if locked else WHITE,
                               (badge_cx, badge_cy), badge_r, 2)
            fg_num = GREY if locked else (YELLOW if done else WHITE)
            draw_text(surf, str(i + 1), 36, fg_num, badge_cx, badge_cy)

            # ── Level label ──
            draw_text(surf, f"LEVEL {i+1}", 14,
                      GREY if locked else WHITE, r.centerx, r.y + 106)

            # ── Status pill / lock ──
            if locked:
                draw_lock(surf, r.centerx, r.y + 138, 24)
            elif done:
                draw_pill_badge(surf, "  DONE  ", 13, BLACK, GREEN_DONE,
                                r.centerx, r.y + 144)
            else:
                draw_pill_badge(surf, "  PLAY  ", 13, WHITE, ORANGE_DK,
                                r.centerx, r.y + 144)

        # ── Top bar ──
        pygame.draw.rect(surf, TEAL_DEEP, (0, 0, SW, TOP_H))
        pygame.draw.line(surf, TEAL_MID, (0, TOP_H), (SW, TOP_H), 1)
        _draw_exit_icon(surf, 26, TOP_H // 2)
        draw_text(surf, "Back", 13, (196, 232, 226), 64, TOP_H // 2, bold=False)
        draw_text_shadow(surf, CAT_NAMES[self.ci], 22, WHITE, SW//2, TOP_H // 2)
        draw_splotch_icon(surf, SW - 46, TOP_H // 2, 16, WHITE,
                          self.game.save.get('deaths', 0))
        _draw_sound_icons(surf, SW - 112, TOP_H // 2)

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
        draw_bg_dots(surf)
        deaths = self.game.save.get('deaths', 0)

        # ── Hero title ──
        draw_text_shadow(surf, "SPLOTCH", 68, WHITE, SW//2, TOP_H + 52)
        draw_text(surf, "How far can you go before you get splotched?",
                  14, TEAL_LIGHT, SW//2, TOP_H + 92, bold=False)

        tips = ["Fake floors", "Pop-up spikes", "Sneaky blocks",
                "Shifting platforms", "Hidden traps"]

        for i, r in enumerate(self._cards()):
            unl = i in self.game.save['unlocked_cats']
            cc  = CAT_COLORS[i]
            hov = (self.hover == i and unl)

            if not unl:
                bg = (36, 48, 46)
            elif hov:
                bg = tuple(min(255, c + 28) for c in cc)
            else:
                bg = tuple(max(0, c - 14) for c in cc)

            border = WHITE if unl else (62, 78, 76)
            draw_modern_card(surf, r, bg, radius=16, hover=hov, border_color=border)

            fg = WHITE if unl else GREY

            # ── Category name ──
            draw_text(surf, CAT_NAMES[i], 16, fg, r.centerx, r.y + 24)
            if unl:
                pygame.draw.line(surf, TEAL_MID,
                                 (r.x + 16, r.y + 40), (r.right - 16, r.y + 40), 1)

            # ── Centre icon or lock ──
            if not unl:
                draw_lock(surf, r.centerx, r.centery - 8, 40)
            else:
                all_done = all(
                    self.game.save['completed'].get(f"{i}_{li}", False)
                    for li in range(3))
                icon_col = YELLOW if all_done else WHITE
                draw_category_icon(surf, i, r.centerx, r.centery - 22, 54, icon_col)
                if all_done:
                    draw_pill_badge(surf, "COMPLETE", 11, BLACK, YELLOW,
                                    r.centerx, r.centery + 32)

            # ── Progress flags ──
            if unl:
                flag_sz   = 12
                spacing_d = 25
                # centre the group accounting for flag extending right
                x_start = r.centerx - spacing_d - flag_sz // 2
                flag_y  = r.bottom - 52
                for li in range(3):
                    done = self.game.save['completed'].get(f"{i}_{li}", False)
                    fx   = x_start + li * spacing_d
                    col  = YELLOW if done else (68, 90, 86)
                    draw_flag_icon(surf, fx, flag_y, size=flag_sz,
                                   color=col, filled=done)

            # ── Tip text ──
            draw_text(surf, tips[i], 11, fg, r.centerx, r.bottom - 24, bold=False)

        # ── Reset button ──
        rb  = self._reset_btn()
        bg_rb = (168, 58, 54) if self.reset_confirm else (38, 66, 62)
        rrect(surf, bg_rb, rb, 8)
        pygame.draw.rect(surf,
                         (200, 78, 74) if self.reset_confirm else (68, 94, 90),
                         rb, 1, border_radius=8)
        draw_text(surf, "Confirm Reset?" if self.reset_confirm else "Reset Save",
                  14, WHITE, rb.centerx, rb.centery)

        draw_text(surf, "Click a category  ·  Ctrl+R = reset save",
                  12, (120, 172, 166), SW//2, SH - 14, bold=False)

        # ── Top bar (rendered last, always on top) ──
        pygame.draw.rect(surf, TEAL_DEEP, (0, 0, SW, TOP_H))
        pygame.draw.line(surf, TEAL_MID, (0, TOP_H), (SW, TOP_H), 1)
        draw_text_shadow(surf, "SPLOTCH", 22, WHITE, SW//2, TOP_H // 2)
        draw_splotch_icon(surf, SW - 46, TOP_H // 2, 16, WHITE, deaths)
        _draw_sound_icons(surf, SW - 112, TOP_H // 2)

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
