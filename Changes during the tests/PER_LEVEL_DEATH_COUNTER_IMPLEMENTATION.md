# Per-Level Death Counter Implementation

## Overview
Individual death counters have been implemented for each level. Players can now see exactly how many times they've died on each specific level, displayed both during gameplay and in the level selection screen.

## What Changed

### 1. Level Select Scene (`scenes/level_select.py`)

#### Added Per-Level Death Display on Level Cards
Each level card in the level select screen now displays the number of deaths for that specific level:

```python
# ── Per-level death counter ──
level_key = f"{self.ci}_{i}"
level_deaths = self.game.save['level_deaths'].get(level_key, 0)
deaths_text = f"Deaths: {level_deaths}"
deaths_color = light_color if done else (120, 140, 136)
draw_text(surf, deaths_text, 11, deaths_color, r.centerx, r.bottom - 16, bold=False)
```

**Features:**
- Displays "Deaths: X" at the bottom of each level card
- Color changes based on level completion status:
  - Brighter color (light_color) for completed levels
  - Muted color (120, 140, 136) for incomplete levels
- Positioned at the bottom of each card for easy visibility

### 2. Level Scene (`scenes/level_scene.py`)

#### Updated Death Counter Display
The death counter in the top-right corner now shows the per-level death count instead of the global total:

```python
# Display per-level death counter for current level
level_key = f"{self.ci}_{self.li}"
level_deaths = self.game.save['level_deaths'].get(level_key, 0)
draw_deaths_counter(surf, SW - 42, TOP_H // 2, level_deaths)
```

**Features:**
- Shows the total deaths for the current level (accumulated across all plays)
- Updates in real-time as the player dies
- Displays separate from "Deaths this run" (which shows deaths in the current session)

## Data Flow

### When Deaths Are Recorded
1. Player dies (falls, hits spike, hits saw, or presses R)
2. `_die()` method in `LevelScene` is called
3. Both global and per-level counters are incremented:
   ```python
   self.game.save['deaths'] += 1  # Global counter
   self.game.save['level_deaths'][level_key] += 1  # Per-level counter
   ```
4. Save file is updated

### Accessing Per-Level Deaths

```python
# In level select scene
level_key = f"{category_index}_{level_index}"
level_deaths = self.game.save['level_deaths'].get(level_key, 0)

# In level scene
level_key = f"{self.ci}_{self.li}"
level_deaths = self.game.save['level_deaths'].get(level_key, 0)
```

## Display Locations

### Level Selection Screen
- **Position:** Bottom of each level card (16 pixels from bottom)
- **Format:** "Deaths: X"
- **Font Size:** 11pt
- **Updates:** When returning from a level

### Level Scene (During Gameplay)
- **Position:** Top-right corner (same position as before)
- **Icon:** Skull icon with death count
- **Updates:** In real-time as deaths occur

## Example Save File Structure

```json
{
  "deaths": 45,
  "level_deaths": {
    "0_0": 3,
    "0_1": 8,
    "0_2": 5,
    "1_0": 12,
    "1_1": 9,
    "1_2": 4,
    "2_0": 2,
    "2_1": 2,
    "3_0": 0,
    "4_2": 0,
    "5_0": 1,
    "5_1": 1,
    "5_2": 1,
    "6_0": 0
  },
  "completed": {
    "0_0": true,
    "0_1": true,
    "0_2": true,
    "1_0": true,
    "1_1": true
  },
  ...
}
```

## Key Differences from Global Counter

| Feature | Global Counter | Per-Level Counter |
|---------|---|---|
| Tracked in | `deaths` field | `level_deaths` dictionary |
| Scope | All levels combined | Individual level |
| Display Location | Removed from main menu | Level select & gameplay |
| Purpose | Overall statistics | Level-specific difficulty tracking |
| Reset Behavior | Resets with save | Tracks lifetime deaths per level |

## Backward Compatibility

- ✅ Existing save files automatically migrate
- ✅ The `load_save()` function initializes `level_deaths` as empty dict if missing
- ✅ No data loss when loading old saves
- ✅ New levels get tracked automatically without code changes

## User Experience

### For Players
- See exactly how many times they've struggled on each level
- Track improvement across multiple playthroughs
- Compare difficulty between levels within a category
- Motivating feedback on progress

### For Developers
- Identify problematic levels (high death counts)
- Balance difficulty based on death statistics
- Create difficulty ratings for each level
- Enable future leaderboards per level

## Technical Implementation Details

### Key Format
- Format: `"{category_index}_{level_index}"`
- Example: `"3_2"` = Category 3 (Platforms), Level 2
- Range: `"0_0"` to `"6_2"` (7 categories × 3 levels)

### Color Logic (Level Select)
```python
deaths_color = light_color if done else (120, 140, 136)
```
- **Completed levels:** Use `light_color` from category palette (bright)
- **Incomplete levels:** Use `(120, 140, 136)` (muted grey-teal)

### Display Update Timing
- **Immediate:** During gameplay (top-right counter)
- **On Return:** When coming back to level select from a level
- **Persistent:** Saved to disk automatically on each death

## Future Enhancement Possibilities

1. **Best Run Statistics** - Track fewest deaths in a single run
2. **Category Statistics** - Show total deaths per category
3. **Difficulty Rating** - Auto-calculate level difficulty from death counts
4. **Achievements** - "Complete without deaths" badges per level
5. **Leaderboards** - Rank players by deaths per level
6. **Comparative UI** - Show average deaths vs your deaths
7. **Performance Analytics** - Track improvement over time

## Files Modified

| File | Changes |
|------|---------|
| `scenes/level_select.py` | Added per-level death display on level cards |
| `scenes/level_scene.py` | Updated to display per-level counter instead of global |
| `core/save_manager.py` | Added `level_deaths` dictionary (previously) |

## Testing Checklist

- ✅ Death counters increment correctly on each death
- ✅ Per-level counters persist across sessions
- ✅ Level select displays correct death counts
- ✅ Level scene displays correct death counts
- ✅ Colors adjust based on completion status
- ✅ Global counter still maintained for statistics
- ✅ Backward compatible with existing saves

