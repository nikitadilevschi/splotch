import pygame
import sys

# Presentation note: this file boots pygame, owns the active scene, and runs the global game loop.

from core.constants import SW, SH, FPS
from core.save_manager import load_save, write_save, default_save
from scenes.category_select import CategorySelectScene


class Game:
    """Top-level game controller: window setup, scene routing, and main loop."""

    def __init__(self):
        """Initialize pygame, load save data, and open the category-select scene."""
        pygame.init()
        self.fullscreen = False
        self.screen = pygame.display.set_mode((SW, SH), pygame.RESIZABLE)
        pygame.display.set_caption("Rage Bait – Precision Platformer")
        self.clock  = pygame.time.Clock()
        self.save   = load_save()
        self.scene  = CategorySelectScene(self)
        self.game_surface = pygame.Surface((SW, SH))  # Internal render surface

    def toggle_fullscreen(self):
        """Toggle between windowed and fullscreen modes."""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            # Get the actual monitor resolution for true fullscreen
            info = pygame.display.Info()
            self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SW, SH), pygame.RESIZABLE)
        pygame.display.set_caption("Rage Bait – Precision Platformer")

    def go_category_select(self):
        """Switch to the category selection screen."""
        self.scene = CategorySelectScene(self)

    def go_level_select(self, ci):
        """Switch to the level-selection screen for a specific category index."""
        from scenes.level_select import LevelSelectScene
        self.scene = LevelSelectScene(self, ci)

    def go_level(self, ci, li):
        """Start gameplay for a specific category and level index."""
        from scenes.level_scene import LevelScene
        self.scene = LevelScene(self, ci, li)

    def reset_save(self):
        """Restore default save data and return to the category-select scene."""
        self.save  = default_save()
        write_save(self.save)
        self.scene = CategorySelectScene(self)

    def run(self):
        """Run the fixed-timestep game loop and delegate events/update/draw to the active scene."""
        while True:
            # Clamp dt so sudden frame drops do not cause large physics jumps.
            dt = min(self.clock.tick(FPS)/1000.0, 0.05)
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # Fullscreen toggle: F11 or Alt+Enter
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_F11 or (ev.key == pygame.K_RETURN and 
                                                   (pygame.key.get_mods() & pygame.KMOD_ALT)):
                        self.toggle_fullscreen()
                        continue
                
                # Scale mouse coordinates if window is larger than base resolution
                screen_w, screen_h = self.screen.get_size()
                if screen_w > SW or screen_h > SH:
                    scale_x = SW / screen_w
                    scale_y = SH / screen_h
                    
                    if ev.type == pygame.MOUSEMOTION:
                        ev.pos = (int(ev.pos[0] * scale_x), int(ev.pos[1] * scale_y))
                    elif ev.type == pygame.MOUSEBUTTONDOWN or ev.type == pygame.MOUSEBUTTONUP:
                        ev.pos = (int(ev.pos[0] * scale_x), int(ev.pos[1] * scale_y))
                
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    mx, my = ev.pos
                    # Top-left back hotspot used across scenes.
                    if my < 56 and mx < 100:
                        from scenes.level_scene import LevelScene
                        from scenes.level_select import LevelSelectScene
                        if isinstance(self.scene, LevelScene):
                            self.go_level_select(self.scene.ci)
                            continue
                        elif isinstance(self.scene, LevelSelectScene):
                            self.go_category_select()
                            continue
                self.scene.handle_event(ev)
            self.scene.update(dt)
            self.scene.draw(self.game_surface)
            
            # Scale and display the game surface to the screen (handles fullscreen scaling and window resizing)
            screen_w, screen_h = self.screen.get_size()
            # Scale if window is larger than base resolution
            if screen_w > SW or screen_h > SH:
                scaled = pygame.transform.scale(self.game_surface, (screen_w, screen_h))
                self.screen.blit(scaled, (0, 0))
            else:
                self.screen.blit(self.game_surface, (0, 0))
            
            pygame.display.flip()


if __name__ == "__main__":
    Game().run()

