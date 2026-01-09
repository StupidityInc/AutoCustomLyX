#!/usr/bin/env python3
import os
import shutil
import subprocess
import urllib.request
from pathlib import Path

# --- CONFIGURATION ---
# We scrape the "Raw" files directly. 
# based on your uploads, I'm assuming 'main' branch and the capitalization below.
REPO_BASE_URL = "https://raw.githubusercontent.com/StupidityInc/lyx-config/main"

# Map Remote (GitHub) paths -> Local (LyX Config) paths
# NOTE: I mapped your 'Templates' to 'templates' (lowercase) so LyX detects it automatically.
FILES_TO_FETCH = {
    "preferences": "preferences",
    "bind/user.bind": "bind/user.bind",
    "Macros/Macros_Standard.lyx": "Macros/Macros_Standard.lyx", 
    "Templates/Assignments.lyx": "templates/Assignments.lyx" 
}

FLATPAK_ID = "org.lyx.LyX"
# Flatpak config location on the host
FLATPAK_CONFIG_DIR = Path.home() / f".var/app/{FLATPAK_ID}/config/lyx"

def run_cmd(cmd):
    """Runs a shell command (using shell=True for sudo prompts if needed)."""
    print(f"Executing: {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def ensure_flatpak():
    """Installs Flatpak if missing (Mint/Debian/Ubuntu)."""
    if shutil.which("flatpak") is None:
        print("📦 Flatpak not found. Installing...")
        run_cmd("sudo apt update && sudo apt install -y flatpak")

def install_lyx():
    """Installs LyX Flatpak and sets permissions."""
    print(f"--- 📦 Setting up {FLATPAK_ID} ---")
    
    # 1. Add Flathub
    run_cmd("flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo")
    
    # 2. Install LyX (Update if exists)
    run_cmd(f"flatpak install --user -y flathub {FLATPAK_ID}")

    # 3. Unlock Permissions (Crucial for Hebrew fonts & Git usage later)
    print("🔓 Unlocking filesystem...")
    run_cmd(f"flatpak override --user --filesystem=host {FLATPAK_ID}")
    
    # 4. Expose Fonts
    font_paths = [
        Path.home() / ".fonts", 
        Path.home() / ".local/share/fonts", 
        Path("/usr/share/fonts"),
        Path("/usr/local/share/fonts")
    ]
    for fp in font_paths:
        if fp.exists():
            run_cmd(f"flatpak override --user --filesystem={fp} {FLATPAK_ID}")

def scrape_config():
    """Downloads config files directly from GitHub (No Git required)."""
    print("\n--- 📥 Scraping Configuration ---")
    
    if not FLATPAK_CONFIG_DIR.exists():
        FLATPAK_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    for remote_path, local_rel_path in FILES_TO_FETCH.items():
        url = f"{REPO_BASE_URL}/{remote_path}"
        dest = FLATPAK_CONFIG_DIR / local_rel_path
        
        print(f"⬇️  Fetching: {remote_path} -> {local_rel_path}")
        
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(url, dest)
        except Exception as e:
            print(f"❌ Error downloading {remote_path}: {e}")
            print("   (Check if the file exists in your repo's 'main' branch)")

def main():
    print("🚀 Starting StupidityInc LyX Installer (No-Git Version)...")
    
    try:
        ensure_flatpak()
        install_lyx()
        scrape_config()
        
        print("\n✅ Installation Complete!")
        print(f"   Config saved to: {FLATPAK_CONFIG_DIR}")
        print("   Run with: flatpak run org.lyx.LyX")
        print("   (Don't forget to 'Tools > Reconfigure' inside LyX first!)")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Installation Failed during command execution.\n{e}")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()