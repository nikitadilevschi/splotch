"""
Category selection scene.
"""

import pygame
import sys

from core.constants import (
    SW, SH, TOP_H, TEAL_DEEP, TEAL_MID, WHITE, GREY, BLACK, TEAL_LIGHT,
    CAT_NAMES, CAT_COLORS
)
from core.sound_manager import get_sound_manager
from core.save_manager import write_save
from ui.draw_helpers import (
    draw_text_shadow, draw_text, draw_modern_card,
    draw_lock, draw_category_icon, draw_pill_badge, rrect,
    draw_deaths_counter, draw_main_menu_background,
    get_category_palette, draw_flag_icon, draw_mute_button
)


class CategorySelectScene:
    def __init__(self, game):
        self.game  = game
        self.sound_mgr = get_sound_manager()
        # Ensure background music is playing on main menu
        if not self.sound_mgr.music_playing:
            self.sound_mgr.play_background_music()
        # Sync mute state from save
        self.sound_mgr.set_muted(self.game.save.get('muted', False))
        self.hover = -1
        self.reset_confirm = False
        self.mute_btn_rect = None
        
        # Scrolling variables
        self.scroll_offset = 0  # Horizontal scroll position in pixels

    def _cards(self):
        """Get category card positions with smooth scrolling applied."""
        cw, ch = 162, 290
        gap = 12
        
        # Calculate center position and apply scroll offset
        total = 5 * cw + 4 * gap  # Updated for 7 categories
        x0 = (SW - total) // 2 - self.scroll_offset
        y0 = TOP_H + 110
        
        # Return list of (category_index, rect) for proper identification
        cards = []
        for i in range(7):  # Updated to 7 categories
            x = x0 + i * (cw + gap)
            cards.append((i, pygame.Rect(x, y0, cw, ch)))
        
        return cards

    def _reset_btn(self):
        return pygame.Rect(SW//2-85, SH-80, 170, 32)

    def handle_event(self, ev):
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if ev.key == pygame.K_r and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                if self.reset_confirm:
                    self.game.reset_save()
                else:
                    self.reset_confirm = True
            # Smooth scrolling with arrow keys
            if ev.key == pygame.K_LEFT:
                cw, gap = 162, 12
                self.scroll_offset = max(0, self.scroll_offset - (cw + gap))
            if ev.key == pygame.K_RIGHT:
                cw, gap = 162, 12
                total = 7 * cw + 6 * gap  # Updated for 7 categories
                max_scroll = max(0, total - (SW - 100))
                self.scroll_offset = min(max_scroll, self.scroll_offset + (cw + gap))
        
        # Mouse wheel scrolling
        if ev.type == pygame.MOUSEWHEEL:
            cw, gap = 162, 12
            if ev.y > 0:  # Scroll up = scroll left
                self.scroll_offset = max(0, self.scroll_offset - (cw + gap))
            elif ev.y < 0:  # Scroll down = scroll right
                total = 7 * cw + 6 * gap  # Updated for 7 categories
                max_scroll = max(0, total - (SW - 100))
                self.scroll_offset = min(max_scroll, self.scroll_offset + (cw + gap))
        
        if ev.type == pygame.MOUSEMOTION:
            self.hover = -1
            for cat_idx, r in self._cards():
                if r.collidepoint(ev.pos):
                    self.hover = cat_idx
        
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button==1:
            mx,my = ev.pos
            
            # Check mute button
            if self.mute_btn_rect and self.mute_btn_rect.collidepoint(mx, my):
                self.sound_mgr.toggle_mute()
                self.game.save['muted'] = self.sound_mgr.muted
                write_save(self.game.save)
                return
            
            for cat_idx, r in self._cards():
                if r.collidepoint(ev.pos):
                    if cat_idx in self.game.save['unlocked_cats']:
                        self.game.go_level_select(cat_idx)
                    self.reset_confirm = False
                    return
            
            if self._reset_btn().collidepoint(mx,my):
                if self.reset_confirm:
                    self.game.reset_save()
                else:
                    self.reset_confirm = True
            else:
                self.reset_confirm = False

    def update(self, dt):
        pass

    def draw(self, surf):
        draw_main_menu_background(surf)

        # ── Hero title ──
        draw_text_shadow(surf, "RAGE BAIT", 68, WHITE, SW//2, TOP_H + 52)
        draw_text(surf, "How far can you go before you get splotched?",
                  14, TEAL_LIGHT, SW//2, TOP_H + 92, bold=False)

        # ── Deaths breakdown by category ──
        level_deaths = self.game.save.get('level_deaths', {})
        category_deaths = {}
        for key, count in level_deaths.items():
            cat_idx = int(key.split('_')[0])
            category_deaths[cat_idx] = category_deaths.get(cat_idx, 0) + count
        
        # Build and display deaths summary
        deaths_summary = "Deaths: "
        for i in range(7):
            deaths_summary += f"{CAT_NAMES[i][:3]} {category_deaths.get(i, 0)} "
        draw_text(surf, deaths_summary, 10, TEAL_LIGHT, SW//2, TOP_H + 115, bold=False)

        tips = ["Fake floors", "Pop-up spikes", "Sneaky blocks",
                "Shifting platforms", "Hidden traps", "Learn controls", "Dimension shift"]

        for cat_idx, r in self._cards():
            unl = cat_idx in self.game.save['unlocked_cats']
            cc  = CAT_COLORS[cat_idx]
            hov = (self.hover == cat_idx and unl)

            # Get category palette for coloring
            palette = get_category_palette(cat_idx)
            category_accent = palette['accent']

            if not unl:
                bg = (36, 48, 46)
            elif hov:
                bg = tuple(min(255, c + 28) for c in cc)
            else:
                bg = tuple(max(0, c - 14) for c in cc)

            border = WHITE if unl else (62, 78, 76)
            draw_modern_card(surf, r, bg, radius=16, hover=hov, border_color=border)

            fg = WHITE if unl else GREY

            # ── Category name ──
            draw_text(surf, CAT_NAMES[cat_idx], 16, fg, r.centerx, r.y + 24)
            if unl:
                pygame.draw.line(surf, TEAL_MID,
                                 (r.x + 16, r.y + 40), (r.right - 16, r.y + 40), 1)

            # ── Centre icon or lock ──
            if not unl:
                draw_lock(surf, r.centerx, r.centery - 8, 40)
            else:
                all_done = all(
                    self.game.save['completed'].get(f"{cat_idx}_{li}", False)
                    for li in range(3))
                icon_col = category_accent if all_done else WHITE
                draw_category_icon(surf, cat_idx, r.centerx, r.centery - 22, 54, icon_col)
                if all_done:
                    draw_pill_badge(surf, "COMPLETE", 11, BLACK, category_accent,
                                    r.centerx, r.centery + 32)

            # ── Progress flags ──
            if unl:
                flag_sz   = 12
                spacing_d = 25
                # centre the group accounting for flag extending right
                x_start = r.centerx - spacing_d - flag_sz // 2
                flag_y  = r.bottom - 52
                for li in range(3):
                    done = self.game.save['completed'].get(f"{cat_idx}_{li}", False)
                    fx   = x_start + li * spacing_d
                    col  = category_accent if done else (68, 90, 86)
                    draw_flag_icon(surf, fx, flag_y, size=flag_sz,
                                   color=col, filled=done)

            # ── Tip text ──
            draw_text(surf, tips[cat_idx], 11, fg, r.centerx, r.bottom - 24, bold=False)

        # ── Reset button ──
        rb  = self._reset_btn()
        bg_rb = (168, 58, 54) if self.reset_confirm else (38, 66, 62)
        rrect(surf, bg_rb, rb, 8)
        pygame.draw.rect(surf,
                         (200, 78, 74) if self.reset_confirm else (68, 94, 90),
                         rb, 1, border_radius=8)
        draw_text(surf, "Confirm Reset?" if self.reset_confirm else "Reset Save",
                  14, WHITE, rb.centerx, rb.centery)

        draw_text(surf, "Click a category  ·  Ctrl+R = reset save  ·  Scroll = ← → or mouse wheel",
                  12, (120, 172, 166), SW//2, SH - 14, bold=False)

        # ── Top bar (rendered last, always on top) ──
        pygame.draw.rect(surf, TEAL_DEEP, (0, 0, SW, TOP_H))
        pygame.draw.line(surf, TEAL_MID, (0, TOP_H), (SW, TOP_H), 1)
        draw_text_shadow(surf, "RAGE BAIT", 22, WHITE, SW//2, TOP_H // 2)
        total_deaths = self.game.save.get('deaths', 0)
        draw_deaths_counter(surf, SW - 42, TOP_H // 2, total_deaths)
        self.mute_btn_rect = draw_mute_button(surf, self.sound_mgr.muted)


