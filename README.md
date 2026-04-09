# 🎮 RAGE BAIT - Precision Platformer Game

<div align="center">

![Python](https://img.shields.io/badge/Python-3.13-blue?style=flat-square&logo=python)
![Pygame](https://img.shields.io/badge/Pygame-2.0+-green?style=flat-square&logo=pygame)
![License](https://img.shields.io/badge/License-MIT-red?style=flat-square)
![Status](https://img.shields.io/badge/Status-Complete-success?style=flat-square)
![Version](https://img.shields.io/badge/Version-1.1.0-blueviolet?style=flat-square)

A challenging precision platformer game with 5 unique categories and 15 levels of increasing difficulty.

[🎮 Play](#features) • [📖 Docs](#documentation) • [🚀 Installation](#installation) • [🤝 Contributing](#contributing)

</div>

---

## 🎯 Overview

**RAGE BAIT** is a precision platformer game where players must navigate through deadly traps, falling platforms, and rotating saws. Each of the 5 categories presents unique challenges with their own visual theme and mechanics.

### ✨ Key Features

- 🎨 **5 Unique Categories** with distinct visual themes and color palettes
  - 🌊 **GAPS** - Platforms that collapse when you jump on them
  - 🔴 **SPIKES** - Hidden guillotines that pop up when you approach
  - 💨 **PUSH** - Mobile blocks that push you across gaps
  - 📦 **PLATFORMS** - Vertical platforms that crush you if you get caught
  - 🔪 **SAWS** - Rotating blades that move along platforms

- 🎮 **15 Challenging Levels** - 3 levels per category with progressive difficulty
- 🎨 **Dynamic Color System** - Each category has its own cohesive visual theme
- 💾 **Persistent Save System** - Your progress is automatically saved
- 🏆 **Achievement Tracking** - Death counter and level completion badges
- 🎯 **Responsive Controls** - Smooth, precise platforming mechanics
- 🎭 **Polished UI** - Beautiful menus and visual feedback
- 🔊 **Sound System** - Background music, jump, death, and victory sounds
- 🔇 **Mute Button** - Easy toggle to mute/unmute all sounds (persistent preference)

---

## 📸 Screenshots

```
Main Menu              Level Select           Gameplay
[Teal Theme]          [Category Colors]       [Dynamic Colors]
5 Categories          3 Levels Each           Real-time Physics
```

---

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Quick Start

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/rage-bait.git
cd rage-bait
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the game:**
```bash
python main.py
```

---

## 🔊 Audio & Sound System

Rage Bait includes a complete sound system with background music and sound effects:

- **Background Music** - Loops continuously on main menu and during gameplay
- **Jump Sound** - Plays when you jump (satisfying ascending tone)
- **Death Sound** - Plays when you die (ominous descending tone)
- **Victory Sound** - Plays when you reach the flag (uplifting chord)
- **Mute Button** - Toggle mute with one click (green 🔊 / red 🔇)

### Sound Setup

Audio files are located in `assets/sounds/`:

```
assets/sounds/
├── jump.wav              # Jump sound effect
├── death.wav             # Death sound effect
├── win.wav               # Victory sound effect
└── background_music.wav  # Looping background music
```

To generate placeholder audio files, run:
```bash
python create_sounds_quick.py
```

For more details, see [SOUND_SETUP.md](./SOUND_SETUP.md)

---

## 🎮 How to Play

### Controls

| Key | Action |
|-----|--------|
| **A / ←** | Move Left |
| **D / →** | Move Right |
| **SPACE / ↑** | Jump |
| **ESC** | Back/Menu |
| **CTRL+R** | Reset Save (Confirm twice) |

### Objective

Navigate through each level by:
1. Jumping over falling platforms
2. Avoiding deadly spikes and saws
3. Using moving platforms strategically
4. Reaching the flag at the end

### Tips

- ⚡ **Timing is everything** - Jump before platforms collapse
- 🎯 **Plan your path** - Look ahead for obstacles
- 📊 **Use the side platforms** - They often provide safe passage
- 🔄 **Learn the patterns** - Each trap has a rhythm you can exploit

---

## 🎨 Design Philosophy

### Color Palette System

Each category features a carefully designed color palette that applies to all visual elements:

**GAPS (Teal)**
- Primary: `(70, 180, 168)` - Calm, aquatic vibes
- Dark: `(45, 130, 120)` - Platform color
- Accent: `(120, 230, 220)` - UI highlights

**SPIKES (Red)**
- Primary: `(185, 75, 75)` - Aggressive, warning
- Dark: `(140, 50, 50)` - Platform color
- Accent: `(240, 130, 130)` - Danger highlights

**PUSH (Blue)**
- Primary: `(75, 130, 185)` - Professional, stable
- Dark: `(50, 95, 140)` - Platform color
- Accent: `(140, 180, 230)` - Cool highlights

**PLATFORMS (Purple)**
- Primary: `(125, 75, 185)` - Creative, mysterious
- Dark: `(90, 50, 140)` - Platform color
- Accent: `(190, 140, 240)` - Magical highlights

**SAWS (Orange)**
- Primary: `(185, 145, 50)` - Energetic, intense
- Dark: `(140, 110, 30)` - Platform color
- Accent: `(240, 200, 110)` - Bright highlights

---

## 📁 Project Structure

```
splotch/
├── core/                          # Core functionality
│   ├── constants.py              # Colors, dimensions, palettes
│   ├── save_manager.py           # Save/load system
│   ├── sound_manager.py          # Audio system
│   └── __init__.py
├── engine/                        # Game engine
│   ├── physics.py                # Player physics & collision
│   ├── mblock.py                 # Moving blocks
│   ├── spike.py                  # Spike hazards
│   ├── sensor.py                 # Activation sensors
│   ├── tl_runner.py              # Timeline animations
│   └── __init__.py
├── levels/                        # Level definitions
│   ├── builder.py                # Level builder utilities
│   ├── gaps.py                   # GAPS category levels
│   ├── spikes.py                 # SPIKES category levels
│   ├── push.py                   # PUSH category levels
│   ├── platforms.py              # PLATFORMS category levels
│   ├── saws.py                   # SAWS category levels
│   └── __init__.py
├── scenes/                        # Game scenes
│   ├── category_select.py        # Main menu
│   ├── level_select.py           # Level selection
│   ├── level_scene.py            # Gameplay scene
│   └── __init__.py
├── ui/                            # User interface
│   ├── draw_helpers.py           # Rendering functions
│   ├── hud.py                    # HUD elements
│   └── __init__.py
├── assets/                        # Game assets
│   ├── images/
│   │   └── silence.png           # Mute button icon
│   └── sounds/
│       ├── jump.wav              # Jump sound effect
│       ├── death.wav             # Death sound effect
│       ├── win.wav               # Victory sound effect
│       └── background_music.wav  # Looping background music
├── main.py                        # Entry point
├── splotch.py                     # Main game class (legacy)
├── requirements.txt               # Dependencies
└── README.md                      # This file
```

---

## 🔧 Technical Details

### Architecture

The game uses a **scene-based architecture** with multiple game states:
- **CategorySelectScene** - Choose game category
- **LevelSelectScene** - Choose level within category
- **LevelScene** - Active gameplay

### Physics System

- Gravity-based movement with collision detection
- Platform carrying (player moves with moving platforms)
- Crush detection (death when trapped between objects)
- Precise hit detection for hazards

### Save System

Progress is automatically saved to `save.json`:
```json
{
    "deaths": 41,
    "unlocked_cats": [0, 1, 2, 3, 4],
    "unlocked_lvls": {"0": [0, 1, 2], "1": [0, 1, 2]},
    "completed": {"0_0": true, "0_1": true}
}
```

---

## 📚 Documentation

- 📖 [Technical Documentation](./DOCUMENTATIE_FINALA_PROIECT.md) (Romanian)
- 🎨 [Color Palette System](./COLOR_PALETTE_SYSTEM.md)
- 📋 [System Architecture](./SYSTEM_ARCHITECTURE.md)
- 🔧 [Implementation Guide](./COLOR_PALETTE_SYSTEM.md)

---

## 🎓 University Project

This project was developed as a final year (licență) project for Computer Science studies, demonstrating:
- Software architecture and design patterns
- Game development concepts
- Physics and collision detection
- User interface design
- State management and persistence

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add comments for complex logic
- Test your changes thoroughly
- Update documentation as needed

---

## 🐛 Bug Reports

Found a bug? Please report it by creating an [Issue](../../issues). Include:
- Description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable

---

## 📝 License

This project is licensed under the **MIT License** - see [LICENSE](./LICENSE) file for details.

---

## 🔜 Roadmap

### Completed Features ✅

- [x] Sound and music system
- [x] Mute button with persistent state

### Future Enhancements

- [ ] Particle effects
- [ ] Level editor
- [ ] Online leaderboards
- [ ] Color-blind friendly palettes
- [ ] Mobile platform support
- [ ] Custom level creation
- [ ] Achievement system
- [ ] Difficulty settings
- [ ] Speed-run mode

---

## 📧 Contact & Support

- 📧 **Email:** dilevschinikita75@gmail.com
  


---

## 🙏 Acknowledgments

- **Pygame** - For the excellent game development library
- **Python Community** - For the amazing language and tools
- **Inspiration** - From classic platformer games

---

<div align="center">

### Made with ❤️ in Python

⭐ **If you enjoy Rage Bait, please consider giving it a star!** ⭐

[Back to Top](#-rage-bait---precision-platformer-game)

</div>

