# Background Color Update - Level Selector Scene

## Changes Made

### 1. **Updated `draw_bg_dots()` Function**
**File:** `ui/draw_helpers.py`

Modified the function to accept optional category colors:

```python
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
```

**Features:**
- ✅ Maintains backward compatibility (uses default colors if none provided)
- ✅ Accepts `bg_color` for background fill
- ✅ Accepts `dot_color` for dot pattern
- ✅ Easy to use with category palettes

### 2. **Updated Level Selector Drawing**
**File:** `scenes/level_select.py`

Now passes category colors to `draw_bg_dots()`:

```python
# Apply category background colors
dark_bg = tuple(max(0, c - 40) for c in primary_color)  # Darker variant
draw_bg_dots(surf, dark_bg, dark_color)
```

**What this does:**
- Creates a darker variant of the primary color for the background
- Uses the category dark color for the dot pattern
- Results in a cohesive, themed appearance

---

## Visual Result

### Before
- Level selector background: Fixed teal color (TEAL_DEEP)
- Same appearance for all categories

### After
- **Gaps Level Selector** - Dark teal background
- **Spikes Level Selector** - Dark red background ✅
- **Push Level Selector** - Dark blue background
- **Platforms Level Selector** - Dark purple background
- **Saws Level Selector** - Dark orange background

Each category's level selector now has a fully themed background that matches the category!

---

## Color Application

| Part | Color Source |
|------|--------------|
| Background fill | Primary color (darkened 40 points) |
| Dot pattern | Category dark color |
| Top bar | Category dark color |
| Text accents | Category light color |
| Play buttons | Category accent color |

---

## Complete User Flow (Fully Themed)

```
1. Category Select
   └─ Shows all 5 categories with default background

2. Level Select (After selecting category)
   └─ Background: Category primary color (darkened)
   └─ Dots: Category dark color
   └─ Top bar: Category dark color
   └─ Text: Category light color
   └─ Buttons: Category accent color

3. Level Play
   └─ Everything in category colors
   └─ Perfect visual consistency!
```

---

## Status

✅ **Update Complete**
- All files error-free
- Background now uses category colors
- Full visual theming achieved
- Production ready

The level selector scene is now fully themed to match its category!

