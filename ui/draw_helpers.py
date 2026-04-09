"""
Drawing and UI helper functions.
"""

import pygame
import math

from core.constants import (
    SW, SH, TOP_H, TEAL_DARK, TEAL_DEEP, TEAL_MID,
    WHITE, BLACK, GREY, YELLOW, RED_FLASH, CARD_BG, GREEN_DONE, GREEN_DK,
    ORANGE, ORANGE_DK, ORANGE_WARM,
    CAT_PALETTES
)

_fonts = {}


def get_category_palette(category_index):
    """Get the color palette for a given category index."""
    if 0 <= category_index < len(CAT_PALETTES):
        return CAT_PALETTES[category_index]
    # Fallback to default teal palette
    return CAT_PALETTES[0]


def get_font(size, bold=True):
    k = (size, bold)
    if k not in _fonts:
        _fonts[k] = pygame.font.SysFont("Segoe UI", size, bold=bold)
    return _fonts[k]


def draw_text(surf, text, size, color, cx, cy, bold=True, anchor="center"):
    s = get_font(size, bold).render(str(text), True, color)
    r = s.get_rect()
    if   anchor == "center":
        r.center   = (cx, cy)
    elif anchor == "topleft":
        r.topleft  = (cx, cy)
    elif anchor == "midleft":
        r.midleft  = (cx, cy)
    surf.blit(s, r)


def rrect(surf, color, rect, radius=8):
    pygame.draw.rect(surf, color, rect, border_radius=radius)


def draw_tile_rect(surf, rect):
    """Draw a single tile-sized block with the solid-tile colour."""
    pygame.draw.rect(surf, TEAL_DARK, rect)


def draw_tile_colored(surf, rect, color):
    """Draw a tile-sized block with custom color."""
    pygame.draw.rect(surf, color, rect)


def draw_tiled_platform(surf, rect, ox, oy):
    """Draw a moving-block rect looking identical to normal floor tiles."""
    r = rect.move(ox, oy)
    pygame.draw.rect(surf, TEAL_DARK, r)


def draw_platform_colored(surf, rect, ox, oy, color):
    """Draw a moving-block rect with custom color."""
    r = rect.move(ox, oy)
    pygame.draw.rect(surf, color, r)


