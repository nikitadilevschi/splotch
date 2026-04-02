"""
Level gameplay scene.
"""

import pygame

from core.constants import (
    SW, SH, OX, OY, OW, OH, TOP_H, TILE, WHITE, TEAL_MID, YELLOW,
    RED_FLASH, CAT_NAMES
)
from core.save_manager import write_save
from engine.physics import Player
from engine.mblock import MBlock, check_saw_collision
from engine.spike import SpikeObj
from levels.builder import tiles_to_rects, _build_trap
from levels import LEVELS
from ui.draw_helpers import (
    draw_text, draw_pill_badge, get_font, draw_flag,
    draw_flag_icon, _alpha_rect, draw_shadow_card, draw_deaths_counter,
    get_category_palette, draw_tile_colored
)


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
            if obj is None:
                continue
            if isinstance(obj, MBlock):
                self._mblocks.append(obj)
            if isinstance(obj, SpikeObj):
                self._spikes.append(obj)

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
        for mb in self._mblocks:
            mb.reset()
        for sp in self._spikes:
            sp.reset()
        self._rebuild_plats()

    def handle_event(self, ev):
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_r:
                self._die()
            if ev.key == pygame.K_ESCAPE:
                self.game.go_level_select(self.ci)

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
        for mb in self._mblocks:
            mb.update(dt, pr)
        for sp in self._spikes:
            sp.update(dt, pr)
        self._rebuild_plats()
        self._carry_player_with_moving_blocks(p, pr)
        p.update(dt, self._platforms)

        pr = p.rect

        # Death: fall off screen
        if p.y > OH + 80:
            self._die()
            return
        # Death: spike
        for sp in self._spikes:
            if pr.colliderect(sp.kill_rect()):
                self._die()
                return
        # Death: saw hazard (only when touching the actual saw blade, not the platform)
        for mb in self._mblocks:
            if mb.is_saw and check_saw_collision(pr, mb.rect):
                self._die()
                return
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
                if self.ci+1 < 5:
                    if (self.ci+1) not in self.game.save['unlocked_cats']:
                        self.game.save['unlocked_cats'].append(self.ci+1)
                    nk = str(self.ci+1)
                    if nk not in ul:
                        ul[nk] = [0]
            write_save(self.game.save)

    def draw(self, surf):
        ox, oy = OX, OY

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
                           size=9, color=col, filled=filled)

        total_d = self.game.save.get('deaths', 0)
        draw_deaths_counter(surf, SW - 42, TOP_H // 2, total_d)

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

