"""
Teleporter mechanism - transports player to a specific location.
Displays as an animated rolling spiral with optional movement.
"""

import pygame

from core.constants import TILE, OW, OH
from engine.tl_runner import TLRunner


class Teleporter:
    """
    A teleportation portal that moves the player to a destination when touched.
    Renders as an animated spiral that rolls continuously.
    Can optionally move along a path like a moving block.
    """
    def __init__(
        self,
        x,
        y,
        dest_x,
        dest_y,
        w=40,
        h=40,
        steps=None,
        sensor=None,
        loop=True,
        destinations=None,
        destination_mode='static',
        teleport_cooldown=0.5,
        self_top_offset_tiles=0,
    ):
        """
        Create a teleporter.
        
        Args:
            x, y: Position of the teleporter (world coords, center)
            dest_x, dest_y: Destination coordinates where player will be teleported
            w, h: Width and height of the teleporter visual
            steps: List of movement steps [[x1, y1, duration], [x2, y2, duration], ...]
            sensor: Optional Sensor object to trigger teleporter movement
            loop: Whether movement should loop (default True)
            destinations: Optional list of destination pairs [(x1, y1), (x2, y2), ...]
            destination_mode: 'static' (default) or 'self_top' (teleport to top of current portal)
            teleport_cooldown: Seconds to wait before next teleport (default 0.5)
            self_top_offset_tiles: Extra tiles above portal top when using self_top mode
        """
        self.ox, self.oy = float(x), float(y)
        if destinations:
            self.destinations = [(float(dx), float(dy)) for dx, dy in destinations]
        else:
            self.destinations = [(float(dest_x), float(dest_y))]
        self._dest_index = 0
        self.dest_x, self.dest_y = self.destinations[0]
        self.destination_mode = destination_mode
        self.teleport_cooldown = max(0.0, float(teleport_cooldown))
        self.self_top_offset_tiles = float(self_top_offset_tiles)
        self.w = w
        self.h = h
        self.rotation = 0.0  # For animation
        self.active = True
        self.cooldown = 0.0  # Prevent multiple teleports in succession
        
        # Movement support
        steps = steps or []
        self.runner = TLRunner(x, y, steps, loop=loop)
        self.runner.active = False  # Don't activate until sensor triggers (if present)
        self.sensor = sensor
        # If no sensor, activate immediately for backwards compatibility
        if not sensor and steps:
            self.runner.active = True
        
    @property
    def x(self):
        """Current teleporter center x from the timeline runner."""
        return self.runner.x
    
    @property
    def y(self):
        """Current teleporter center y from the timeline runner."""
        return self.runner.y
    
    @property
    def rect(self):
        """Current teleporter collision rect centered at x/y."""
        return pygame.Rect(self.x - self.w//2, self.y - self.h//2, self.w, self.h)
        
    def update(self, dt, prect=None):
        """Update animation and movement."""
        self.rotation += dt * 360.0  # Rotate 360 degrees per second
        self.rotation %= 360.0
        
        # Check if sensor triggered - activate movement
        if prect and self.sensor and not self.runner.active:
            if self.sensor.check(prect):
                self.runner.active = True
        
        # Update movement
        self.runner.update(dt)
        
        # Update cooldown
        if self.cooldown > 0:
            self.cooldown -= dt
    
    def check_collision(self, player_rect):
        """
        Check if player collides with teleporter.
        Returns True if collision and teleporter is ready to activate.
        """
        if self.cooldown > 0:
            return False
        return self.rect.colliderect(player_rect)
    
    def teleport(self, player):
        """
        Teleport the player to the destination.
        """
        if self.destination_mode == 'self_top':
            # Place player's feet on the top edge of the moving teleporter.
            target_x = self.x
            extra_offset = self.self_top_offset_tiles * TILE
            target_y = self.y - (self.h / 2) - extra_offset
            self.dest_x, self.dest_y = target_x, target_y
        else:
            target_x, target_y = self.destinations[self._dest_index]
            self._dest_index = (self._dest_index + 1) % len(self.destinations)

        # Keep teleport target inside playable bounds.
        pw = float(getattr(player, 'W', 26))
        ph = float(getattr(player, 'H', 26))
        target_x = max(pw / 2.0, min(float(target_x), OW - (pw / 2.0)))
        target_y = max(ph, min(float(target_y), OH))
        self.dest_x, self.dest_y = target_x, target_y

        player.x = target_x
        player.y = target_y
        player.rect.center = (target_x, target_y)
        self.cooldown = self.teleport_cooldown
    
    def reset(self):
        """Reset the teleporter state."""
        self.rotation = 0.0
        self.cooldown = 0.0
        self._dest_index = 0
        self.dest_x, self.dest_y = self.destinations[0]
        self.runner.reset()
        if self.sensor:
            self.sensor.reset()

