"""
Level selection scene.

Presentation notes:
- This scene is the transition between menu navigation and gameplay.
- It visualizes unlock state, completion state, and per-category theming.
"""

import pygame

from core.constants import (
    SW, SH, TOP_H, TEAL_DEEP, TEAL_MID, WHITE, GREY, TEAL_LIGHT, YELLOW,
    ORANGE_DK, GREEN_DONE, GREEN_DK, BLACK, CAT_NAMES, CAT_COLORS
)
from ui.draw_helpers import (
    draw_text_shadow, draw_text, draw_modern_card, draw_lock,
    draw_pill_badge, draw_bg_dots, _alpha_rect,
    get_font, draw_flag_icon, get_category_palette
)


class LevelSelectScene:
    def __init__(self, game, ci):
        """Initialize level-select state for one category index."""
        self.game = game
        self.ci   = ci
        self.hover = -1

    def _btns(self):
        """Return the three level-card button rects centered on screen."""
        bw, bh = 220, 168
        gap    = 28
        total  = 3*bw + 2*gap
        x0     = (SW - total)//2
        y0     = SH//2 - bh//2 + 16
        return [pygame.Rect(x0+i*(bw+gap), y0, bw, bh) for i in range(3)]

    def handle_event(self, ev):
        """Handle level card hover/click and back navigation."""
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            self.game.go_category_select()
        if ev.type == pygame.MOUSEMOTION:
            self.hover = -1
            for i,r in enumerate(self._btns()):
                if r.collidepoint(ev.pos):
                    self.hover = i
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            unl = self.game.save['unlocked_lvls'].get(str(self.ci), [0])
            for i,r in enumerate(self._btns()):
                if r.collidepoint(ev.pos) and i in unl:
                    self.game.go_level(self.ci, i)

    def update(self, dt):
        """No animated simulation in this scene; kept for scene interface parity."""
        pass

    def draw(self, surf):
        """Render themed level cards with locked/done/play states."""
        # Get category palette for theming
        palette = get_category_palette(self.ci)
        cc = palette['primary']
        primary_color = palette['primary']
        dark_color = palette['dark']
        accent_color = palette['accent']
        light_color = palette['light']
        
        # Apply category background colors (darker shade for dots, primary for background)
        dark_bg = tuple(max(0, c - 40) for c in primary_color)
        draw_bg_dots(surf, dark_bg, dark_color)
        
        draw_text_shadow(surf, CAT_NAMES[self.ci], 46, WHITE, SW//2, TOP_H + 52)
        draw_text(surf, "Choose a Level", 16, light_color, SW//2, TOP_H + 90, bold=False)

        unl = self.game.save['unlocked_lvls'].get(str(self.ci), [0])
        for i, r in enumerate(self._btns()):
            locked = i not in unl
            done   = self.game.save['completed'].get(f"{self.ci}_{i}", False)
            hov    = (self.hover == i and not locked)

            # Color cards based on state using category colors
            if locked:
                bg = (36, 48, 46)  # Stay dark grey for locked
            elif done:
                # Use category primary color (darker) for completed levels
                bg = dark_color
            elif hov:
                # Lighter variant when hovering
                bg = tuple(min(255, c + 28) for c in cc)
            else:
                # Default: category primary color
                bg = tuple(max(0, c - 14) for c in cc)

            border = (68, 88, 84) if locked else (WHITE if hov else light_color)
            draw_modern_card(surf, r, bg, radius=16, hover=hov, border_color=border)

            # ── Large numbered badge circle ──
            badge_cx, badge_cy, badge_r = r.centerx, r.y + 58, 30
            _alpha_rect(surf, (0, 0, 0, 55),
                        pygame.Rect(badge_cx-badge_r, badge_cy-badge_r, badge_r*2, badge_r*2),
                        badge_r)
            pygame.draw.circle(surf,
                               (68, 88, 84) if locked else WHITE,
                               (badge_cx, badge_cy), badge_r, 2)
            # Use category light color for done badge, white for available
            fg_num = GREY if locked else (light_color if done else WHITE)
            draw_text(surf, str(i + 1), 36, fg_num, badge_cx, badge_cy)

            # ── Level label ──
            draw_text(surf, f"LEVEL {i+1}", 14,
                      GREY if locked else WHITE, r.centerx, r.y + 106)

            # ── Status pill / lock ──
            if locked:
                draw_lock(surf, r.centerx, r.y + 138, 24)
            elif done:
                draw_pill_badge(surf, "  DONE  ", 13, BLACK, GREEN_DONE,
                                r.centerx, r.y + 144)
            else:
                draw_pill_badge(surf, "  PLAY  ", 13, WHITE, accent_color,
                                r.centerx, r.y + 144)

        # ── Top bar with category colors ──
        pygame.draw.rect(surf, dark_color, (0, 0, SW, TOP_H))
        pygame.draw.line(surf, accent_color, (0, TOP_H), (SW, TOP_H), 1)
        _draw_exit_icon(surf, 26, TOP_H // 2, palette)
        draw_text(surf, "Back", 13, light_color, 64, TOP_H // 2, bold=False)
        draw_text_shadow(surf, CAT_NAMES[self.ci], 22, WHITE, SW//2, TOP_H // 2)


def _draw_exit_icon(surf, cx, cy, palette=None):
    """Modern back button: filled circle with a left chevron."""
    if palette is None:
        # Fallback to teal colors
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


