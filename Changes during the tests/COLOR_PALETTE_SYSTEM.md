# Category-Specific Color Palette System

## Overview
A comprehensive color theming system has been implemented that ensures each category level maintains visual consistency with its category card colors. Each level displays a unique, cohesive color palette that matches the category it belongs to.

## Categories and Their Color Palettes

### 1. **Gaps** (Teal/Cyan)
- **Primary Color**: `(70, 180, 168)` - Main platform color
- **Dark Variant**: `(45, 130, 120)` - Tile/platform outlines
- **Light Variant**: `(100, 210, 200)` - Accents
- **Accent Color**: `(120, 230, 220)` - UI highlights
- **Spike Color**: `(160, 160, 160)` - Neutral grey spikes

### 2. **Spikes** (Red)
- **Primary Color**: `(185, 75, 75)` - Main platform color
- **Dark Variant**: `(140, 50, 50)` - Tile/platform outlines
- **Light Variant**: `(220, 100, 100)` - Accents
- **Accent Color**: `(240, 130, 130)` - UI highlights
- **Spike Color**: `(200, 100, 100)` - Category-colored spikes

### 3. **Push** (Blue)
- **Primary Color**: `(75, 130, 185)` - Main platform color
- **Dark Variant**: `(50, 95, 140)` - Tile/platform outlines
- **Light Variant**: `(110, 160, 210)` - Accents
- **Accent Color**: `(140, 180, 230)` - UI highlights
- **Spike Color**: `(160, 160, 160)` - Neutral grey spikes

### 4. **Platforms** (Purple)
- **Primary Color**: `(125, 75, 185)` - Main platform color
- **Dark Variant**: `(90, 50, 140)` - Tile/platform outlines
- **Light Variant**: `(160, 110, 220)` - Accents
- **Accent Color**: `(190, 140, 240)` - UI highlights
- **Spike Color**: `(160, 160, 160)` - Neutral grey spikes

### 5. **Saws** (Orange/Gold)
- **Primary Color**: `(185, 145, 50)` - Main platform color
- **Dark Variant**: `(140, 110, 30)` - Tile/platform outlines
- **Light Variant**: `(220, 175, 80)` - Accents
- **Accent Color**: `(240, 200, 110)` - UI highlights
- **Spike Color**: `(160, 160, 160)` - Neutral grey spikes

## Implementation Details

### Core Files Modified

#### 1. `core/constants.py`
Added `CAT_PALETTES` list containing 5 dictionaries (one per category), each with:
- `'primary'`: Base color used for background
- `'dark'`: Dark variant for platforms and tiles
- `'light'`: Light variant for accents
- `'accent'`: Bright color for UI elements and headers
- `'spike'`: Color for spike hazards

#### 2. `ui/draw_helpers.py`
Added helper functions:
- `get_category_palette(category_index)`: Retrieves the palette for a given category
- `draw_tile_colored(surf, rect, color)`: Draws tiles with custom color
- `draw_platform_colored(surf, rect, ox, oy, color)`: Draws moving platforms with custom color
- `draw_spike_colored(surf, cx, bot_y, color)`: Draws spikes with custom color
- `draw_saw_colored(surf, rect, ox, oy, color_light, color_dark, color_hub, rotation)`: Draws saws with custom colors

#### 3. `scenes/level_scene.py`
Updated `LevelScene.draw()` method to:
- Retrieve the category palette using `get_category_palette(self.ci)`
- Apply palette colors to:
  - Background (primary color)
  - Tiles (dark color)
  - Moving blocks (passed via palette parameter)
  - Top bar and UI elements (accent colors)
  - Win card overlay (category primary color)
- Pass palette to all drawing functions

#### 4. `engine/mblock.py`
Updated `MBlock.draw()` method to:
- Accept optional `palette` parameter
- Use palette colors for platforms and saws
- Maintain backward compatibility with default colors when palette is None

#### 5. `engine/spike.py`
Updated `SpikeObj.draw()` method to:
- Accept optional `palette` parameter
- Use palette spike color when available
- Maintain backward compatibility with default grey spikes

## Visual Features

### Consistent Color Theming
Each level maintains visual cohesion through:
1. **Matching Category Card Colors**: Levels use the exact same primary color as their category card
2. **Layered Depth**: Dark variants provide platform visibility and edge definition
3. **UI Consistency**: Top bar, buttons, and overlays use accent colors matching the category

### Dynamic Element Coloring
All game elements adapt to the category:
- **Static Platforms**: Use dark color for clear visibility
- **Moving Platforms**: Same dark color for visual consistency
- **Saw Blades**: Light color for blade, dark for outline and hub
- **Spikes**: Category-specific color (mostly neutral grey, red for Spikes category)
- **Background**: Category primary color around play area
- **Top Bar**: Dark color for contrast
- **Accents**: Light/accent colors for highlights and UI elements

## Usage in Game

### For Players
- **Visual Recognition**: Instantly know which category you're in by the level colors
- **Aesthetic Consistency**: Everything feels cohesive and intentional
- **Less Visual Fatigue**: Each category has its own color personality

### For Developers
All colored drawing is handled automatically when passing the palette:

```python
palette = get_category_palette(category_index)
# Pass palette to draw methods:
mblock.draw(surf, ox, oy, palette)
spike_obj.draw(surf, ox, oy, palette)
draw_tile_colored(surf, rect, palette['dark'])
```

## Benefits

✅ **Brand Consistency**: Each category maintains its visual identity across all levels
✅ **Enhanced UX**: Players instantly recognize which category they're playing
✅ **Professional Polish**: Cohesive color schemes create a polished game feel
✅ **Easy Customization**: Colors are centralized in one location (`CAT_PALETTES`)
✅ **Backward Compatible**: Default drawing functions still work without palettes
✅ **Extensible**: Easy to add new categories or adjust existing colors

## Future Enhancements

Potential improvements:
- Animated color transitions when switching levels
- Dynamic palette adjustment based on difficulty
- Color-blind friendly palette variants
- Player customizable color themes

