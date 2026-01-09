#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

# --- CONFIGURATION ---
# The base URL for the RAW files in your repo
REPO_BASE_URL = "https://raw.githubusercontent.com/StupidityInc/AutoCustomLyX/master"

# Files to scrape: "Remote Path" : "Local Relative Path"
FILES_TO_FETCH = {
    "preferences": "preferences",
    "bind/user.bind": "bind/user.bind",
    "macros/arazim_macros.lyx": "macros/arazim_macros.lyx"
}

FLATPAK_ID = "org.lyx.LyX"
FLATPAK_CONFIG_DIR = Path.home() / f".var/app/{FLATPAK_ID}/config/lyx"

def run_cmd(cmd):
    """Run shell command with sudo support."""
    print(f"Executing: {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def download_file(url, dest_path):
    """Scrapes a file from URL and saves it locally."""
    print(f"⬇️ Scraping: {url}")
    try:
        # Ensure parent folder exists (e.g., 'bind' or 'macros')
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, dest_path)
    except Exception as e:
        print(f"❌ Failed to download {url}\nError: {e}")

def main():
    print("--- 🚀 Starting Non-Git LyX Installer ---")

    # 1. Install System Dependencies (Flatpak only, no Git needed)
    if not shutil.which("flatpak"):
        print("📦 Flatpak missing. Installing...")
        run_cmd("sudo apt update && sudo apt install -y flatpak")

    # 2. Install LyX Flatpak
    print("📦 Installing LyX...")
    run_cmd("flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo")
    run_cmd(f"flatpak install --user -y flathub {FLATPAK_ID}")
    
    # 3. Unlock Permissions (Fonts & Files)
    print("🔓 Unlocking permissions...")
    run_cmd(f"flatpak override --user --filesystem=host {FLATPAK_ID}")
    font_paths = [Path.home() / ".fonts", Path.home() / ".local/share/fonts", Path("/usr/share/fonts")]
    for fp in font_paths:
        if fp.exists():
            run_cmd(f"flatpak override --user --filesystem={fp} {FLATPAK_ID}")

    # 4. Scrape & Save Config Files
    print("\n--- 📥 Scraping Configuration ---")
    
    # Create the main config dir if it doesn't exist
    FLATPAK_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    for remote_file, local_rel_path in FILES_TO_FETCH.items():
        full_url = f"{REPO_BASE_URL}/{remote_file}"
        local_dest = FLATPAK_CONFIG_DIR / local_rel_path
        
        # Download the file
        download_file(full_url, local_dest)

    print("\n✅ Installation Complete.")
    print(f"Config saved to: {FLATPAK_CONFIG_DIR}")
    print("Run LyX with: flatpak run org.lyx.LyX")

if __name__ == "__main__":
    main()