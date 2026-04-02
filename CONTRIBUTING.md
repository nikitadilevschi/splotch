# Contributing to SPLOTCH

Thank you for your interest in contributing to SPLOTCH! We welcome contributions from everyone. This document provides guidelines and instructions for contributing.

## 🎯 Code of Conduct

Be respectful, inclusive, and professional. We're all here to make SPLOTCH better!

## 🚀 Getting Started

### 1. Fork the Repository
Click the "Fork" button on GitHub to create your own copy of the project.

### 2. Clone Your Fork
```bash
git clone https://github.com/YOUR-USERNAME/splotch.git
cd splotch
```

### 3. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

Use descriptive branch names:
- `feature/new-level` - For new features
- `fix/bug-description` - For bug fixes
- `docs/update-readme` - For documentation
- `refactor/module-name` - For refactoring

### 4. Install Development Dependencies
```bash
pip install -r requirements.txt
```

### 5. Make Your Changes

Follow these guidelines:

#### Code Style
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use meaningful variable and function names
- Keep functions focused and modular
- Add comments for complex logic

#### Example
```python
def calculate_collision_distance(rect1, rect2):
    """
    Calculate distance between two rectangles.
    
    Args:
        rect1: First pygame.Rect
        rect2: Second pygame.Rect
    
    Returns:
        float: Minimum distance between rectangles
    """
    # Implementation here
    pass
```

#### Commits
- Write clear, descriptive commit messages
- Use present tense: "Add feature" not "Added feature"
- Reference issues when relevant: "Fix #123"

```bash
git commit -m "Add new spike level to SPIKES category - closes #42"
```

### 6. Test Your Changes

Run the game and test your changes:
```bash
python main.py
```

Test in each category and level:
- ✅ No crashes
- ✅ Smooth gameplay
- ✅ Correct physics
- ✅ Visual polish

### 7. Push to Your Fork
```bash
git push origin feature/your-feature-name
```

### 8. Create a Pull Request

1. Go to the original repository
2. Click "New Pull Request"
3. Select your branch
4. Fill in the PR template:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Documentation
- [ ] Refactoring

## Related Issues
Closes #issue_number

## Testing
- [ ] Tested in GAPS category
- [ ] Tested in SPIKES category
- [ ] Tested in PUSH category
- [ ] Tested in PLATFORMS category
- [ ] Tested in SAWS category

## Screenshots (if applicable)
[Add screenshots here]
```

---

## 📋 Types of Contributions

### 🎮 New Features

Ideas for new features:
- New levels in existing categories
- New categories
- Additional visual effects
- UI improvements
- Quality of life enhancements

**Process:**
1. Open an issue discussing the feature
2. Wait for feedback
3. Implement in a feature branch
4. Submit PR with testing evidence

### 🐛 Bug Fixes

Found a bug? Great!

**Process:**
1. Open an issue describing the bug
2. Include steps to reproduce
3. Fix the bug in a branch
4. Add test case if possible
5. Submit PR

### 📚 Documentation

Help improve our documentation:
- Fix typos or unclear explanations
- Add examples
- Improve comments
- Create tutorials

### ⚡ Performance

Help us optimize the game:
- Profile code for bottlenecks
- Suggest optimizations
- Test on different systems
- Report performance issues

---

## 🎨 Adding New Levels

### Create a New Level

1. **Define in level file** (e.g., `levels/gaps.py`):
```python
GAPS_L1 = {
    'tiles': [
        # 27x15 grid (405 elements)
        # 1 = platform, 0 = empty
        1,1,1,...
    ],
    'player': [160, 320],      # Starting position
    'goal': [672, 320],        # Flag position
    'traps': [
        # Moving platforms, spikes, saws
        dict(kind='mblock', x=544, y=320, w=96, h=160,
             sensor=(560, 192, 32, 128),
             steps=[dict(ty=6, t=0.3)], loop=False, auto=False),
    ],
    'hint': "Jump before the platform falls!",
}
```

2. **Add to level list** in `levels/__init__.py`:
```python
LEVELS = [
    [GAPS_L1, GAPS_L2, GAPS_L3],
    [SPIKES_L1, SPIKES_L2, SPIKES_L3],
    # ...
]
```

3. **Test thoroughly:**
   - Level is beatable
   - Difficulty is appropriate
   - No physics glitches
   - Colors match category theme

---

## 🎨 Adding New Categories

A category needs:
1. Color palette in `core/constants.py`
2. 3 levels in a new module (e.g., `levels/new_category.py`)
3. Category icon in `ui/draw_helpers.py`
4. Name in `CAT_NAMES`
5. Category select scene integration

---

## 💬 Communication

- **Issues:** For bugs and feature requests
- **Discussions:** For questions and ideas
- **Pull Requests:** For code contributions
- **Email:** For direct contact

---

## ✅ Checklist Before Submitting PR

- [ ] Code follows PEP 8
- [ ] Tested in game
- [ ] No console errors
- [ ] Descriptive commit messages
- [ ] PR description is clear
- [ ] Related issues referenced
- [ ] Documentation updated if needed

---

## 🎓 Learning Resources

- [Python Style Guide (PEP 8)](https://www.python.org/dev/peps/pep-0008/)
- [Pygame Documentation](https://www.pygame.org/docs/)
- [Git Guide](https://git-scm.com/book/en/v2)
- [GitHub Flow](https://guides.github.com/introduction/flow/)

---

## 🙏 Thank You!

Every contribution helps make SPLOTCH better. Whether it's code, bug reports, documentation, or ideas - we appreciate it all!

Happy coding! 🎮

