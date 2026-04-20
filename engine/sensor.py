"""
Sensor collision detection zones.
"""

import pygame


class Sensor:
    def __init__(self, x, y, w, h):
        """Create a one-shot rectangular trigger zone in world coordinates."""
        self.rect = pygame.Rect(x, y, w, h)
        self.fired = False

    def check(self, player_rect):
        """Return True once when player first overlaps the sensor rect."""
        if not self.fired and self.rect.colliderect(player_rect):
            self.fired = True
            return True
        return False

    def reset(self):
        """Re-arm this sensor so it can fire again."""
        self.fired = False

