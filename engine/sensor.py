"""
Sensor collision detection zones.
"""

import pygame


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

