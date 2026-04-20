"""
Level gameplay scene.

Presentation notes:
- This is the core runtime scene: input, physics, hazards, win/death, and HUD all meet here.
- Build/update/draw are intentionally separated to keep gameplay deterministic and explainable.
"""

import pygame

from core.constants import (
    SW, SH, OX, OY, OW, OH, TOP_H, TILE, WHITE, TEAL_MID, YELLOW,
    RED_FLASH, CAT_NAMES
)
from core.save_manager import write_save
from core.sound_manager import get_sound_manager
from engine.physics import Player
from engine.mblock import MBlock, check_saw_collision
from engine.spike import SpikeObj
from engine.teleporter import Teleporter
from engine.sensor import Sensor
from levels.builder import tiles_to_rects, _build_trap
from levels import LEVELS
from ui.draw_helpers import (
    draw_text, draw_pill_badge, get_font, draw_flag,
    draw_flag_icon, _alpha_rect, draw_shadow_card, draw_deaths_counter,
    get_category_palette, draw_tile_colored, draw_mute_button, draw_teleporter
)


class LevelScene:
    def __init__(self, game, ci, li):
        """Initialize one gameplay level scene from category/level indices."""
        self.game   = game
        self.ci, self.li = ci, li
        self.data   = LEVELS[ci][li]
        self.sound_mgr = get_sound_manager()
        self.sound_mgr.play_background_music()
        self._build()
        self.flash  = 0.0
        self.hint_t = 5.0
        self.win    = False
        self.win_t  = 0.0
        self.run_deaths = 0
        
        # Reversed tiles list (for Controls category)
        self.reversed_tiles = self.data.get('reversed_tiles', [])
        
        # Track current platform for persistent control reversal
        self.current_reversed_tile = None

        # Jump boost tiles list
        self.jump_boost_tiles = self.data.get('jump_boost_tiles', [])
        self.current_jump_boost = None

    def _build(self):
        """Build player, goal, traps, and optional goal-trigger sensor from level data."""
        d = self.data
        self._static_plats = tiles_to_rects(d['tiles'])
        px, py = d['player']
        self.player = Player(px, py)
        gx, gy = d['goal']
        self._initial_goal = (gx, gy)
        self._set_goal(gx, gy)

        self._goal_sensor = None
        self._goal_trigger_target = None
        self._goal_trigger_fired = False
        goal_trigger = d.get('goal_trigger')
        if goal_trigger:
            sx, sy, sw, sh = goal_trigger['sensor']
            self._goal_sensor = Sensor(sx, sy, sw, sh)
            tx, ty = goal_trigger.get('target', d['player'])
            self._goal_trigger_target = (tx, ty)

        self._mblocks = []
        self._spikes  = []
        self._teleporters = []
        for td in d.get('traps', []):
            obj = _build_trap(td)
            if obj is None:
                continue
            if isinstance(obj, MBlock):
                self._mblocks.append(obj)
            if isinstance(obj, SpikeObj):
                self._spikes.append(obj)
            if isinstance(obj, Teleporter):
                self._teleporters.append(obj)

        self._rebuild_plats()

    def _set_goal(self, gx, gy):
        """Set goal world position and rebuild its collision rect."""
        self.gx, self.gy = gx, gy
        self.goal_rect = pygame.Rect(gx-8, gy-48, 22, 48)

    def _rebuild_plats(self):
        """Recompute active solid platforms (static tiles + in-bounds moving blocks)."""
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

    def _is_on_reversed_tile(self, player_rect):
        """Check if player is standing on a reversed control tile. Returns the tile or None."""
        for rev_tile in self.reversed_tiles:
            # Check if player is standing on top of this reversed tile
            if (player_rect.bottom >= rev_tile.top - 4 and
                player_rect.bottom <= rev_tile.top + 4 and
                player_rect.right > rev_tile.left and
                player_rect.left < rev_tile.right):
                return rev_tile
        return None

    def _get_jump_boost(self, player_rect):
        """Check if player is standing on a jump boost tile. Returns the boost velocity or None."""
        for boost_tile in self.jump_boost_tiles:
            boost_rect = boost_tile['rect']
            # Check if player is standing on top of this boost tile
            if (player_rect.bottom >= boost_rect.top - 4 and
                player_rect.bottom <= boost_rect.top + 4 and
                player_rect.right > boost_rect.left and
                player_rect.left < boost_rect.right):
                return boost_tile.get('jump_v', None)
        return None

    def _carry_player_with_moving_blocks(self, player, prect):
        """Move player by block delta when standing on top of a moving platform."""
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
        """Handle death: play effects, increment stats, and reset entities to spawn state."""
        self.sound_mgr.play_sound('death', volume=0.7)
        self.game.save['deaths'] = self.game.save.get('deaths', 0) + 1
        
        # Track per-level deaths using category and level indices
        level_key = f"{self.ci}_{self.li}"
        self.game.save['level_deaths'][level_key] = self.game.save['level_deaths'].get(level_key, 0) + 1
        
        write_save(self.game.save)
        self.run_deaths += 1
        self.flash = 0.45
        self.win   = False
        self.win_t = 0.0
        px, py = self.data['player']
        self.player.reset_pos()
        self.player._sx, self.player._sy = float(px), float(py)
        self.player.x, self.player.y     = float(px), float(py)
        for mb in self._mblocks:
            mb.reset()
        for sp in self._spikes:
            sp.reset()
        for tel in self._teleporters:
            tel.reset()
        self._set_goal(*self._initial_goal)
        if self._goal_sensor is not None:
            self._goal_sensor.reset()
        self._goal_trigger_fired = False
        self._rebuild_plats()

    def handle_event(self, ev):
        """Handle level-local input: restart, back navigation, and mute toggling."""
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_r:
                self._die()
            if ev.key == pygame.K_ESCAPE:
                self.game.go_level_select(self.ci)
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            mx, my = ev.pos
            # Check mute button
            if self.mute_btn_rect and self.mute_btn_rect.collidepoint(mx, my):
                self.sound_mgr.toggle_mute()
                self.game.save['muted'] = self.sound_mgr.muted
                write_save(self.game.save)

    def update(self, dt):
        """Advance one gameplay frame: input, hazards, physics, death/win checks."""
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
        
        # Check if player is standing on a reversed control tile
        tile_under_player = self._is_on_reversed_tile(pr)
        
        if tile_under_player:
            # Player is standing on a reversed tile - set it as current
            self.current_reversed_tile = tile_under_player
        elif self.current_reversed_tile is None:
            # Player is not on any reversed tile and wasn't on one before
            pass
        # else: Player is in the air (jumping) but was on a reversed tile - keep reversing
        
        # Apply reversed controls if player is on a reversed tile (or jumping from one)
        if self.current_reversed_tile is not None:
            p.vx = -p.vx
        
        # Clear current reversed tile if player landed on a different platform
        if tile_under_player is None and p.vy >= 0:
            # Player is falling/idle and not on any reversed tile
            # Check if they're actually on a regular platform
            pr_below = pygame.Rect(pr.x, pr.y + 4, pr.w, pr.h)
            if any(pr_below.colliderect(plat) for plat in self._platforms):
                # Player landed on a non-reversed platform
                self.current_reversed_tile = None
        
        for mb in self._mblocks:
            mb.update(dt, pr)
        for sp in self._spikes:
            sp.update(dt, pr)
        for tel in self._teleporters:
            tel.update(dt, pr)
        self._rebuild_plats()
        self._carry_player_with_moving_blocks(p, pr)
        
        # Check if player is on a jump boost tile
        jump_boost_value = self._get_jump_boost(pr)
        level_max_fall = self.data.get('max_fall', None)
        p.update(dt, self._platforms, custom_jump_v=jump_boost_value, max_fall=level_max_fall)

        pr = p.rect
        
        # Detect jump using the player's jumped flag (set in physics.py)
        if p.jumped:
            self.sound_mgr.play_sound('jump', volume=0.6)

        # Death: fall off screen
        if p.y > OH + 80:
            self._die()
            return
        # Death: spike
        for sp in self._spikes:
            if pr.colliderect(sp.kill_rect()):
                self._die()
                return
        # Teleporter activation
        for tel in self._teleporters:
            if tel.check_collision(pr):
                tel.teleport(p)
                pr = p.rect  # Update rect after teleportation
        # Death: saw hazard (only when touching the actual saw blade, not the platform)
        for mb in self._mblocks:
            if mb.is_saw and check_saw_collision(pr, mb.rect):
                self._die()
                return

        # Optional level-specific sensor that can relocate the goal once.
        if self._goal_sensor and (not self._goal_trigger_fired) and self._goal_sensor.check(pr):
            self._set_goal(*self._goal_trigger_target)
            self._goal_trigger_fired = True

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
                        self._die()
                        return

        # Win
        if pr.colliderect(self.goal_rect):
            self.sound_mgr.play_sound('win', volume=0.8)
            self.win = True
            key = f"{self.ci}_{self.li}"
            self.game.save['completed'][key] = True
            ul = self.game.save['unlocked_lvls']
            ck = str(self.ci)
            if ck not in ul:
                ul[ck] = [0]
            if self.li + 1 < 3 and (self.li+1) not in ul[ck]:
                ul[ck].append(self.li+1)
            if all(self.game.save['completed'].get(f"{self.ci}_{x}", False)
                   for x in range(3)):
                if self.ci+1 < 7:  # Updated to support 7 categories
                    if (self.ci+1) not in self.game.save['unlocked_cats']:
                        self.game.save['unlocked_cats'].append(self.ci+1)
                    nk = str(self.ci+1)
                    if nk not in ul:
                        ul[nk] = [0]
            write_save(self.game.save)

    def draw(self, surf):
        """Render world, entities, HUD, and overlays using the category palette."""
        ox, oy = OX, OY

        # Draw order matters: world first, then entities, then feedback overlays, then HUD/top-bar.
        # Get category-specific palette
        palette = get_category_palette(self.ci)
        tile_color = palette['dark']
        bg_color = (255, 255, 255)  # Keep white background

        # Background – white world, dark tiles
        surf.fill(palette['primary'])
        pygame.draw.rect(surf, bg_color, (ox, oy, OW, OH))

        # ── Draw tile grid with category color ──
        tiles = self.data['tiles']
        for row in range(15):
            for col in range(27):
                if tiles[row*27+col]:
                    r = pygame.Rect(ox+col*TILE, oy+row*TILE, TILE, TILE)
                    draw_tile_colored(surf, r, tile_color)

        # ── Moving blocks – look IDENTICAL to normal tiles ──
        for mb in self._mblocks:
            mb.draw(surf, ox, oy, palette)

        # ── Spikes ──
        for sp in self._spikes:
            sp.draw(surf, ox, oy, palette)

        # ── Teleporters ──
        for tel in self._teleporters:
            draw_teleporter(surf, tel.x + ox, tel.y + oy, radius=tel.w//2, 
                          rotation=tel.rotation, color_light=palette['light'], 
                          color_dark=palette['primary'])

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
                pygame.draw.rect(surf, palette['dark'], card_r, border_radius=20)
                # Category-themed header band
                hdr = pygame.Rect(card_r.x, card_r.y, card_r.width, 60)
                _alpha_rect(surf, (*palette['primary'], min(255, ca)), hdr, radius=20)
                _alpha_rect(surf, (*palette['primary'], min(255, ca)),
                            pygame.Rect(card_r.x, card_r.y+38, card_r.width, 22))
                # Top shine
                _alpha_rect(surf, (255, 255, 255, 18),
                            pygame.Rect(card_r.x+4, card_r.y+4, card_r.width-8, 28), 16)
                pygame.draw.rect(surf, palette['light'], card_r, 2, border_radius=20)
                # Text
                if ca > 80:
                    draw_text(surf, "LEVEL COMPLETE!", 32, WHITE,
                              SW//2, card_r.y + 32)
                    draw_text(surf, f"Deaths this run:  {self.run_deaths}", 22,
                              palette['accent'], SW//2, card_r.y + 108)
                    # Progress flags
                    for li in range(3):
                        done = self.game.save['completed'].get(f"{self.ci}_{li}", False)
                        fx   = SW//2 - 24 + li*24
                        fy   = card_r.y + 152
                        col  = palette['accent'] if done else (72, 94, 90)
                        draw_flag_icon(surf, fx, fy, size=10, color=col,
                                       filled=done)
                    draw_text(surf, "Returning to level select...", 14,
                              palette['light'], SW//2, card_r.y + 186, bold=False)

        # ── Top bar (always on top) ──
        pygame.draw.rect(surf, palette['dark'], (0, 0, SW, TOP_H))
        pygame.draw.line(surf, palette['accent'], (0, TOP_H), (SW, TOP_H), 1)

        _draw_exit_icon(surf, 26, TOP_H // 2, palette)
        draw_text(surf, "Back", 13, palette['accent'], 64, TOP_H // 2, bold=False)

        # Centre pill: "CATEGORY · Lv.N"
        lv_text = f"{CAT_NAMES[self.ci]}  ·  Lv.{self.li + 1}"
        draw_pill_badge(surf, lv_text, 14, WHITE, palette['accent'], SW//2 - 18, TOP_H // 2)

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
                           size=10, color=col, filled=filled)
        
        # Mute button (top-right)
        self.mute_btn_rect = draw_mute_button(surf, self.sound_mgr.muted)

        # Display per-level death counter for current level
        level_key = f"{self.ci}_{self.li}"
        level_deaths = self.game.save['level_deaths'].get(level_key, 0)
        draw_deaths_counter(surf, SW - 42, TOP_H // 2, level_deaths)

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
                _alpha_rect(surf, (*palette['light'], int(alpha * 0.45)),
                            pill_r.inflate(2, 2), pill_r.height//2 + 1)
                ts.set_alpha(alpha)
                surf.blit(ts, ts.get_rect(center=(SW//2, SH - 35)))


def _draw_exit_icon(surf, cx, cy, palette=None):
    """Modern back button: filled circle with a left chevron."""
    if palette is None:
        # Fallback colors if no palette provided
        primary_color = TEAL_MID
        accent_color = WHITE
    else:
        primary_color = palette['accent']
        accent_color = WHITE
    pygame.draw.circle(surf, primary_color, (cx, cy), 14)
    pygame.draw.circle(surf, accent_color, (cx, cy), 14, 1)
    s = 6
    pts = [(cx + s//2, cy - s), (cx - s//2, cy), (cx + s//2, cy + s)]
    pygame.draw.lines(surf, accent_color, False, pts, 2)

