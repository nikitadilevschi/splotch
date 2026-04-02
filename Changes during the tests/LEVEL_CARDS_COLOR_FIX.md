# Level Card Colors - Fix Update

## Issue Fixed

The level cards were showing hardcoded green colors instead of using category-specific palette colors.

## Changes Made

**File:** `scenes/level_select.py`

### Problem
```python
# OLD CODE - Hardcoded colors
if locked:
    bg = (36, 48, 46)
elif done:
    bg = (30, 118, 56)  # ❌ HARDCODED GREEN
elif hov:
    bg = tuple(min(255, c + 28) for c in cc)
else:
    bg = tuple(max(0, c - 14) for c in cc)

fg_num = GREY if locked else (YELLOW if done else WHITE)  # ❌ YELLOW badges
```

### Solution
```python
# NEW CODE - Uses category palette
if locked:
    bg = (36, 48, 46)  # Stay dark for locked
elif done:
    bg = dark_color  # ✅ Use category dark color
elif hov:
    bg = tuple(min(255, c + 28) for c in cc)
else:
    bg = tuple(max(0, c - 14) for c in cc)

fg_num = GREY if locked else (light_color if done else WHITE)  # ✅ Category light color
```

## What Changed

### Card Background Colors
- **Locked:** Dark grey (unchanged)
- **Available:** Category primary color (darker shade)
- **Hover:** Category primary color (lighter shade)
- **Done:** Category dark color (✅ NOW THEMED!)

### Badge Number Colors
- **Locked:** Grey (unchanged)
- **Available:** White
- **Done:** Category light color (✅ NOW THEMED!)

## Visual Result

### Before (Spikes Category - Green cards)
```
┌─────────────────────────────┐
│  Green Card (DONE)          │  ❌ Wrong color
│  Green Card (DONE)          │
│  Green Card (DONE)          │
└─────────────────────────────┘
```

### After (Spikes Category - Red cards)
```
┌─────────────────────────────┐
│  Red Card (DONE)            │  ✅ Correct color
│  Red Card (DONE)            │
│  Red Card (DONE)            │
└─────────────────────────────┘
```

## All Category Examples

| Category | Level Cards Color |
|----------|-------------------|
| **Gaps** | Teal |
| **Spikes** | Red ✅ |
| **Push** | Blue |
| **Platforms** | Purple |
| **Saws** | Orange |

## Status

✅ **Issue Fixed**
- Level cards now use category colors
- All states properly themed
- Badges show category light colors
- Production ready

The level cards now perfectly match the category theme!

