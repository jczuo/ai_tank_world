# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

Python Pygame tank battle game (坦克大战). Single-process GUI application with no external services, databases, or APIs. Entry point: `python src/main.py` (must run from `/workspace`).

### Running the game

```bash
export DISPLAY=:1 SDL_AUDIODRIVER=dummy
cd /workspace
python3 src/main.py
```

- `DISPLAY=:1` targets the Desktop pane display; use `:99` for headless Xvfb.
- `SDL_AUDIODRIVER=dummy` is required because there is no audio hardware in the cloud VM.

### Linting

```bash
flake8 src/ --max-line-length=120
```

Pre-existing warnings (star imports from `constants`, whitespace) are expected and should not be treated as regressions.

### Dependencies

- Single dependency: `pygame` (pinned to `2.1.2` in `requirements.txt`, but that version lacks Python 3.12 wheels — `pip install pygame` installs the latest compatible version which is backward-compatible).
- Linting: `flake8` (not in `requirements.txt`; installed separately).

### Gotchas

- `pygame==2.1.2` will fail to install from source on Python 3.12 due to missing SDL2 dev headers. Use `pip install pygame` (without version pin) to get a compatible wheel.
- The game window is 600x600 pixels. Asset paths are relative to the working directory, so always run from `/workspace`.
- Sound files are optional — the game falls back gracefully if audio files are missing.
