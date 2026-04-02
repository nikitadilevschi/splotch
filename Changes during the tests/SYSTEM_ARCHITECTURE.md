# Color Palette System Architecture

## System Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    GAME INITIALIZATION                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Player Selects Category (0-4)                   │
│           (Category Select Scene shows cards)               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Level Scene Initialized                         │
│         (self.ci stores category index)                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  get_category_palette(self.ci) → Returns Palette Dict       │
│                                                              │
│  Returns: {                                                 │
│    'primary': (R,G,B),    ← Background color               │
│    'dark': (R,G,B),       ← Platform & tile color          │
│    'light': (R,G,B),      ← Accent color                   │
│    'accent': (R,G,B),     ← UI highlight color             │
│    'spike': (R,G,B)       ← Spike color                    │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  RENDERING PIPELINE (Every Frame)                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ▼ draw_tile_colored(rect, palette['dark'])               │
│    All static tiles rendered in category dark color        │
│                                                              │
│  ▼ mblock.draw(palette)                                    │
│    Moving platforms/saws use palette colors                │
│                                                              │
│  ▼ spike.draw(palette)                                     │
│    Spikes use palette['spike'] color                       │
│                                                              │
│  ▼ UI Elements                                              │
│    Top bar: palette['dark']                                │
│    Accents: palette['accent']                              │
│    Overlays: palette['primary']                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  RESULT: Fully themed level with category colors            │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
core/constants.py (CAT_PALETTES)
         │
         ├─ Index 0: Gaps Palette (Teal)
         ├─ Index 1: Spikes Palette (Red)
         ├─ Index 2: Push Palette (Blue)
         ├─ Index 3: Platforms Palette (Purple)
         └─ Index 4: Saws Palette (Orange)
         │
         ▼
ui/draw_helpers.py
         │
         ├─ get_category_palette(ci) ──┐
         │                             │
         ├─ draw_tile_colored()       │
         │                             │
         ├─ draw_platform_colored()   │
         │                             │
         ├─ draw_spike_colored()      │
         │                             │
         └─ draw_saw_colored()        │
                                       │
                ┌──────────────────────┘
                │
                ▼
        scenes/level_scene.py
                │
                ├─ Passes palette to mblock.draw()
                │
                ├─ Passes palette to spike.draw()
                │
                └─ Uses palette for UI theming
                │
                ├─────────────────────┐
                │                     │
                ▼                     ▼
          engine/mblock.py      engine/spike.py
                │                     │
                └──────────┬──────────┘
                           │
                           ▼
              Colored Platforms & Spikes Rendered
```

## Color Palette Structure

Each category palette is a dictionary with 5 colors:

```
{
    'primary':    RGB tuple  ← Background, win overlay
    'dark':       RGB tuple  ← Platforms, tiles, top bar
    'light':      RGB tuple  ← Accent highlights
    'accent':     RGB tuple  ← UI elements, borders
    'spike':      RGB tuple  ← Spike hazards
}
```

## Usage Example

```python
# In level_scene.py during draw()
palette = get_category_palette(self.ci)

# Apply to tiles
for tile in tiles:
    draw_tile_colored(surf, tile_rect, palette['dark'])

# Apply to moving blocks
for mblock in moving_blocks:
    mblock.draw(surf, ox, oy, palette)

# Apply to UI
pygame.draw.rect(surf, palette['dark'], top_bar_rect)
draw_pill_badge(surf, text, size, WHITE, palette['accent'], cx, cy)
```

## Color Consistency Table

| Element | Primary | Dark | Light | Accent | Spike |
|---------|---------|------|-------|--------|-------|
| Background | ✓ | | | | |
| Platforms | | ✓ | | | |
| Tiles | | ✓ | | | |
| Top Bar | | ✓ | | | |
| UI Highlights | | | ✓ | | |
| Buttons/Badges | | | | ✓ | |
| Spikes | | | | | ✓ |
| Win Overlay | ✓ | | | | |
| Accents | | | | ✓ | |

## Adding a New Category

To add a 6th category:

1. Edit `core/constants.py`:
   ```python
   CAT_COLORS.append((NEW_R, NEW_G, NEW_B))  # Add to color list
   
   CAT_PALETTES.append({                     # Add to palettes
       'primary':    (R, G, B),
       'dark':       (R, G, B),
       'light':      (R, G, B),
       'accent':     (R, G, B),
       'spike':      (R, G, B),
   })
   ```

2. The system automatically applies the new palette to all levels in that category!

## Summary

This architecture ensures:
- ✅ **Centralized Color Management** - All colors in one place
- ✅ **Automatic Application** - Dynamic based on category
- ✅ **Easy Customization** - Change colors without code changes
- ✅ **Scalable** - Add categories/colors easily
- ✅ **Maintainable** - Clean separation of concerns

