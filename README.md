# AutoCustomLyX

Automated installer for LyX with TeXLive and custom configurations.

## What It Does
1. Installs **TeXLive** (full LaTeX distribution)
2. Installs **LyX** (graphical LaTeX editor)
3. Pulls custom configs from [lyx-config](https://github.com/StupidityInc/lyx-config) and applies them
4. Configures Hebrew support (bidirectional text, fonts)

## Files
- **`install.py`** — Main installer script (cross-platform: Windows/Linux/macOS)
- **`test.py`** — Tests and validation for the installer

## Usage
```bash
python install.py
```

The script handles package manager detection, platform-specific paths, and automatic configuration.
