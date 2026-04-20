# Changelog

All notable changes to the Rage Bait project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-04-20

### Added

#### New Teleporters Category
- 🌀 New 7th category: **Teleporters** with 3 dedicated puzzle levels
- Animated teleporter portals with optional path movement
- Sensor-triggered teleporter activation and movement support

#### Gameplay
- Expanded from 6 to 7 categories
- Expanded from 18 to 21 total levels
- Advanced teleporter behaviors:
  - Multiple teleport destinations
  - `self_top` destination mode (teleport above current portal position)
  - Configurable teleport cooldown
- Sensor-triggered goal relocation support in level data
- Per-level fall-speed tuning support (`max_fall`)

### Technical
- Added `levels/teleporters.py` with `TELEPORTERS_L1..L3`
- Added `engine/teleporter.py` teleporter system and runtime destination logic
- Extended `levels/builder.py` to build teleporter variants and destination modes
- Extended save tracking with per-level deaths (`level_deaths`)

### Documentation
- Updated `README.md` to reflect 7 categories / 21 levels and version `1.3.0`

## [1.2.0] - 2026-04-10

### Added

#### New Controls Category
- 🎮 New 6th category: **Controls** - Tutorial-style levels for learning mechanics
- 3 new levels introducing game controls and jumping mechanics
- Green color palette for Controls category
- Progressive difficulty in Controls levels (basic movement → complex platforming)
- No traps or hazards - focuses purely on movement mechanics

#### Gameplay
- Expanded from 5 to 6 categories
- Expanded from 15 to 18 total levels
- New category icon for Controls (gamepad controller concept)

### Technical
- Updated constants.py to include Controls category colors
- Added levels/controls.py with 3 tutorial levels
- Updated save system to track Controls progress
- Updated LEVELS array to include Controls category

### Documentation
- Updated README to reflect 6 categories and 18 levels
- Updated project structure documentation

---

## [1.1.0] - 2026-04-09

### Added

#### Audio & Sound System
- 🔊 Complete sound system with Pygame mixer integration
- 🔊 Background music that loops during gameplay and main menu
- 🔊 Jump sound effect (ascending tone)
- 🔊 Death sound effect (descending tone)
- 🔊 Victory/win sound effect (uplifting chord)
- 🔇 Mute button with persistent state (saved to save.json)
- 🔇 Sound controls on both main menu and level scenes
- 🔊 Volume-adjustable sound effects (0.0 to 1.0)

#### UI/UX Improvements
- 🎨 Mute button with silence.png icon image
- 🎨 Color-coded mute button (green for unmuted, red for muted)
- 🎨 Mute button positioned next to death counter on top-right
- 🎨 Sound state persists between game sessions

#### Branding
- 🎮 Game rebranded from "Splotch" to "Rage Bait"
- 🎮 Updated all window titles and in-game displays
- 🎮 Updated documentation to reflect new branding

### Technical
- 🔧 New `core/sound_manager.py` module for centralized sound management
- 🔧 Sound state stored in save data with fallback support
- 🔧 Graceful degradation when sound files are missing
- 🔧 Proper jump detection using player.jumped flag for reliable sound triggering

### Documentation
- 📖 Added SOUND_SETUP.md with sound configuration guide
- 📖 Added MUTE_BUTTON_README.md with mute button implementation details
- 📖 Added sound generation scripts for creating placeholder audio

---

## [1.0.0] - 2026-04-02

### Added

#### Features
- ✨ Complete 5-category platformer game (15 levels total)
- ✨ Dynamic color palette system for visual theming
- ✨ 5 unique game mechanics: GAPS, SPIKES, PUSH, PLATFORMS, SAWS
- ✨ Persistent save system with JSON storage
- ✨ Death counter and progress tracking
- ✨ Smooth physics engine with collision detection
- ✨ Mobile platform "carry" mechanics
- ✨ Crush detection between platforms
- ✨ Professional UI with animated transitions
- ✨ Category selection scene with visual cards
- ✨ Level selection with completion indicators
- ✨ Dynamic background theming per category
- ✨ Head-up display (HUD) with death counter
- ✨ Victory overlay with category colors
- ✨ Visual progress indicators (flags)

#### Technical
- 🔧 Scene-based game architecture
- 🔧 Timeline animation system for moving platforms
- 🔧 Sensor-based activation for dynamic obstacles
- 🔧 Gravity-based physics with terminal velocity
- 🔧 Rectangle-based collision detection
- 🔧 Save state management with auto-save
- 🔧 Category-based level organization

#### Documentation
- 📖 Comprehensive technical documentation
- 📖 Color palette system guide
- 📖 Architecture documentation
- 📖 Implementation guides

