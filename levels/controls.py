"""
Controls category levels - Tutorial-style levels teaching game mechanics.
"""

import pygame

CONTROLS_L1 = {
    'tiles': [
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
        1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
        1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
        1,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,1,
        1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
        1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
        1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
        1,1,1,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,
        1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
        1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
        1,1,1,0,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,
        1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
        1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
    ],
    'player': [192, 128],
    'goal':   [416, 386],
    'traps': [],
    'reversed_tiles': [
        # Top platform - reversed controls zone (full width)
        pygame.Rect(6*32, 5*32, 384, 96),
        # Middle platform - reversed controls zone (full width)
        pygame.Rect(9*32, 9*32, 384, 96),
    ],
    'hint': "Use LEFT/RIGHT arrows to move on platforms with spikes. Reach the flag!",
}

CONTROLS_L2 = {
    'tiles': [
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
        1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
        1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
        1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
        1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
        1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
        1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
        1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
        1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
        1,1,1,1,1,0,0,0,1,1,1,0,0,1,1,1,0,0,1,1,1,0,0,1,1,1,1,
        1,1,1,1,1,0,0,0,1,1,1,0,0,1,1,1,0,0,1,1,1,0,0,1,1,1,1,
        1,1,1,1,1,0,0,0,1,1,1,0,0,1,1,1,0,0,1,1,1,0,0,1,1,1,1,
        1,1,1,1,1,0,0,0,1,1,1,0,0,1,1,1,0,0,1,1,1,0,0,1,1,1,1,
    ],
    'player': [140, 350],
    'goal':   [780, 352],
    'traps': [],
    'reversed_tiles': [
        # Top area - reversed controls zone (full width)
        pygame.Rect(3*32, 2*32, 672, 96),
        # Bottom platforms - aligned with actual solid tiles
        pygame.Rect(8*32, 11*32, 96, 96),   # Left platform
        pygame.Rect(18*32, 11*32, 96, 96),  # Middle-right platform
        pygame.Rect(23*32, 11*32, 32, 96),  # Right platform
    ],
    'hint': "Navigate between reversed control platforms!",
}

CONTROLS_L3 = {
    'tiles': [
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,1,1,1,1,1,
        1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,1,1,1,1,1,
        1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,
        1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,
        1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,1,1,1,1,1,
        1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
    ],
    'player': [370, 160],
    'goal':   [540, 160],
    'traps': [
        # Right edge of left upper platform - spikes pointing right into the gap
        dict(kind='spike', x=12*32, y=3*32, w=32, h=14, steps=[], sensor=None, dir='left'),
        dict(kind='spike', x=12 * 32, y=4 * 32, w=32, h=14, steps=[], sensor=None, dir='left'),
        dict(kind='spike', x=12 * 32, y=5 * 32, w=32, h=14, steps=[], sensor=None, dir='left'),

        # Left edge of right upper platform - spikes pointing left into the gap
        dict(kind='spike', x=15*32, y=3*32, w=32, h=14, steps=[], sensor=None, dir='right'),
        dict(kind='spike', x=15 * 32, y=4 * 32, w=32, h=14, steps=[], sensor=None, dir='right'),
        dict(kind='spike', x=15 * 32, y=5 * 32, w=32, h=14, steps=[], sensor=None, dir='right'),

        # Bottom of central horizontal platform (row 5) - spikes pointing down
        dict(kind='spike', x=8*32, y=6*32, w=32, h=14, steps=[], sensor=None, dir='left'),

        # Left side of central channel (rows 8-9) - spikes pointing right
        dict(kind='spike', x=12*32, y=7*32, w=32, h=14, steps=[], sensor=None, dir='left'),
        dict(kind='spike', x=12 * 32, y=8 * 32, w=32, h=14, steps=[], sensor=None, dir='left'),
        dict(kind='spike', x=12 * 32, y=9 * 32, w=32, h=14, steps=[], sensor=None, dir='left'),

        dict(kind='spike', x=15 * 32, y=7 * 32, w=32, h=14, steps=[], sensor=None, dir='right'),
        dict(kind='spike', x=15 * 32, y=8 * 32, w=32, h=14, steps=[], sensor=None, dir='right'),
        dict(kind='spike', x=15 * 32, y=9 * 32, w=32, h=14, steps=[], sensor=None, dir='right'),

        # Right side of central channel (rows 8-9) - spikes pointing left
        dict(kind='spike', x=19*32, y=6*32, w=32, h=14, steps=[], sensor=None, dir='right'),
    ],
    'reversed_tiles': [
        # Top horizontal platform - reversed controls (columns 6-19, row 5)
        pygame.Rect(6*32, 5*32, 14*32, 32),
        # Vertical channel platforms - reversed controls zones (rows 7-9)
        pygame.Rect(10*32, 7*32, 32, 64),   # Left channel platform
        pygame.Rect(17*32, 7*32, 32, 64),   # Right channel platform
        # Bottom platform - reversed controls (columns 3-24, rows 9-11)
        pygame.Rect(3*32, 9*32, 24*32, 96),
    ],
    'jump_boost_tiles': [
        # Bottom platform area (full width, rows 9-11) - covers all the bottom platform
        {
            'rect': pygame.Rect(3*32, 12*32, 24*32, 96),
            'jump_v': -1200,  # Significantly higher jump boost (default is -500)
        },
        # Right channel platform (row 7) - jump boost
        {
            'rect': pygame.Rect(3*32, 9*32, 24*32, 96),
            'jump_v': -1200,  # Same boost as bottom platform
        },
    ],
}

