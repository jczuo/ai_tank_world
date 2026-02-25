# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

Python Pygame tank battle game (坦克大战). Single-process GUI application with no external services, databases, or APIs. Entry point: `python src/main.py` (must run from `/workspace`).

**Source files:**
- `src/main.py` — entry point
- `src/constants.py` — all game configuration (screen, colors, tank stats, level settings)
- `src/game.py` — main game loop, state management, collision detection
- `src/tank.py` — player tank and 4 enemy tank types (basic/fast/power/armor)
- `src/bullet.py` — bullet with damage/speed/steel-breaking properties
- `src/terrain.py` — 6 terrain types (brick, steel, water, forest, ice, base)
- `src/powerup.py` — 5 power-up types (star, shield, life, bomb, timer)
- `src/effects.py` — explosion, spawn animation, shield visual effects
- `src/level.py` — 5 level definitions with map layouts
- `src/hud.py` — sidebar HUD display
- `src/sound.py` — sound manager
- `src/brick.py` — legacy file, no longer used

### Running the game

```bash
export DISPLAY=:1 SDL_AUDIODRIVER=dummy
cd /workspace
python3 src/main.py
```

- `DISPLAY=:1` targets the Desktop pane display; use `:99` for headless Xvfb.
- `SDL_AUDIODRIVER=dummy` is required because there is no audio hardware in the cloud VM.
- Game window is 780x600 (600px game area + 180px HUD sidebar).

### Linting

```bash
flake8 src/ --max-line-length=120
```

Expected warnings: F403/F405 (star imports from `constants`) are by design. `src/brick.py` is legacy and can be excluded.

### Dependencies

- Single dependency: `pygame` (pinned to `2.1.2` in `requirements.txt`, but that version lacks Python 3.12 wheels — `pip install pygame` installs the latest compatible version which is backward-compatible).
- Linting: `flake8` (not in `requirements.txt`; installed separately).

### Gotchas

- `pygame==2.1.2` will fail to install from source on Python 3.12 due to missing SDL2 dev headers. Use `pip install pygame` (without version pin) to get a compatible wheel.
- Asset paths are relative to the working directory, so always run from `/workspace`.
- Sound files are optional — the game falls back gracefully if audio files are missing.
