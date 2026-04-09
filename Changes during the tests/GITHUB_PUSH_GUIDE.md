# GitHub Setup and Push Guide

## Before Pushing to GitHub

### 1. Verify All Changes

Make sure all files are updated:

```bash
git status
```

Expected modified/new files:
- ✅ `README.md` - Updated with audio system info
- ✅ `CHANGELOG.md` - Version 1.1.0 entry
- ✅ `core/sound_manager.py` - NEW
- ✅ `core/save_manager.py` - Updated
- ✅ `ui/draw_helpers.py` - Updated
- ✅ `scenes/category_select.py` - Updated
- ✅ `scenes/level_scene.py` - Updated
- ✅ `engine/physics.py` - Updated
- ✅ `SOUND_SETUP.md` - NEW
- ✅ `MUTE_BUTTON_README.md` - NEW
- ✅ `create_sounds_quick.py` - NEW
- ✅ `generate_sounds.py` - NEW
- ✅ `RELEASE_NOTES_v1.1.0.md` - NEW
- ✅ `.gitignore` - Updated
- ✅ `requirements.txt` - Check if unchanged

### 2. Verify Git Configuration

```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### 3. Create a Feature Branch (Recommended)

```bash
git checkout -b feature/audio-system-and-mute
```

Or directly on main (if appropriate):

```bash
git checkout main
git pull origin main
```

## Pushing to GitHub

### Step 1: Stage All Changes

```bash
git add .
```

Or stage specific files:

```bash
git add README.md CHANGELOG.md core/sound_manager.py
git add scenes/category_select.py scenes/level_scene.py
git add engine/physics.py ui/draw_helpers.py
git add SOUND_SETUP.md MUTE_BUTTON_README.md
git add create_sounds_quick.py generate_sounds.py
git add RELEASE_NOTES_v1.1.0.md .gitignore
```

### Step 2: Create Commit

```bash
git commit -m "feat: Add audio system with background music, sound effects, and mute button

- Implement complete sound system with Pygame mixer
- Add background music (loops) and sound effects (jump, death, win)
- Add persistent mute button with toggle functionality
- Create sound_manager.py module for centralized audio control
- Update save system to persist mute state
- Rebrand game from 'Splotch' to 'Rage Bait'
- Improve jump detection using player.jumped flag
- Add comprehensive audio documentation
- Include sound file generation scripts

Fixes: More reliable jump sound detection
Related: Audio system implementation #<issue-number>"
```

Or use a simpler message:

```bash
git commit -m "feat: Add audio system and mute button (v1.1.0)"
```

### Step 3: Push to Remote

```bash
# If using feature branch:
git push -u origin feature/audio-system-and-mute

# If pushing to main:
git push origin main
```

### Step 4: Create Pull Request (if on feature branch)

Go to GitHub.com and create a PR with:
- **Title:** Add audio system with background music and mute button
- **Description:** See RELEASE_NOTES_v1.1.0.md

## Release on GitHub

### Create a Release Tag

```bash
git tag -a v1.1.0 -m "Rage Bait v1.1.0 - Audio System Release"
git push origin v1.1.0
```

Then on GitHub.com:
1. Go to **Releases**
2. Click **Draft a new release**
3. Select tag `v1.1.0`
4. Fill in release notes (copy from RELEASE_NOTES_v1.1.0.md)
5. Publish release

## Post-Push Checklist

- [ ] All commits pushed successfully
- [ ] GitHub Actions (if configured) passes
- [ ] Release is published with correct tag
- [ ] Release notes are visible on GitHub
- [ ] Documentation is readable on GitHub
- [ ] README displays correctly on GitHub homepage
- [ ] Contributors are credited

## Important Notes

### Audio Files
Audio files (`.wav`) are generated locally using:
```bash
python create_sounds_quick.py
```

They are **NOT** committed to Git (see `.gitignore`). Users generate them when they first run the game.

### Save Files
The `save.json` file is also in `.gitignore`. Each user has their own save file.

### GitHub-Specific Files to Consider Adding

If you want GitHub-specific features, create:

**`.github/workflows/python-app.yml`** - CI/CD workflow
**`.github/ISSUE_TEMPLATE/bug_report.md`** - Bug report template
**`.github/ISSUE_TEMPLATE/feature_request.md`** - Feature request template
**`.github/pull_request_template.md`** - PR template

## Troubleshooting

### Changes not showing in git status?
```bash
git add -A
git status
```

### Need to undo last commit?
```bash
git reset --soft HEAD~1
git status
```

### Need to change commit message?
```bash
git commit --amend -m "new message"
```

### Merge conflict?
```bash
# Resolve conflicts in files, then:
git add .
git commit -m "Resolve merge conflicts"
git push origin main
```

## References

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/)
- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)

