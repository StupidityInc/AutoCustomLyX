#!/usr/bin/env python3
"""
Updated LyX Hebrew Installation Script for StupidityInc
Scrapes from: https://github.com/StupidityInc/lyx-config
"""

import os
import subprocess
import sys
import time
import urllib.request
import urllib.error
from shutil import rmtree, which
from pathlib import Path

# --- CONFIGURATION ---
CONFIG_REPO_RAW = "https://raw.githubusercontent.com/StupidityInc/lyx-config/main"

### UTILITIES ###

def is_windows() -> bool:
    return sys.platform == "win32"

def sudo():
    return "sudo " if not is_windows() else ""

def panic(message: str):
    print(f"[LyX Hebrew] {message}")
    exit(-1)

def run(command: str):
    print(f"[LyX Hebrew] Executing: {command}")
    if os.system(command) != 0:
        print(f"[LyX Hebrew] Warning: Command failed.")

def fetch_raw(remote_path):
    """Downloads a raw file from the config repo."""
    url = f"{CONFIG_REPO_RAW}/{remote_path}"
    try:
        with urllib.request.urlopen(url) as response:
            return response.read().decode('utf-8')
    except urllib.error.HTTPError:
        print(f"[LyX Hebrew] 404: Could not find {remote_path} on GitHub.")
        return None

### LYX DIRECTORY LOGIC ###

def get_lyx_user_directory():
    # Priority 1: Flatpak (Requested for Mint/Linux check)
    flatpak_path = Path.home() / ".var/app/org.lyx.LyX/config/lyx"
    if flatpak_path.exists():
        return str(flatpak_path)

    # Priority 2: Standard OS Paths
    if is_windows():
        roaming = os.environ.get("APPDATA", "")
        latest_lyx = sorted([f for f in os.listdir(roaming) if f.startswith("LyX")]) if roaming else []
        return os.path.join(roaming, latest_lyx[-1]) if latest_lyx else None
    elif sys.platform == "darwin":
        support = os.path.expanduser("~/Library/Application Support")
        latest_lyx = sorted([f for f in os.listdir(support) if f.startswith("LyX")])
        return os.path.join(support, latest_lyx[-1]) if latest_lyx else None
    else:
        return os.path.expanduser("~/.lyx")

### MAIN INSTALLER LOGIC ###

def install_lyx():
    """Installs LyX via Flatpak (Primary) or System Package (Secondary)."""
    if not is_windows() and which("flatpak"):
        print("[LyX Hebrew] Installing via Flatpak...")
        run("flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo")
        run("flatpak install --user -y flathub org.lyx.LyX")
        run("flatpak override --user --filesystem=host org.lyx.LyX")
    elif is_windows():
        run("winget install lyx.lyx")
    else:
        run(f"{sudo()}apt-get install -y lyx")

if __name__ == "__main__":
    # 1. Install LyX if missing
    lyx_user_dir = get_lyx_user_directory()
    if not lyx_user_dir or not os.path.exists(lyx_user_dir):
        print("[LyX Hebrew] LyX not detected. Attempting installation...")
        install_lyx()
        # Initialize user dir
        print("[LyX Hebrew] Initializing user directory...")
        time.sleep(2)
        lyx_user_dir = get_lyx_user_directory()
        if not os.path.exists(lyx_user_dir):
            os.makedirs(lyx_user_dir, exist_ok=True)

    print(f"[LyX Hebrew] Using Directory: {lyx_user_dir}")

    # 2. CREATE FOLDER STRUCTURE
    for subfolder in ["bind", "Macros", "templates", "layouts"]:
        path = os.path.join(lyx_user_dir, subfolder)
        if not os.path.exists(path):
            print(f"[LyX Hebrew] Creating folder: {subfolder}")
            os.makedirs(path, exist_ok=True)

    # 3. SCRAPE CONFIGURATION
    print("[LyX Hebrew] Scraping custom configurations...")
    
    # A. Preferences (Cites:)
    pref_content = fetch_raw("preferences")
    if pref_content:
        with open(os.path.join(lyx_user_dir, "preferences"), "w", encoding="utf-8") as f:
            f.write(pref_content)

    # B. Bindings (Cites:)
    bind_content = fetch_raw("bind/user.bind")
    if bind_content:
        with open(os.path.join(lyx_user_dir, "bind", "user.bind"), "w", encoding="utf-8") as f:
            f.write(bind_content)

    # C. Macros (Cites:)
    macro_content = fetch_raw("Macros/Macros_Standard.lyx")
    if macro_content:
        with open(os.path.join(lyx_user_dir, "Macros", "Macros_Standard.lyx"), "w", encoding="utf-8") as f:
            f.write(macro_content)

    # D. Templates (Cites:)
    template_content = fetch_raw("Templates/Assignments.lyx")
    if template_content:
        with open(os.path.join(lyx_user_dir, "templates", "Assignments.lyx"), "w", encoding="utf-8") as f:
            f.write(template_content)

    print("\n[LyX Hebrew] Installation Complete!")
    print("[LyX Hebrew] Files Scraped successfully from lyx-config repository.")
    print("[LyX Hebrew] Please restart LyX and run 'Tools -> Reconfigure'.")