"""
Sound manager for Rage Bait.
Handles background music, sound effects for jumping, dying, etc.
"""

import pygame
import os

class SoundManager:
    """Centralized sound effect and music management."""
    
    def __init__(self):
        """Initialize pygame mixer state and preload known sound assets."""
        pygame.mixer.init()
        self.sounds = {}
        self.music = None
        self.music_playing = False
        self.muted = False  # Global mute state
        self._load_sounds()
    
    def _load_sounds(self):
        """Load all sound files. Files are in 'assets/sounds/' directory."""
        sounds_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'sounds')
        
        # Create assets/sounds directory if it doesn't exist
        if not os.path.exists(sounds_dir):
            os.makedirs(sounds_dir, exist_ok=True)
        
        # Dictionary of sound names to file paths
        sound_files = {
            'jump': 'jump.wav',
            'death': 'death.wav',
            'win': 'win.wav',
            'background': 'background_music.wav'
        }
        
        for name, filename in sound_files.items():
            filepath = os.path.join(sounds_dir, filename)
            try:
                if name == 'background':
                    # Background music loaded separately
                    self.music = pygame.mixer.Sound(filepath)
                else:
                    self.sounds[name] = pygame.mixer.Sound(filepath)
            except (pygame.error, FileNotFoundError):
                # If sound file doesn't exist, create a silent placeholder
                # This allows the game to run without audio files
                self.sounds[name] = None
                if name == 'background':
                    self.music = None
    
    def play_sound(self, sound_name, volume=1.0):
        """Play a sound effect by name."""
        if self.muted:
            return
        if sound_name in self.sounds and self.sounds[sound_name] is not None:
            self.sounds[sound_name].set_volume(volume)
            self.sounds[sound_name].play()
    
    def play_background_music(self, loops=-1, volume=0.3):
        """Play background music on loop."""
        if self.muted or self.music is None or self.music_playing:
            return
        self.music.set_volume(volume)
        self.music.play(loops)
        self.music_playing = True
    
    def stop_background_music(self):
        """Stop background music."""
        if self.music is not None:
            self.music.stop()
            self.music_playing = False
    
    def set_music_volume(self, volume):
        """Set background music volume (0.0 to 1.0)."""
        if self.music is not None:
            self.music.set_volume(max(0.0, min(1.0, volume)))
    
    def toggle_mute(self):
        """Toggle mute state for all sounds."""
        self.muted = not self.muted
        if self.muted:
            self.stop_background_music()
        elif self.music is not None:
            # Restart music when unmuting
            self.music_playing = False
            self.play_background_music()
        return self.muted
    
    def set_muted(self, muted):
        """Apply mute state directly, restarting music when unmuting."""
        if muted and not self.muted:
            self.muted = True
            self.stop_background_music()
        elif not muted and self.muted:
            self.muted = False
            if self.music is not None:
                self.music_playing = False
                self.play_background_music()


# Global sound manager instance
_sound_manager = None

def get_sound_manager():
    """Get or create the global sound manager instance."""
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundManager()
    return _sound_manager