def draw_player(surf, x, y, w=26, h=26):
    """Orange square with big cartoon eyes and eye-glint."""
    r = pygame.Rect(int(x - w//2), int(y - h), w, h)
    pygame.draw.rect(surf, ORANGE, r, border_radius=6)
    pygame.draw.rect(surf, ORANGE_DK, r, 2, border_radius=6)
    ew = 8
    eh = 8
    lx = r.x + 4
    rx2 = r.right - 4 - ew
    ey2 = r.y + 6
    pygame.draw.ellipse(surf, WHITE, (lx, ey2, ew, eh))
    pygame.draw.ellipse(surf, WHITE, (rx2, ey2, ew, eh))
    pygame.draw.circle(surf, BLACK, (lx + ew//2 + 1, ey2 + eh//2 + 1), 3)
    pygame.draw.circle(surf, BLACK, (rx2 + ew//2 + 1, ey2 + eh//2 + 1), 3)
    # specular glints
    pygame.draw.circle(surf, WHITE, (lx + 2, ey2 + 2), 1)
    pygame.draw.circle(surf, WHITE, (rx2 + 2, ey2 + 2), 1)


def draw_flag(surf, fx, fy):
    """Goal flag – pole with shadow + warm orange triangular flag."""
    pole_h = 48
    top    = fy - pole_h
    pygame.draw.line(surf, (40, 42, 40), (fx, fy), (fx, top), 3)
    pts = [(fx, top), (fx + 24, top + 12), (fx, top + 24)]
    pygame.draw.polygon(surf, ORANGE_DK, [(x+1, y+1) for x, y in pts])
    pygame.draw.polygon(surf, ORANGE, pts)
    pygame.draw.polygon(surf, ORANGE_WARM, pts, 1)


def draw_spike(surf, cx, bot_y):
    """Single upward spike – grey, looks like a tile when flush."""
    hw = 11
    h = 16
    pts = [(cx, bot_y - h), (cx - hw, bot_y), (cx + hw, bot_y)]
    pygame.draw.polygon(surf, (180, 180, 180), pts)
    pygame.draw.polygon(surf, (80, 80, 80), pts, 1)


def draw_spike_colored(surf, cx, bot_y, color):
    """Single upward spike with custom color."""
    hw = 11
    h = 16
    pts = [(cx, bot_y - h), (cx - hw, bot_y), (cx + hw, bot_y)]
    # Darken color for outline
    dark_color = tuple(max(0, c - 100) for c in color)
    pygame.draw.polygon(surf, color, pts)
    pygame.draw.polygon(surf, dark_color, pts, 1)


def get_saw_blade_radius(rect):
    """Return the radius of the saw blade for collision detection."""
    return min(rect.width, rect.height) // 2 - 4


def draw_saw(surf, rect, ox, oy, rotation=0):
    """Draw a circular saw blade with rotating teeth."""
    r = rect.move(ox, oy)

    # Draw saw circle in the center
    cx = r.centerx
    cy = r.centery
    radius = get_saw_blade_radius(rect)

    # Saw blade circle (red/orange)
    pygame.draw.circle(surf, (220, 80, 50), (cx, cy), radius)
    pygame.draw.circle(surf, (140, 40, 20), (cx, cy), radius, 2)

    # Draw saw teeth (triangular spikes around the circle) with rotation
    num_teeth = 8
    for i in range(num_teeth):
        angle = (i / num_teeth) * 2 * math.pi + rotation
        # Outer tooth point
        tx = cx + math.cos(angle) * (radius + 6)
        ty = cy + math.sin(angle) * (radius + 6)
        # Inner base points
        angle_next = ((i + 1) / num_teeth) * 2 * math.pi + rotation
        tx1 = cx + math.cos(angle - 0.3) * radius
        ty1 = cy + math.sin(angle - 0.3) * radius
        tx2 = cx + math.cos(angle_next + 0.3) * radius
        ty2 = cy + math.sin(angle_next + 0.3) * radius

        pygame.draw.polygon(surf, (240, 100, 60), [(tx, ty), (tx1, ty1), (tx2, ty2)])

    # Central hub (darker)
    pygame.draw.circle(surf, (80, 40, 30), (cx, cy), radius // 3)


def draw_saw_colored(surf, rect, ox, oy, color_light, color_dark, color_hub, rotation=0):
    """Draw a circular saw blade with custom colors."""
    r = rect.move(ox, oy)
    cx = r.centerx
    cy = r.centery
    radius = get_saw_blade_radius(rect)

    # Saw blade circle
    pygame.draw.circle(surf, color_light, (cx, cy), radius)
    pygame.draw.circle(surf, color_dark, (cx, cy), radius, 2)

    # Draw saw teeth with rotation
    num_teeth = 8
    for i in range(num_teeth):
        angle = (i / num_teeth) * 2 * math.pi + rotation
        # Outer tooth point
        tx = cx + math.cos(angle) * (radius + 6)
        ty = cy + math.sin(angle) * (radius + 6)
        # Inner base points
        angle_next = ((i + 1) / num_teeth) * 2 * math.pi + rotation
        tx1 = cx + math.cos(angle - 0.3) * radius
        ty1 = cy + math.sin(angle - 0.3) * radius
        tx2 = cx + math.cos(angle_next + 0.3) * radius
        ty2 = cy + math.sin(angle_next + 0.3) * radius

        pygame.draw.polygon(surf, color_light, [(tx, ty), (tx1, ty1), (tx2, ty2)])

    # Central hub
    pygame.draw.circle(surf, color_hub, (cx, cy), radius // 3)


def _alpha_rect(surf, rgba, rect, radius=0):
    """Blit a translucent (optionally rounded) rect onto surf."""
    r = rect if isinstance(rect, pygame.Rect) else pygame.Rect(*rect)
    w, h = max(1, r.width), max(1, r.height)
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    if radius > 0:
        pygame.draw.rect(s, rgba, (0, 0, w, h), border_radius=max(0, radius))
    else:
        s.fill(rgba)
    surf.blit(s, r.topleft)


def draw_shadow_card(surf, rect, radius=14):
    """Layered soft drop-shadow under a card rect."""
    for i in range(5, 0, -1):
        r2 = rect.inflate(i*2, i*2).move(2, i+1)
        if r2.width > 0 and r2.height > 0:
            _alpha_rect(surf, (6, 24, 20, i * 11), r2, radius + i)


def draw_modern_card(surf, rect, bg, radius=14, hover=False, border_color=None):
    """Shadow → fill → top-shine strip → border (+ hover glow)."""
    draw_shadow_card(surf, rect, radius)
    pygame.draw.rect(surf, bg, rect, border_radius=radius)
    shine_h = max(6, rect.height // 9)
    _alpha_rect(surf, (255, 255, 255, 22),
                pygame.Rect(rect.x+3, rect.y+3, rect.width-6, shine_h), radius-2)
    bc = border_color if border_color else WHITE
    pygame.draw.rect(surf, bc, rect, 2 if hover else 1, border_radius=radius)
    if hover:
        _alpha_rect(surf, (255, 255, 255, 18), rect.inflate(8, 8), radius + 4)


def draw_pill_badge(surf, text, size, fg, bg, cx, cy, px=12, py=5):
    """Pill-shaped badge with top shine. Returns the badge Rect."""
    f  = get_font(size)
    ts = f.render(str(text), True, fg)
    tw, th = ts.get_size()
    r  = pygame.Rect(0, 0, tw + px*2, th + py*2)
    r.center = (cx, cy)
    _alpha_rect(surf, (0, 0, 0, 45), r.move(1, 2), r.height // 2)
    pygame.draw.rect(surf, bg, r, border_radius=r.height // 2)
    _alpha_rect(surf, (255, 255, 255, 38),
                pygame.Rect(r.x+2, r.y+2, r.width-4, r.height//2), r.height//2)
    surf.blit(ts, ts.get_rect(center=(cx, cy)))
    return r


def draw_text_shadow(surf, text, size, color, cx, cy, bold=True, anchor="center"):
    """Draw text with a dark offset shadow for depth."""
    draw_text(surf, text, size, TEAL_DEEP, cx+2, cy+2, bold, anchor)
    draw_text(surf, text, size, color, cx, cy, bold, anchor)


def draw_bg_dots(surf, bg_color=None, dot_color=None):
    """Dark dot-grid background for menu screens. Supports category theming."""
    if bg_color is None:
        bg_color = TEAL_DEEP
    if dot_color is None:
        dot_color = TEAL_MID
    
    surf.fill(bg_color)
    for y in range(0, SH + 28, 28):
        for x in range(0, SW + 28, 28):
            pygame.draw.circle(surf, dot_color, (x, y), 1)


def draw_main_menu_background(surf):
    """Draw an enhanced background for the main category select menu."""
    # Base dark color (rich, sophisticated)
    base_color = (12, 35, 32)
    
    # Fill with base color
    surf.fill(base_color)
    
    # Add a subtle gradient effect with semi-transparent rectangles
    for i in range(0, SH, 40):
        alpha = int(15 * (1 - abs(i - SH//2) / (SH//2)))
        rect = pygame.Rect(0, i, SW, 40)
        gradient_overlay = pygame.Surface((SW, 40), pygame.SRCALPHA)
        gradient_overlay.fill((255, 255, 255, alpha // 4))
        surf.blit(gradient_overlay, rect)
    
    # Draw an enhanced dot pattern with varying sizes for depth
    dot_colors = [
        (40, 80, 75),    # Small darker dots
        (60, 110, 105),  # Medium mid-tone dots
    ]
    
    for y in range(0, SH + 56, 56):
        for x in range(0, SW + 56, 56):
            # Large subtle dots
            pygame.draw.circle(surf, dot_colors[0], (x, y), 2)
            
            # Smaller dots offset
            if (x + y) % 112 == 0:
                pygame.draw.circle(surf, dot_colors[1], (x + 28, y + 28), 1)
    
    # Add a subtle horizontal line at the top for visual separation
    pygame.draw.line(surf, (50, 100, 95), (0, TOP_H), (SW, TOP_H), 1)


def draw_splotch_icon(surf, cx, cy, r, color, num):
    n = 10
    pts = []
    for i in range(n):
        a  = i * 2*math.pi/n
        dr = r * (0.65 + 0.35 * math.sin(i*3.9 + 1.1))
        pts.append((cx + math.cos(a)*dr, cy + math.sin(a)*dr))
    spts = [(int(x+1), int(y+1)) for x, y in pts]
    pygame.draw.polygon(surf, TEAL_DEEP, spts)
    pygame.draw.polygon(surf, color, [(int(x), int(y)) for x, y in pts])
    draw_text(surf, str(num), max(9, r-5), BLACK, cx, cy)


def draw_lock(surf, cx, cy, size=30):
    hw = size//3
    body = pygame.Rect(cx-hw, cy-hw//2, hw*2, int(hw*1.4))
    pygame.draw.rect(surf, (50, 62, 60), body.move(1, 2), border_radius=3)
    pygame.draw.rect(surf, GREY, body, border_radius=3)
    arc_r = pygame.Rect(cx-hw+2, cy-hw-hw//2, (hw-2)*2, hw*2)
    pygame.draw.arc(surf, GREY, arc_r, 0, math.pi, 4)


def draw_flag_icon(surf, cx, cy, size=14, color=WHITE, filled=True):
    pole_top = cy - size
    pygame.draw.line(surf, color, (cx, cy+2), (cx, pole_top), 2)
    pts = [(cx, pole_top), (cx+size, pole_top+size//2), (cx, pole_top+size)]
    if filled:
        pygame.draw.polygon(surf, color, pts)
    else:
        pygame.draw.polygon(surf, color, pts, 1)


def draw_category_icon(surf, ci, cx, cy, size, color):
    """Draw a clearly recognisable icon for each trap category."""
    s  = size
    lw = max(2, s // 22)

    if ci == 0:
        # ── GAPS: two floor slabs with a hole + down-arrow danger + player dot ──
        ph   = max(5, s // 8)
        pw   = s * 5 // 14
        gap  = s // 5
        bot  = cy + s // 6
        # left slab
        pygame.draw.rect(surf, color, (cx - gap//2 - pw, bot, pw, ph), border_radius=2)
        # right slab
        pygame.draw.rect(surf, color, (cx + gap//2,       bot, pw, ph), border_radius=2)
        # down-arrow inside the gap (danger)
        hw  = max(3, s // 12)
        ay2 = bot + ph + s // 7
        pygame.draw.line(surf, color, (cx, bot + 2), (cx, ay2 - hw - 1), lw)
        pygame.draw.polygon(surf, color,
                            [(cx - hw, ay2 - hw*2 + 1), (cx, ay2 + 1), (cx + hw, ay2 - hw*2 + 1)])
        # small player circle on left slab top
        pygame.draw.circle(surf, color,
                           (cx - gap//2 - pw//2, bot - s//8 - 2), max(3, s // 9))

    elif ci == 1:
        # ── SPIKES: flat floor base with three sharp triangles ──
        floor_y = cy + s // 5
        floor_h = max(4, s // 9)
        pygame.draw.rect(surf, color,
                         (cx - s//2 + 2, floor_y, s - 4, floor_h), border_radius=2)
        n_sp       = 3
        sp_w       = max(4, s // 10)
        sp_spacing = (s - 4) // n_sp
        for k in range(n_sp):
            sx     = cx - s//2 + 2 + sp_spacing * k + sp_spacing // 2
            tip_y  = floor_y - s * 2 // 5
            pygame.draw.polygon(surf, color,
                                [(sx, tip_y), (sx - sp_w, floor_y), (sx + sp_w, floor_y)])

    elif ci == 2:
        # ── PUSH: centred block with motion arrows on both sides (←□→) ──
        bsz = s * 2 // 5
        pygame.draw.rect(surf, color,
                         (cx - bsz//2, cy - bsz//2, bsz, bsz), border_radius=3)
        hw  = max(3, s // 11)
        arm = s // 4
        # left arrow ←
        lx0 = cx - bsz//2 - 4
        lx1 = lx0 - arm
        pygame.draw.line(surf, color, (lx0, cy), (lx1 + hw, cy), lw + 1)
        pygame.draw.polygon(surf, color,
                            [(lx1 + hw*2, cy - hw), (lx1, cy), (lx1 + hw*2, cy + hw)])
        # right arrow →
        rx0 = cx + bsz//2 + 4
        rx1 = rx0 + arm
        pygame.draw.line(surf, color, (rx0, cy), (rx1 - hw, cy), lw + 1)
        pygame.draw.polygon(surf, color,
                            [(rx1 - hw*2, cy - hw), (rx1, cy), (rx1 - hw*2, cy + hw)])

    elif ci == 3:
        # ── PLATFORMS: staircase of three floating bars (stepping stones) ──
        bar_w = s * 7 // 12
        bar_h = max(4, s // 9)
        # three bars offset in X and Y like stair steps
        steps = [
            (cx - s*3//10, cy + s//5),
            (cx,           cy),
            (cx + s*3//10, cy - s//5),
        ]
        for bx, by in steps:
            pygame.draw.rect(surf, color,
                             (bx - bar_w//2, by, bar_w, bar_h), border_radius=2)
        # small player square on the top bar
        psz = max(4, s // 8)
        top_bx, top_by = steps[2]
        pygame.draw.rect(surf, color,
                         (top_bx - psz//2, top_by - psz - 2, psz, psz), border_radius=2)

    else:
        # ── SAWS: gear blade with hollow hub + rotation arc ──
        n_teeth = 8
        pts = []
        for k in range(n_teeth * 2):
            a  = k * math.pi / n_teeth - math.pi / 8
            r2 = (s // 2) if k % 2 == 0 else int(s * 0.32)
            pts.append((int(cx + math.cos(a) * r2),
                        int(cy + math.sin(a) * r2)))
        pygame.draw.polygon(surf, color, pts)
        # hollow hub
        hub_r = max(3, s // 7)
        pygame.draw.circle(surf, TEAL_DEEP, (cx, cy), hub_r)
        pygame.draw.circle(surf, color, (cx, cy), hub_r, lw)
        # rotation arc + arrowhead (↻)
        arc_r   = s // 2 + s // 6
        a_start = math.pi * 0.25
        a_end   = math.pi * 1.20
        pygame.draw.arc(surf, color,
                        pygame.Rect(cx - arc_r, cy - arc_r, arc_r * 2, arc_r * 2),
                        a_start, a_end, lw)
        # arrowhead at the end of the arc
        tang = a_end + math.pi / 2
        tip  = (int(cx + math.cos(a_end) * arc_r),
                int(cy - math.sin(a_end) * arc_r))
        hw2  = max(3, s // 10)
        pygame.draw.polygon(surf, color, [
            (int(tip[0] + math.cos(tang + 0.5) * hw2),
             int(tip[1] + math.sin(tang + 0.5) * hw2)),
            (int(tip[0] + math.cos(tang + math.pi) * hw2 * 0.7),
             int(tip[1] + math.sin(tang + math.pi) * hw2 * 0.7)),
            (int(tip[0] + math.cos(tang - 0.5) * hw2),
             int(tip[1] + math.sin(tang - 0.5) * hw2)),
        ])


def draw_deaths_counter(surf, cx, cy, deaths):
    """
    Draw a modern, attractive deaths counter with glow effects.
    
    Features:
    - Gradient rounded badge background
    - Glow/shadow effects
    - Large centered sun/warning icon + counter number
    - Red/orange danger color scheme
    """
    # Badge dimensions
    badge_w, badge_h = 85, 45
    badge_x = cx - badge_w // 2
    badge_y = cy - badge_h // 2
    badge_r = pygame.Rect(badge_x, badge_y, badge_w, badge_h)
    
    # Draw outer glow shadow (multiple layers for smooth glow)
    for glow_size in [12, 8, 4]:
        glow_alpha = int(40 * (1 - glow_size / 12))
        glow_rect = badge_r.inflate(glow_size * 2, glow_size * 2)
        _alpha_rect(surf, (200, 50, 50, glow_alpha), glow_rect, radius=badge_h // 2)
    
    # Draw main badge background with gradient effect
    # Dark red base
    pygame.draw.rect(surf, (180, 30, 30), badge_r, border_radius=badge_h // 2)
    
    # Brighter red top shine for gradient effect
    shine_rect = pygame.Rect(badge_x + 2, badge_y + 2, badge_w - 4, badge_h // 3)
    _alpha_rect(surf, (255, 80, 80, 100), shine_rect, radius=badge_h // 2)
    
    # Border - bright orange/red
    pygame.draw.rect(surf, (255, 120, 60), badge_r, 2, border_radius=badge_h // 2)
    
    # Draw sun/warning icon (centered, with radiating spikes)
    icon_x = cx - 12  # Shifted left to balance with number on right
    icon_y = cy
    
    # Draw radiating spikes (like sun rays)
    num_spikes = 8
    inner_radius = 4
    outer_radius = 10
    
    for i in range(num_spikes):
        angle = (i / num_spikes) * 2 * math.pi
        # Inner point (near center)
        ix = int(icon_x + math.cos(angle) * inner_radius)
        iy = int(icon_y + math.sin(angle) * inner_radius)
        # Outer point (spike tip)
        ox = int(icon_x + math.cos(angle) * outer_radius)
        oy = int(icon_y + math.sin(angle) * outer_radius)
        # Draw spike line
        pygame.draw.line(surf, YELLOW, (ix, iy), (ox, oy), 2)
    
    # Draw center circle (main body of sun icon)
    pygame.draw.circle(surf, YELLOW, (int(icon_x), int(icon_y)), 5)
    # Inner circle for depth
    pygame.draw.circle(surf, (255, 200, 50), (int(icon_x), int(icon_y)), 3)
    
    # Draw death count number (right side)
    number_text = get_font(20, bold=True).render(str(deaths), True, YELLOW)
    number_rect = number_text.get_rect(center=(cx + 20, cy))
    
    # Add subtle shadow under number
    shadow_text = get_font(20, bold=True).render(str(deaths), True, (80, 20, 20))
    shadow_rect = shadow_text.get_rect(center=(cx + 21, cy + 1))
    surf.blit(shadow_text, shadow_rect)
    
    # Blit the number
    surf.blit(number_text, number_rect)
    
    # Add pulse effect indicator (small dot) - positioned at top-right of badge
    pulse_alpha = int(255 * (0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 200)))
    _alpha_rect(surf, (255, 200, 100, pulse_alpha), 
                pygame.Rect(cx + 37, cy - 8, 5, 5), radius=2)


def draw_mute_button(surf, muted=False, x=None, y=None):
    """Draw a mute button using silence.png image.
    
    Args:
        surf: Pygame surface to draw on
        muted: Whether sound is muted
        x: X position (default: left of death counter)
        y: Y position (default: TOP_H // 2)
    
    Returns the button rect for collision detection.
    """
    if x is None:
        x = SW - 150  # Position to the left of death counter
    if y is None:
        y = TOP_H // 2 - 20  # Centered in top bar
    
    btn_rect = pygame.Rect(x, y, 40, 40)
    
    # Draw button background
    bg_color = (200, 60, 60) if muted else (60, 120, 110)
    border_color = (255, 100, 100) if muted else (100, 160, 150)
    
    pygame.draw.rect(surf, bg_color, btn_rect, border_radius=8)
    pygame.draw.rect(surf, border_color, btn_rect, 2, border_radius=8)
    
    # Load and draw the silence.png image
    try:
        import os
        img_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'images', 'silence.png')
        if os.path.exists(img_path):
            img = pygame.image.load(img_path)
            # Scale image to fit button (leave some padding)
            img = pygame.transform.scale(img, (28, 28))
            img_rect = img.get_rect(center=btn_rect.center)
            surf.blit(img, img_rect)
    except:
        # Fallback to text if image loading fails
        icon_color = WHITE
        cx, cy = btn_rect.centerx, btn_rect.centery
        if muted:
            draw_text(surf, "🔇", 24, icon_color, cx, cy)
        else:
            draw_text(surf, "🔊", 24, icon_color, cx, cy)
    
    return btn_rect

