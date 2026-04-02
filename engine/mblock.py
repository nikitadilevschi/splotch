"""
Moving blocks (platforms and saws).
"""

import math
import pygame

from core.constants import TILE, OW, OH
from engine.tl_runner import TLRunner
from ui.draw_helpers import draw_tiled_platform, draw_saw, draw_platform_colored, draw_saw_colored


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
        if auto:
            self.runner.activate()

    def reset(self):
        self.runner.reset()
        self.prev_x, self.prev_y = float(self.ox), float(self.oy)
        if self.auto:
            self.runner.activate()
        if self.sensor:
            self.sensor.reset()
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

    def draw(self, surf, ox, oy, palette=None):
        """Draw moving block - as a regular platform or saw blade."""
        if palette is None:
            # Fallback to default drawing
            if self.is_saw:
                draw_saw(surf, self.rect, ox, oy, self.saw_rotation)
            else:
                draw_tiled_platform(surf, self.rect, ox, oy)
        else:
            # Use category-specific colors
            if self.is_saw:
                draw_saw_colored(surf, self.rect, ox, oy, 
                               palette['light'], palette['dark'], palette['dark'],
                               self.saw_rotation)
            else:
                draw_platform_colored(surf, self.rect, ox, oy, palette['dark'])


