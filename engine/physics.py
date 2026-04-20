"""
Player character physics and controls.
"""

import pygame

from core.constants import GRAVITY, MAX_FALL, JUMP_V, SPEED, COYOTE, JBUF
from ui.draw_helpers import draw_player


class Player:
    W, H = 26, 26

    def __init__(self, sx, sy):
        """Create a player with a fixed spawn position in world coordinates."""
        self._sx, self._sy = float(sx), float(sy)
        self.reset_pos()

    def reset_pos(self):
        """Reset position, velocities, and jump-assist state after spawn/death."""
        self.x, self.y = self._sx, self._sy
        self.vx = self.vy = 0.0
        self.on_ground = False
        self.coyote    = 0.0
        self.jbuf      = 0.0
        self.alive     = True
        self.jumped    = False  # Flag to track if player just jumped

    def handle_input(self, keys):
        """Read keyboard state and convert it into horizontal speed/jump buffering."""
        left  = keys[pygame.K_LEFT]  or keys[pygame.K_a]
        right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        jump  = keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]
        self.vx = SPEED * (right - left)
        if jump:
            self.jbuf = JBUF

    def update(self, dt, platforms, custom_jump_v=None, max_fall=None):
        """Integrate physics and resolve collisions against static/moving platforms."""
        self.jumped = False  # Reset jump flag at start of frame
        # Use provided max_fall or fall back to global constant
        fall_limit = max_fall if max_fall is not None else MAX_FALL
        self.vy = min(self.vy + GRAVITY*dt, fall_limit)
        self.coyote = max(0, self.coyote - dt)
        self.jbuf   = max(0, self.jbuf   - dt)

        if self.jbuf > 0 and (self.on_ground or self.coyote > 0):
            # Use custom jump velocity if provided (for boost tiles), otherwise use default
            jump_velocity = custom_jump_v if custom_jump_v is not None else JUMP_V
            self.vy = jump_velocity
            self.jumped = True  # Set flag when jump happens
            self.coyote = self.jbuf = 0

        # Resolve X then Y for stable axis-aligned collisions.
        self.on_ground = False
        self.x += self.vx * dt
        self._cx(platforms)
        self.y += self.vy * dt
        self._cy(platforms)

    def _cx(self, plats):
        """Resolve horizontal penetration and stop horizontal velocity on impact."""
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
                self.vx = 0
                r = self.rect

    def _cy(self, plats):
        """Resolve vertical penetration and update grounded/coyote state."""
        r = self.rect
        for p in plats:
            if r.colliderect(p):
                if self.vy >= 0:
                    self.y = p.top
                    self.on_ground = True
                    self.coyote = COYOTE
                else:
                    self.y = p.bottom + self.H
                self.vy = 0
                r = self.rect

    @property
    def rect(self):
        """Return current player hitbox rect derived from physics position."""
        return pygame.Rect(int(self.x - self.W//2), int(self.y - self.H),
                           self.W, self.H)

    def draw(self, surf, ox, oy):
        """Render player in screen coordinates using world offsets."""
        draw_player(surf, int(self.x)+ox, int(self.y)+oy, self.W, self.H)

