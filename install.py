#!/usr/bin/env python3
"""
LyX Hebrew Ultimate Installer (Interactive Fix)
1. Clears terminal glitches.
2. Installs Fonts (System-wide OR User-local).
3. Installs LyX (Flatpak).
4. Configures Preferences, Macros, and Templates.
"""

import os
import sys
import shutil
import time
import subprocess
import urllib.request
from pathlib import Path
from shutil import which

# --- CONFIGURATION ---
REPO_BASE = "https://raw.githubusercontent.com/StupidityInc/lyx-config/main"
CONFIG_URLS = {
    "preferences": f"{REPO_BASE}/preferences",
    "bind/user.bind": f"{REPO_BASE}/bind/user.bind",
    "Macros/Macros_Standard.lyx": f"{REPO_BASE}/Macros/Macros_Standard.lyx",
    "templates/Assignments.lyx": f"{REPO_BASE}/templates/Assignments.lyx"
}

FONT_URL = "https://raw.githubusercontent.com/StupidityInc/lyx-config/main/fonts/DavidCLM-Medium.otf"

# --- UTILITIES ---

def is_interactive():
    """Check if we're running interactively (not piped)."""
    return sys.stdin.isatty()

def ask_user(question, default='n'):
    """Ask user a question. If piped, use default."""
    if not is_interactive():
        print(f"{question} [Auto: {default}]")
        return default
    
    try:
        choice = input(f"{question} [y/N]: ").lower()
        return choice if choice else default
    except (EOFError, KeyboardInterrupt):
        print("\nUsing default: No")
        return default

def run_interactive(cmd, desc):
    """Runs a command where the user might need to interact (e.g. Password)."""
    print(f"\n[LyX Installer] --- {desc} ---")
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError:
        print(f"⚠️  Warning: {desc} failed. (Check your internet or password)")
        return False
    return True

def run_quiet(cmd):
    """Runs a command silently to prevent noise."""
    try:
        subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

def fetch_content(url):
    try:
        with urllib.request.urlopen(url) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"❌ Error downloading {url}: {e}")
        return None

# --- STEPS ---

def step_1_init():
    os.system("reset")
    print("=== StupidityInc LyX Installer ===")
    if not is_interactive():
        print("⚙️  Running in non-interactive mode (using defaults)")

def step_2_dependencies():
    """Installs fonts and tools. Asks user for permission first."""
    print("\n[?] Do you want to try installing System Fonts (fonts-culmus)?")
    print("    (This requires your SUDO PASSWORD)")
    
    choice = ask_user("    Install System Fonts?", default='n')
    
    if choice == 'y':
        if which("apt"):
            run_interactive("sudo apt update", "Updating Apt Sources")
            run_interactive("sudo apt install -y flatpak git curl fonts-culmus fonts-lyx", "Installing Fonts & Tools")
        elif which("dnf"):
            run_interactive("sudo dnf install -y flatpak git curl culmus-fonts", "Installing Fonts & Tools")
        else:
            print("⚠️  Package manager not found. Skipping system font install.")
    else:
        print("    Skipping system fonts installation.")

def step_3_install_lyx():
    """Installs LyX via Flatpak."""
    if not which("flatpak"):
        print("\n❌ Error: Flatpak is missing. Please install Flatpak and restart.")
        sys.exit(1)

    print("\n[LyX Installer] Setting up LyX (Flatpak)...")
    run_quiet("flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo")
    
    run_interactive("flatpak install --user -y flathub org.lyx.LyX", "Installing LyX App")
    
    print("[LyX Installer] configuring Permissions (Fonts & Files)...")
    run_quiet("flatpak override --user --filesystem=host org.lyx.LyX")
    run_quiet("flatpak override --user --filesystem=/usr/share/fonts org.lyx.LyX")
    run_quiet("flatpak override --user --filesystem=~/.local/share/fonts org.lyx.LyX")

def step_4_configure():
    """Downloads and patches configs."""
    print("\n[LyX Installer] Downloading Configurations...")
    
    config_dir = Path.home() / ".var/app/org.lyx.LyX/config/lyx"
    
    if not config_dir.exists():
        print(f"[LyX Installer] Creating config directory: {config_dir}")
        config_dir.mkdir(parents=True, exist_ok=True)

    for local_path, url in CONFIG_URLS.items():
        dest = config_dir / local_path
        if not dest.parent.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
        
        content = fetch_content(url)
        if content:
            if "preferences" in local_path:
                content = content.replace('screen_font_roman "LM Sans Quot 8"', 'screen_font_roman "David CLM"')
                content = content.replace('screen_font_sans "Latin Modern Roman"', 'screen_font_sans "Simple CLM"')
                if "\\path_prefix" not in content:
                    content += '\n\\path_prefix "/usr/bin:/usr/local/bin"\n'
            
            with open(dest, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"    ✅ Installed {local_path}")
        else:
            print(f"    ⚠️  Failed to download {local_path}")

def step_5_finish():
    print("\n[LyX Installer] Finalizing...")
    run_quiet("update-desktop-database ~/.local/share/applications")
    
    print("\n" + "="*40)
    print("✅ INSTALLATION COMPLETE")
    print("="*40)
    print("1. If the 'LyX' icon is missing, Log Out and Log In.")
    print("2. Launch LyX.")
    print("3. Go to Tools > Reconfigure.")
    print("4. Restart LyX.")

if __name__ == "__main__":
    step_1_init()
    step_2_dependencies()
    step_3_install_lyx()
    step_4_configure()
    step_5_finish()