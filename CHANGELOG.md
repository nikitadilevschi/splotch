# Changelog

All notable changes to the SPLOTCH project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- 📖 Comprehensive technical documentation (Romanian)
- 📖 Color palette system guide
- 📖 Architecture documentation
- 📖 Implementation guides

### Game Categories

#### GAPS (Teal Theme)
- 3 levels with increasing gap sizes
- Platforms that collapse when player lands
- Progressive difficulty: 3, 3, 3+ tile gaps
- Teal color scheme (Primary: 70, 180, 168)

#### SPIKES (Red Theme)
- 3 levels with hidden guillotines
- Sensor-based spike activation
- Multiple spike hazards per level
- Red color scheme (Primary: 185, 75, 75)

#### PUSH (Blue Theme)
- 3 levels with horizontal moving blocks
- Blocks that push player across gaps
- Dynamic block timing and coordination
- Blue color scheme (Primary: 75, 130, 185)

#### PLATFORMS (Purple Theme)
- 3 levels with vertical moving platforms
- Crush detection between platforms
- Complex platform choreography
- Purple color scheme (Primary: 125, 75, 185)

#### SAWS (Orange Theme)
- 3 levels with rotating saw blades
- Saws that move along paths
- Multiple saws with offset patterns
- Orange color scheme (Primary: 185, 145, 50)

### Systems

#### Color System
- 5 unique color palettes (one per category)
- 5 colors per palette: primary, dark, light, accent, spike
- Dynamic application throughout game
- Category-specific theming for all UI elements

#### Physics System
- Gravity acceleration (800 pixels/s²)
- Terminal velocity (800 pixels/s)
- Platform collision detection
- Horizontal and vertical collision handling
- Platform carrying mechanics

#### Save System
- Automatic save to save.json
- Tracks deaths, unlocked categories, completed levels
- Persistent progress across sessions
- Default save initialization

#### UI System
- Main menu with category cards
- Level select with visual indicators
- Gameplay HUD with death counter and progress flags
- Victory overlay with level complete card
- Smooth transitions between scenes

---

## [Unreleased]

### Planned Features

#### Gameplay Enhancements
- [ ] Sound and music system
- [ ] Particle effects for impacts and deaths
- [ ] Visual screen shake on close calls
- [ ] Power-ups and temporary abilities
- [ ] Speed-run mode with timer
- [ ] Difficulty settings (Easy, Medium, Hard)

#### Level System
- [ ] Level editor for custom level creation
- [ ] Custom level loading and saving
- [ ] Level sharing between players
- [ ] Level difficulty rating system
- [ ] Daily challenge levels

#### Player Progression
- [ ] Achievement/Badge system
- [ ] Leaderboards (local and online)
- [ ] Skill points and unlockables
- [ ] Player statistics tracking
- [ ] Speed-run records

#### Graphics & Visual Effects
- [ ] Improved sprite animations
- [ ] Parallax scrolling backgrounds
- [ ] Visual effects for different game events
- [ ] Shader-based visual effects
- [ ] Gradient backgrounds per category
- [ ] Character customization skins

#### Accessibility
- [ ] Color-blind friendly palette options
- [ ] Difficulty accessibility features
- [ ] Keyboard remapping options
- [ ] Screen reader support
- [ ] Subtitle support for future audio

#### Platform Support
- [ ] Mobile/Android support
- [ ] Web version (WebGL/Pyodide)
- [ ] macOS native build
- [ ] Linux native build

### Under Discussion
- Multiplayer competitive mode
- Online multiplayer levels
- Streaming integration
- AI opponents
- Level procedural generation

---

## Version History

### 1.0.0 - Initial Release
- Complete game with all 5 categories
- 15 levels with varying difficulty
- Full color theming system
- Save/load functionality
- Professional UI
- Documentation

---

## Known Issues

### Current Release
- None documented

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on how to contribute to this project.

---

## Credits

- Game designed and developed as a final year university project
- Built with Python and Pygame
- Inspired by classic precision platformers

---

## License

This project is licensed under the MIT License - see [LICENSE](./LICENSE) file for details.

---

**Last Updated:** April 2, 2026

