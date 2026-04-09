# Version 1.1.0 Release Notes

## Rage Bait v1.1.0 - Audio & Mute System Update

**Release Date:** April 9, 2026

### 🎉 What's New

#### Complete Sound System
- Background music that loops during gameplay
- Jump sound effect for satisfying feedback
- Death sound for collision feedback
- Victory sound when reaching the flag
- All sounds can be toggled with the mute button

#### Mute Button Feature
- Easy-to-use mute button in top-right corner
- Color-coded for visual feedback:
  - Green (🔊) when sound is ON
  - Red (🔇) when sound is OFF
- One-click toggle on both main menu and level scenes
- **Persistent preference** - Your mute setting is saved!

#### Game Rebranding
- Official name change: **Splotch → Rage Bait**
- Updated all displays and documentation
- Fresh, more energetic branding

### 🔧 Technical Improvements

- New `core/sound_manager.py` module for centralized audio management
- Reliable jump detection using `player.jumped` flag
- Sound state persisted in `save.json`
- Graceful fallback when audio files are missing
- Volume-adjustable sound effects (0.0 to 1.0 scale)

### 📚 Documentation

- **SOUND_SETUP.md** - Complete audio system guide
- **MUTE_BUTTON_README.md** - Mute button implementation details
- **generate_sounds.py** - Script to create placeholder audio files
- Updated README with audio system information

### 🐛 Bug Fixes

- Fixed unreliable jump sound detection (now uses physics flag)
- Improved sound file loading with better error handling
- Fixed mute state initialization on scene transitions

### 📦 Installation & Setup

1. **Clone/Update the repository:**
```bash
git clone https://github.com/yourusername/rage-bait.git
cd rage-bait
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Generate sound files (optional):**
```bash
python create_sounds_quick.py
```

4. **Run the game:**
```bash
python main.py
```

### 🎮 New Controls

- **Click mute button** - Toggle sound on/off (top-right corner)
- Mute preference is automatically saved

### 📋 Files Changed

**New Files:**
- `core/sound_manager.py`
- `assets/sounds/` (directory)
- `assets/images/silence.png`
- `SOUND_SETUP.md`
- `MUTE_BUTTON_README.md`
- `create_sounds_quick.py`
- `generate_sounds.py`

**Modified Files:**
- `core/save_manager.py` - Added muted field
- `ui/draw_helpers.py` - Added draw_mute_button()
- `scenes/category_select.py` - Integrated mute button
- `scenes/level_scene.py` - Integrated mute button
- `engine/physics.py` - Added jumped flag
- `README.md` - Updated with audio info
- `CHANGELOG.md` - Version history

### 💾 Save File Format

New `save.json` field:
```json
{
  "deaths": 0,
  "completed": {},
  "unlocked_cats": [0, 1],
  "unlocked_lvls": {...},
  "muted": false
}
```

The `muted` field is automatically added to existing saves.

### 🎯 Known Limitations

- Audio files are not included in the repository (use sound generation scripts)
- Emoji icons used as fallback if image loading fails
- Sound system gracefully handles missing audio files

### 🚀 Performance

- Minimal performance impact from sound system
- Sound loading is done at scene initialization
- No audio processing during gameplay (pre-loaded sounds)

### 🔜 Future Enhancements

- Settings menu for volume control
- More sound effects (powerups, transitions)
- Music variations per category
- Sound effect presets
- Audio visualization

### 📝 Credits

- Sound system implementation with Pygame mixer
- Silence icon from game asset pack
- Background music generation

---

**For the complete changelog, see [CHANGELOG.md](../CHANGELOG.md)**

