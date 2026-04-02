# Color Palette Reference - RGB Values

## Gaps Category (Teal Theme)
```
Primary:    (70, 180, 168)   - Main background color
Dark:       (45, 130, 120)   - Platforms and tiles
Light:      (100, 210, 200)  - Accents
Accent:     (120, 230, 220)  - UI highlights (top bar)
Spike:      (160, 160, 160)  - Spike hazards (neutral grey)
```

## Spikes Category (Red Theme)
```
Primary:    (185, 75, 75)    - Main background color
Dark:       (140, 50, 50)    - Platforms and tiles
Light:      (220, 100, 100)  - Accents
Accent:     (240, 130, 130)  - UI highlights (top bar)
Spike:      (200, 100, 100)  - Spike hazards (red-tinted)
```

## Push Category (Blue Theme)
```
Primary:    (75, 130, 185)   - Main background color
Dark:       (50, 95, 140)    - Platforms and tiles
Light:      (110, 160, 210)  - Accents
Accent:     (140, 180, 230)  - UI highlights (top bar)
Spike:      (160, 160, 160)  - Spike hazards (neutral grey)
```

## Platforms Category (Purple Theme)
```
Primary:    (125, 75, 185)   - Main background color
Dark:       (90, 50, 140)    - Platforms and tiles
Light:      (160, 110, 220)  - Accents
Accent:     (190, 140, 240)  - UI highlights (top bar)
Spike:      (160, 160, 160)  - Spike hazards (neutral grey)
```

## Saws Category (Orange/Gold Theme)
```
Primary:    (185, 145, 50)   - Main background color
Dark:       (140, 110, 30)   - Platforms and tiles
Light:      (220, 175, 80)   - Accents
Accent:     (240, 200, 110)  - UI highlights (top bar)
Spike:      (160, 160, 160)  - Spike hazards (neutral grey)
```

## How to Customize

Edit the `CAT_PALETTES` list in `core/constants.py`:

```python
CAT_PALETTES = [
    # Category 0: Gaps
    {
        'primary':    (R, G, B),
        'dark':       (R, G, B),
        'light':      (R, G, B),
        'accent':     (R, G, B),
        'spike':      (R, G, B),
    },
    # ... repeat for other categories
]
```

Each color is a tuple of (Red, Green, Blue) values from 0-255.

