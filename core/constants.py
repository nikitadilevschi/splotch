"""
Game constants and palette colours.
"""

# Window size and layout
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

# Category names and colors
CAT_NAMES  = ["Gaps", "Spikes", "Push", "Platforms", "Saws"]
CAT_COLORS = [
    ( 70, 180, 168),
    (185,  75,  75),
    ( 75, 130, 185),
    (125,  75, 185),
    (185, 145,  50),
]

# Category-specific color palettes for level design
# Each palette includes: primary_color, dark_variant, light_variant, accent_color, spike_color
CAT_PALETTES = [
    # Gaps - Teal/Cyan
    {
        'primary':    ( 70, 180, 168),
        'dark':       ( 45, 130, 120),
        'light':      (100, 210, 200),
        'accent':     (120, 230, 220),
        'spike':      (160, 160, 160),
    },
    # Spikes - Red
    {
        'primary':    (185,  75,  75),
        'dark':       (140,  50,  50),
        'light':      (220, 100, 100),
        'accent':     (240, 130, 130),
        'spike':      (200, 100, 100),
    },
    # Push - Blue
    {
        'primary':    ( 75, 130, 185),
        'dark':       ( 50,  95, 140),
        'light':      (110, 160, 210),
        'accent':     (140, 180, 230),
        'spike':      (160, 160, 160),
    },
    # Platforms - Purple
    {
        'primary':    (125,  75, 185),
        'dark':       ( 90,  50, 140),
        'light':      (160, 110, 220),
        'accent':     (190, 140, 240),
        'spike':      (160, 160, 160),
    },
    # Saws - Orange/Gold
    {
        'primary':    (185, 145,  50),
        'dark':       (140, 110,  30),
        'light':      (220, 175,  80),
        'accent':     (240, 200, 110),
        'spike':      (160, 160, 160),
    },
]
